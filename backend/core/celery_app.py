import os

from celery import Celery

app = Celery(
    "archangel",
    broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    include=["core.tasks"],
)

app.conf.timezone = "UTC"
app.conf.beat_schedule = {
    # cron-syntax scheduled tasks land here, e.g.:
    # "poll-devices-every-minute": {
    #     "task": "core.tasks.run_polling_cycle",
    #     "schedule": crontab(minute="*"),
    # },
}
