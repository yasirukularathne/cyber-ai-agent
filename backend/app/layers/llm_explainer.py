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
        self.use_groq = os.getenv('USE_GROQ', 'true').lower() == 'true'
        api_key = os.getenv('GROQ_API_KEY') if self.use_groq else os.getenv('OPENAI_API_KEY')
        
        if not api_key or 'your_' in api_key or api_key == '':
            logger.info('LLM: No valid API key found. Using mock mode.')
            self.mock_mode = True
            self.client = None
            self.model_name = 'mock'
        else:
            self.mock_mode = False
            if self.use_groq:
                from groq import Groq
                self.client = Groq(api_key=api_key)
                self.model_name = 'llama3-8b-8192'
                logger.info('LLM: Using Groq Llama3')
            else:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.model_name = 'gpt-3.5-turbo'
                logger.info('LLM: Using OpenAI GPT-3.5')

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
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                'explanation': 'LLM response could not be parsed.',
                'why_dangerous': 'Manual review required.',
                'mitigation': '1. Isolate host. 2. Review logs. 3. Escalate to SOC.',
                'severity': threat.get('severity', 'HIGH'),
                'model_agreement': 'Unknown'
            }
        except Exception as e:
            logger.error(f'LLM API call failed: {e}')
            return {
                'explanation': f'LLM unavailable: {str(e)}',
                'why_dangerous': 'See raw detection output.',
                'mitigation': '1. Block IP. 2. Review logs manually. 3. Alert SOC team.',
                'severity': threat.get('severity', 'HIGH'),
                'model_agreement': 'N/A'
            }
        
