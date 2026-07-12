from app.services.zap_service import zap_service
from app.ai.analyzer import analyzer
import json

# Get alerts
alerts = zap_service.get_alerts()
print(f"Total vulnerabilities: {len(alerts)}")

# Prepare summary for DeepSeek — don't send all 594, too many tokens
# Group by alert type and take unique ones
unique_alerts = {}
for alert in alerts:
    name = alert.get('alert')
    if name not in unique_alerts:
        unique_alerts[name] = {
            "alert": name,
            "risk": alert.get('risk'),
            "url": alert.get('url'),
            "description": alert.get('description', '')[:200],
        }

unique_list = list(unique_alerts.values())
print(f"Unique vulnerability types: {len(unique_list)}")
print("Sending to DeepSeek for analysis...")

# Send to DeepSeek
analysis = analyzer.analyze_recon(
    tool="zap",
    raw_output=json.dumps(unique_list),
    target="host.docker.internal:3000"
)

print("\n=== DeepSeek Analysis ===")
print(f"Summary: {analysis.get('summary')}")
print(f"Risk Score: {analysis.get('risk_score')}")
print(f"\nVulnerabilities identified:")
for v in analysis.get('vulnerabilities', []):
    print(f"  - [{v.get('severity').upper()}] {v.get('name')}")
print(f"\nNext attacks recommended:")
for n in analysis.get('next_attacks', []):
    print(f"  - {n.get('tool')}: {n.get('reason')}")
