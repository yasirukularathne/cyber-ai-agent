import os
import json
import re

from app.utils.logger import get_logger

logger = get_logger('llm')

DEFAULT_GROQ_MODEL = 'openai/gpt-oss-120b'
FALLBACK_GROQ_MODELS = [
    'openai/gpt-oss-20b',
    'qwen/qwen3.6-27b'
]


def _sanitize_llm_json(raw: str) -> str:
    """
    Fix common LLM JSON mistakes before parsing.
    """

    raw = raw.strip()

    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'\s*```$', '', raw)

    raw = re.sub(r'\bTrue\b', 'true', raw)
    raw = re.sub(r'\bFalse\b', 'false', raw)
    raw = re.sub(r'\bNone\b', 'null', raw)

    return raw.strip()


class LLMExplainerLayer:

    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')

        if not api_key or api_key == '' or 'your_' in api_key:
            logger.info('LLM: No valid GROQ_API_KEY found. Using mock mode.')
            self.mock_mode = True
            self.client = None
            self.model_name = 'mock'
        else:
            from groq import Groq

            self.mock_mode = False
            self.client = Groq(api_key=api_key)

            self.model_name = os.getenv(
                'GROQ_MODEL',
                DEFAULT_GROQ_MODEL
            )

            logger.info(f'LLM: Using Groq model {self.model_name}')

    def run(self, mcp_output: dict) -> dict:
        try:
            threats = mcp_output['enriched_threats'][:5]

            logger.info(f'LLM explaining {len(threats)} threats')

            explanations = []

            for threat in threats:
                report = self._explain(threat)
                explanations.append({
                    **threat,
                    'llm_report': report
                })

            return {
                'status': 'OK',
                'layer': 'llm',
                'explained_threats': explanations,
                'count': len(explanations)
            }

        except Exception as e:
            logger.error(f'LLM failed: {e}')
            return {
                'status': 'ERROR',
                'layer': 'llm',
                'error': str(e)
            }

    # -----------------------------
    # SEVERITY (RULE-BASED ONLY)
    # -----------------------------
    def _calculate_severity(self, threat: dict) -> str:

        xgb = str(threat.get('xgb_prediction', 'BENIGN')).upper()
        bert = str(threat.get('bert_prediction', 'BENIGN')).upper()

        anomaly = bool(threat.get('ae_flagged', False))

        try:
            confidence = float(threat.get('confidence_pct') or 0)
        except Exception:
            confidence = 0

        ip_rep = threat.get('ip_reputation', {})

        known_bad_ip = (
            bool(threat.get('ip_is_known_bad', False))
            or ip_rep.get('risk') in ('HIGH', 'CRITICAL')
        )

        attack_votes = 0

        if xgb != 'BENIGN':
            attack_votes += 1

        if bert != 'BENIGN':
            attack_votes += 1

        if known_bad_ip:
            return 'HIGH'

        if attack_votes >= 2:
            return 'HIGH'

        if attack_votes == 1 and anomaly:
            return 'MEDIUM'

        if anomaly:
            if confidence < 40:
                return 'LOW'
            return 'MEDIUM'

        return 'LOW'

    # -----------------------------
    # EXPLAIN
    # -----------------------------
    def _explain(self, threat: dict):

        calculated_severity = self._calculate_severity(threat)

        if self.mock_mode:

            xgb = threat.get('xgb_prediction', 'BENIGN')
            bert = threat.get('bert_prediction', 'BENIGN')

            agreement = 'Agreed' if xgb == bert else 'Disagreed'

            return {
                'explanation': (
                    f"Network activity from {threat.get('ip')} "
                    f"was analyzed. Detected pattern corresponds to "
                    f"{threat.get('attack_type')} behavior signals."
                ),
                'why_dangerous': (
                    "Unusual network behavior may indicate abnormal activity "
                    "requiring further inspection."
                ),
                'mitigation': (
                    "1. Block or rate-limit source IP.\n"
                    "2. Inspect related logs.\n"
                    "3. Verify authentication attempts."
                ),
                'severity': calculated_severity,
                'model_agreement': f"XGBoost and BERT {agreement.lower()}."
            }

        ae_flagged = 'yes' if bool(threat.get('ae_flagged', False)) else 'no'
        ip_rep_reason = threat.get('ip_reputation', {}).get('reason', 'unknown')

        prompt = f"""
You are a cybersecurity analyst.

RULES:
- Do NOT invent CVEs, exploits, malware names, threat actors, or techniques.
- Do NOT speculate.
- Do NOT use phrases like zero-day, novel attack, unknown attack.
- Only use given event data.

SEVERITY (DO NOT CHANGE):
{calculated_severity}

Event:

IP: {threat.get('ip')}
Attack Type: {threat.get('attack_type')}
Confidence: {threat.get('confidence_pct')}
Anomaly Score: {threat.get('anomaly_score')}
Autoencoder: {ae_flagged}
IP Reputation: {ip_rep_reason}
XGBoost: {threat.get('xgb_prediction')}
BERT: {threat.get('bert_prediction')}

Return ONLY JSON:
{{
  "explanation": "...",
  "why_dangerous": "...",
  "mitigation": "...",
  "severity": "{calculated_severity}",
  "model_agreement": "..."
}}
"""

        fallback_idx = 0

        for attempt in range(1 + len(FALLBACK_GROQ_MODELS)):

            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a cybersecurity analyst. "
                                "Return ONLY valid JSON. "
                                "Never invent technical entities. "
                                "No markdown."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=600
                )

                raw = response.choices[0].message.content.strip()
                logger.info(f"Raw LLM response:\n{raw}")

                raw = _sanitize_llm_json(raw)

                if not raw:
                    raise json.JSONDecodeError("Empty", raw, 0)

                try:
                    parsed = json.loads(raw)

                    if isinstance(parsed, dict):
                        parsed['severity'] = calculated_severity
                        return parsed

                    raise ValueError("Non-object JSON")

                except Exception:
                    start = raw.find('{')
                    end = raw.rfind('}')

                    if start != -1 and end != -1:
                        parsed = json.loads(
                            _sanitize_llm_json(raw[start:end+1])
                        )

                        if isinstance(parsed, dict):
                            parsed['severity'] = calculated_severity
                            return parsed

                    return self._fallback(threat, calculated_severity)

            except Exception as e:
                msg = str(e)
                logger.error(f"LLM API error: {msg}")

                if (
                    'decommission' in msg.lower()
                    or 'model_decommissioned' in msg.lower()
                ) and fallback_idx < len(FALLBACK_GROQ_MODELS):

                    self.model_name = FALLBACK_GROQ_MODELS[fallback_idx]
                    fallback_idx += 1
                    continue

                return self._fallback(threat, calculated_severity)

        return self._fallback(threat, calculated_severity)

    def _fallback(self, threat: dict, severity: str):
        return {
            "explanation": "LLM unavailable.",
            "why_dangerous": "Requires manual review.",
            "mitigation": "1. Isolate host. 2. Review logs. 3. Escalate.",
            "severity": severity,
            "model_agreement": "Unknown"
        }