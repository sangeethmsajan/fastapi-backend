from app.services.zap_service import zap_service

status = zap_service.get_active_scan_status("0")
print(f"Active scan progress: {status}%")
