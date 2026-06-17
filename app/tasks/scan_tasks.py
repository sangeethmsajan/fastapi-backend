import json
import docker
from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import Attack
from app.services.ai_analyzer import analyze_findings

@celery_app.task(bind=True, name="run_attack")
def run_attack(self, attack_id: int):
    db = SessionLocal()
    try:
        attack = db.query(Attack).filter(Attack.id == attack_id).first()
        if not attack:
            return {"status": "error", "message": "Attack not found"}

        attack.status = "Running"
        db.commit()

        client = docker.from_env()
        # run a fresh scanner container, pass the target as the argument.
        # it runs, prints JSON, and is auto-removed.
        output = client.containers.run(
            image="iosaf-scanner",
            command=[attack.target],     # becomes: python3 scanner.py <target>
            # network="scan-net",          # isolated network
            remove=True,                 # auto-delete container when done
            stdout=True,
        )

        findings = json.loads(output.decode())   # bytes -> JSON dict
        analysis = analyze_findings(findings)
        print("=== DEBUG START ===")
        print("attack id:", attack.id)
        print("analysis type:", type(analysis))
        print("analysis value:", analysis)
        dumped = json.dumps(analysis)
        print("dumped length:", len(dumped))
        attack.ai_analysis = dumped
        attack.response = json.dumps(findings)
        attack.status = "Completed"
        db.commit()
        db.refresh(attack)

        print("AFTER COMMIT -> attack.ai_analysis:", attack.ai_analysis)
        print("=== DEBUG END ===")
        # (next: save `findings` to your DB here)
        # print(findings)
        # analysis = analyze_findings(findings)
        # print("AI analysis:", analysis)
        # attack.response = json.dumps(findings)
        # attack.ai_analysis = json.dumps(analysis)   # save JSON as a strin   # save JSON as a string
        # # db.commit()
        # attack.status = "Completed"
        # db.commit()
        # db.refresh(attack)
        return {"status": "Completed", "attack_id": attack_id, "findings": findings}

    except Exception as e:
        attack.status = "Failed"
        db.commit()
        raise self.retry(exc=e, countdown=10, max_retries=2)
    finally:
        db.close()