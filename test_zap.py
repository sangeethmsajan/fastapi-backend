from app.services.zap_service import zap_service

# Test connection
result = zap_service._get('core/view/version/')
print('ZAP connected:', result)

# Clear previous session
zap_service.clear_session()
print('Session cleared')

# Start spider on Juice Shop
scan_id = zap_service.start_spider('http://host.docker.internal:3000')
print('Spider started, scan ID:', scan_id)
