from app.services.zap_service import zap_service

alerts = zap_service.get_alerts()
print(f"Total vulnerabilities found: {len(alerts)}")
print("---")
for alert in alerts[:10]:  # show first 10 only
    print(f"Alert: {alert.get('alert', 'N/A')}")
    print(f"Risk:  {alert.get('risk', 'N/A')}")
    print(f"URL:   {alert.get('url', 'N/A')}")
    print("---")
