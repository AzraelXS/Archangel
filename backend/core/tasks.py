from core.celery_app import app


@app.task
def run_polling_cycle():
    """Entry point for the scheduled polling engine. Placeholder."""
    pass
