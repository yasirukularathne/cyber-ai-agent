import os
import json
from app.utils.logger import get_logger

logger = get_logger('llm')

class LLMExplainerLayer:
    """
    Layer 8: LLM-based human-readable threat explanation.
    Uses Groq (free Llama 3) by default, falls back to OpenAI.
    Only processes top 5 threats per run to control cost.
    Bypasses API calls if placeholders are used.
    """
    def __init__(self):
        # Force Groq-only usage per request
        self.use_groq = True
        api_key = os.getenv('GROQ_API_KEY')

        if not api_key or 'your_' in api_key or api_key == '':
            logger.info('LLM: No valid GROQ_API_KEY found. Using mock mode.')
            self.mock_mode = True
            self.client = None
            self.model_name = 'mock'
        else:
            self.mock_mode = False
            from groq import Groq
            self.client = Groq(api_key=api_key)
            # Use a supported, smaller-context model by default
            self.model_name = os.getenv('GROQ_MODEL', 'llama3-8b-2048')
            logger.info(f'LLM: Using Groq model {self.model_name}')

    def run(self, mcp_output: dict) -> dict:
        try:
            threats = mcp_output['enriched_threats'][:5]
            logger.info(f'LLM explaining {len(threats)} threats')
            explanations = []

            for threat in threats:
                explanation = self._explain(threat)
                explanations.append({**threat, 'llm_report': explanation})

            return {
                'status': 'OK',
                'layer': 'llm',
                'explained_threats': explanations,
                'count': len(explanations)
            }
        except Exception as e:
            logger.error(f'LLM failed: {e}')
            return {'status': 'ERROR', 'layer': 'llm', 'error': str(e)}

    def _explain(self, threat: dict) -> dict:
        if self.mock_mode:
            # Generate a realistic mock explanation
            agreement = "Agreed" if threat['xgb_prediction'] == threat['bert_prediction'] else "Disagreed"
            return {
                "explanation": f"Simulated analysis of network flow from {threat['ip']}. The activity indicates a potential {threat['attack_type']} attack pattern.",
                "why_dangerous": f"This threat type ({threat['attack_type']}) targeting port {threat['xgb_prediction']} poses a risk of system intrusion or downtime.",
                "mitigation": "1. Block source IP on firewall.\n2. Enable security scanning on affected hosts.\n3. Audit authentication logs.",
                "severity": threat.get('severity', 'HIGH'),
                "model_agreement": f"XGBoost and BERT {agreement.lower()} on this classification."
            }

        prompt = f"""You are a senior cybersecurity analyst. Analyze this security event and respond ONLY with a valid JSON object.

Security Event:
- Source IP: {threat['ip']}
- Attack Type: {threat['attack_type']}
- Detection Confidence: {threat['confidence_pct']}%
- Anomaly Score: {threat['anomaly_score']}
- Autoencoder Flagged: {threat['ae_flagged']}
- IP Reputation: {threat['ip_reputation']['reason']}
- Related CVEs: {[c['id'] for c in threat['related_cves']]}
- XGBoost Predicted: {threat['xgb_prediction']}
- BERT Predicted: {threat['bert_prediction']}
- Current Severity: {threat['severity']}

Respond with exactly this JSON:
{{
  "explanation": "Plain English description of what happened",
  "why_dangerous": "Specific organizational risk",
  "mitigation": "3 numbered concrete actions to take now",
  "severity": "LOW or MEDIUM or HIGH or CRITICAL",
  "model_agreement": "Whether XGBoost and BERT agreed and what that implies"
}}"""

        # Try once, and if model decommission occurs, retry with a fallback Groq model
        tried_fallback = False
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {'role': 'system', 'content': 'You are a cybersecurity expert. Respond only with valid JSON. No markdown.'},
                        {'role': 'user',   'content': prompt}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )
                raw = response.choices[0].message.content.strip()
                try:
                    if not raw:
                        raise json.JSONDecodeError('Empty response', raw, 0)
                    return json.loads(raw)
                except json.JSONDecodeError:
                    # Attempt to recover JSON substring
                    logger.warning('LLM returned non-JSON or empty response. Attempting recovery...')
                    start = raw.find('{')
                    end = raw.rfind('}')
                    if start != -1 and end != -1 and end > start:
                        try:
                            return json.loads(raw[start:end+1])
                        except Exception:
                            logger.exception('Failed to recover JSON from LLM response')
                    return {
                        'explanation': 'LLM response could not be parsed.',
                        'why_dangerous': 'Manual review required.',
                        'mitigation': '1. Isolate host. 2. Review logs. 3. Escalate to SOC.',
                        'severity': threat.get('severity', 'HIGH'),
                        'model_agreement': 'Unknown'
                    }
            except Exception as e:
                msg = str(e)
                logger.error(f'LLM API call failed (attempt {attempt+1}): {msg}')
                # If Groq model decommissioned, try a smaller-context fallback once
                if not tried_fallback and ('decommission' in msg.lower() or 'model_decommissioned' in msg.lower()):
                    old = self.model_name
                    fallback = 'llama3-8b' if '2048' in old or '8192' in old else 'llama3-8b-2048'
                    logger.info(f'LLM: model {old} decommissioned. Retrying with fallback {fallback}.')
                    self.model_name = fallback
                    tried_fallback = True
                    continue
                return {
                    'explanation': f'LLM unavailable: {msg}',
                    'why_dangerous': 'See raw detection output.',
                    'mitigation': '1. Block IP. 2. Review logs manually. 3. Alert SOC team.',
                    'severity': threat.get('severity', 'HIGH'),
                    'model_agreement': 'N/A'
                }
        return {
            'explanation': 'LLM unavailable after retries.',
            'why_dangerous': 'Manual review required.',
            'mitigation': '1. Isolate host. 2. Review logs. 3. Escalate to SOC.',
            'severity': threat.get('severity', 'HIGH'),
            'model_agreement': 'Unknown'
        }
        
