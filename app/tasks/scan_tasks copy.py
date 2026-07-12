from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import Attack


@celery_app.task(bind=True, name="run_attack")
def run_attack(self, attack_id: int):
    db = SessionLocal()
    try:
        attack = db.query(Attack).filter(Attack.id == attack_id).first()
        if not attack:
            return {"status": "error", "message": "Attack not found"}

        # Mark as Running
        attack.status = "Running"
        db.commit()

        # TODO: Replace with actual Docker SDK + Nmap execution
        import time
        time.sleep(5)

        # Mark as Completed
        attack.status = "Completed"
        db.commit()

        return {"status": "Completed", "attack_id": attack_id}

    except Exception as e:
        attack.status = "Failed"
        db.commit()
        raise self.retry(exc=e, countdown=10, max_retries=2)

    finally:
        db.close()