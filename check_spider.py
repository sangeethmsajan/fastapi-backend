from app.services.zap_service import zap_service

status = zap_service.get_spider_status("0")
print(f"Spider progress: {status}%")
