import json
import time
import docker
from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import Attack, Scan
from app.services.ai_analyzer import analyze_findings
from app.services.zap_service import zap_service


@celery_app.task(bind=True, name="run_attack", time_limit=3600, soft_time_limit=3500)
def run_attack(self, attack_id: int):
    db = SessionLocal()
    attack = None

    try:
        attack = db.query(Attack).filter(Attack.id == attack_id).first()
        if not attack:
            return {"status": "error", "message": "Attack not found"}

        attack.status = "Running"
        db.commit()

        target = attack.target

        # ── Stage 1: Nmap ─────────────────────────────────────────
        print(f"[*] Stage 1 — Nmap scanning {target}")

        try:
            client = docker.from_env()
            output = client.containers.run(
                image="iosaf-scanner",
                command=[target],
                remove=True,
                stdout=True,
            )
            nmap_findings = json.loads(output.decode())
            print(f"[✓] Nmap completed")

            nmap_scan = Scan(
                attack_id=attack_id,
                tool="nmap",
                command=f"nmap {target}",
                raw_output=json.dumps(nmap_findings)[:60000],
                status="Completed",
            )
            db.add(nmap_scan)
            try:
                db.commit()
            except Exception as db_err:
                db.rollback()
                print(f"[!] Nmap DB save failed: {db_err}")

            try:
                nmap_analysis = analyze_findings(nmap_findings)
                attack.response    = json.dumps(nmap_findings)[:60000]
                attack.ai_analysis = json.dumps(nmap_analysis)[:60000]
                db.commit()
            except Exception as ai_err:
                db.rollback()
                print(f"[!] AI analysis failed: {ai_err}")

        except Exception as nmap_err:
            db.rollback()
            print(f"[!] Nmap failed: {nmap_err}")
            nmap_findings = {}

        # ── Stage 2: ZAP ──────────────────────────────────────────
        print(f"[*] Stage 2 — ZAP scanning {target}")

        zap_scan = Scan(
            attack_id=attack_id,
            tool="zap",
            command=f"zap spider {target}",
            status="Running",
        )
        db.add(zap_scan)
        try:
            db.commit()
            db.refresh(zap_scan)
        except Exception as db_err:
            db.rollback()
            print(f"[!] ZAP scan row create failed: {db_err}")

        try:
            # Clear previous ZAP session
            zap_service.clear_session()

            # Format target URL
            target_url = target if target.startswith("http") else f"http://{target}"

            # Step 1 — Spider only
            print(f"[*] ZAP Spider starting on {target_url}")
            spider_id = zap_service.start_spider(target_url)

            elapsed = 0
            max_spider_time = 300  # 5 minutes max for spider

            while True:
                status = zap_service.get_spider_status(spider_id)
                print(f"[*] Spider progress: {status}%")
                if status >= 100:
                    break
                if elapsed >= max_spider_time:
                    print(f"[!] Spider timeout — saving partial results")
                    break
                time.sleep(5)
                elapsed += 5

            print(f"[✓] Spider completed")

            # Step 2 — Active scan skipped for now
            print(f"[*] Skipping active scan — spider results only")

            # Step 3 — Get alerts from spider
            alerts = zap_service.get_alerts()
            print(f"[✓] ZAP found {len(alerts)} alerts")

            # Deduplicate alerts
            unique_alerts = {}
            for alert in alerts:
                name = alert.get('alert')
                if name not in unique_alerts:
                    unique_alerts[name] = {
                        "alert": name,
                        "risk":  alert.get('risk'),
                        "url":   alert.get('url'),
                        "description": alert.get('description', '')[:200],
                    }

            unique_list = list(unique_alerts.values())

            # Save ZAP results — truncated to prevent MySQL overflow
            zap_scan.raw_output            = json.dumps(alerts)[:60000]
            zap_scan.vulnerabilities_found = json.dumps(unique_list)
            zap_scan.status                = "Completed"

            try:
                db.commit()
                print(f"[✓] ZAP results saved — {len(unique_list)} unique vulnerability types")
            except Exception as db_err:
                db.rollback()
                print(f"[!] ZAP DB save failed: {db_err}")
                try:
                    zap_scan.raw_output = "truncated — too large"
                    zap_scan.status     = "Completed"
                    db.commit()
                except:
                    db.rollback()

        except Exception as zap_error:
            db.rollback()
            print(f"[!] ZAP failed: {zap_error}")
            try:
                zap_scan.status = "Failed"
                db.commit()
            except:
                db.rollback()

        # ── Done ──────────────────────────────────────────────────
        try:
            attack.status = "Completed"
            db.commit()
            db.refresh(attack)
        except Exception as final_err:
            db.rollback()
            print(f"[!] Final status update failed: {final_err}")

        print(f"[✓] Attack {attack_id} completed")

        return {
            "status":    "Completed",
            "attack_id": attack_id,
            "findings":  nmap_findings,
        }

    except Exception as e:
        db.rollback()
        if attack:
            try:
                attack.status = "Failed"
                db.commit()
            except:
                db.rollback()
        raise self.retry(exc=e, countdown=10, max_retries=2)

    finally:
        db.close()