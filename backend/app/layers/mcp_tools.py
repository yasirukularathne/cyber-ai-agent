from app.utils.logger import get_logger

logger = get_logger('mcp')

IP_BLACKLIST = {
    '45.12.22.1':    {'reason': 'Known C2 Server',      'risk': 'CRITICAL'},
    '103.45.66.2':   {'reason': 'Known DDoS Source',    'risk': 'HIGH'},
    '185.220.101.1': {'reason': 'Tor Exit Node',        'risk': 'HIGH'},
    '194.165.16.1':  {'reason': 'Known Port Scanner',   'risk': 'MEDIUM'},
    '10.0.0.200':    {'reason': 'Flagged Botnet Node',  'risk': 'HIGH'},
}
# NOTE: This is a static, hand-curated lookup table, not a live threat-intel
# feed (e.g. AbuseIPDB/VirusTotal). Any IP not in this 5-entry list will
# always resolve to 'UNKNOWN' risk. Fine for a coursework demo — just don't
# describe this as "live IP reputation checking" in writeups.

CVE_MAP = {
    'Brute Force': [
        {'id': 'CVE-2023-32784', 'desc': 'Password exposure via memory leak'},
        {'id': 'CVE-2022-1388',  'desc': 'BIG-IP iControl REST auth bypass'}
    ],
    'DDoS/DoS': [
        {'id': 'CVE-2023-44487', 'desc': 'HTTP/2 Rapid Reset DDoS attack'},
        {'id': 'CVE-2022-26134', 'desc': 'Confluence Server RCE via OGNL'}
    ],
    'Port Scan': [
        {'id': 'CVE-2021-44228', 'desc': 'Log4Shell - scanning phase indicator'}
    ],
    'Botnet': [
        {'id': 'CVE-2022-30190', 'desc': 'Follina - used in botnet payloads'},
        {'id': 'CVE-2023-23397', 'desc': 'Outlook privilege escalation'}
    ]
}

# ── FIX: alias map from real model labels (e.g. CIC-IDS2017 class names)
# to the CVE_MAP keys above. Without this, CVE_MAP.get(atype, []) almost
# never matched because the model's actual labels ('PortScan', 'Bot',
# 'DDoS', 'FTP-Patator', etc.) don't equal the CVE_MAP keys verbatim.
# VERIFY against your real label set (print fusion_output['threats'][0]
# ['attack_type'] and check your label encoder) before trusting this.
ATTACK_TYPE_TO_CVE_KEY = {
    'FTP-Patator': 'Brute Force',
    'SSH-Patator': 'Brute Force',
    'Web Attack – Brute Force': 'Brute Force',
    'DDoS': 'DDoS/DoS',
    'DoS Hulk': 'DDoS/DoS',
    'DoS GoldenEye': 'DDoS/DoS',
    'DoS slowloris': 'DDoS/DoS',
    'DoS Slowhttptest': 'DDoS/DoS',
    'PortScan': 'Port Scan',
    'Bot': 'Botnet',
}
# Classes with no curated CVE entries (will always show "Related CVEs: None"):
# Infiltration, Heartbleed, Web Attack – XSS, Web Attack – Sql Injection, BENIGN


class MCPToolLayer:
    """
    Layer 7: Enriches threats with IP reputation, CVE mapping, and incident summary.
    """

    def run(self, fusion_output: dict) -> dict:
        try:
            threats = fusion_output['threats']
            enriched = []
            skipped = 0

            for threat in threats:
                try:
                    ip    = threat['ip']
                    atype = threat['attack_type']

                    ip_rep = IP_BLACKLIST.get(ip, {
                        'reason': 'No known threat intelligence', 'risk': 'UNKNOWN'
                    })

                    cve_key = ATTACK_TYPE_TO_CVE_KEY.get(atype, atype)
                    cves = CVE_MAP.get(cve_key, [])

                    enriched.append({
                        **threat,
                        'ip_reputation': ip_rep,
                        'related_cves': cves,
                        'ip_is_known_bad': ip in IP_BLACKLIST,
                        'incident_summary': self._format_summary(threat, ip_rep, cves)
                    })
                except Exception as item_err:
                    # ── FIX: don't let one malformed threat abort the whole batch
                    skipped += 1
                    logger.warning(f'MCP: skipping malformed threat record: {item_err}')
                    continue

            known_bad = sum(1 for e in enriched if e['ip_is_known_bad'])
            logger.info(
                f'MCP: {known_bad} known-bad IPs found in {len(enriched)} threats'
                f'{f" ({skipped} skipped)" if skipped else ""}'
            )

            return {
                'status': 'OK',
                'layer': 'mcp',
                'enriched_threats': enriched,
                'known_bad_ips': known_bad
            }
        except Exception as e:
            logger.error(f'MCP failed: {e}')
            return {'status': 'ERROR', 'layer': 'mcp', 'error': str(e)}

    def _format_summary(self, threat, ip_rep, cves) -> str:
        cve_str = ', '.join(c['id'] for c in cves) if cves else 'None'
        return (
            f"Threat: {threat['attack_type']} from {threat['ip']}. "
            f"Severity: {threat['severity']}. "
            f"IP Intel: {ip_rep['reason']}. "
            f"Related CVEs: {cve_str}."
        )