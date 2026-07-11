from app.services.zap_service import zap_service

# Start active scan
scan_id = zap_service.start_active_scan('http://host.docker.internal:3000')
print(f'Active scan started, scan ID: {scan_id}')
