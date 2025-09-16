import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "update-auction-status-every-minute": {
        "task": "apps.listings.tasks.update_auction_status",
        "schedule": 60.0, 
    }
}


