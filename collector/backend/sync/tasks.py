from core.celery_app import app
from sync.shipper import ship_backlog


@app.task
def ship_backlog_task():
    ship_backlog()
