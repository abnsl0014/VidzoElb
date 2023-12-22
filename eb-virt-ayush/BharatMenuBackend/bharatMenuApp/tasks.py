# yourapp/tasks.py
from celery import shared_task
from .models import Reminder

@shared_task
def send_reminder(reminder_id):
    reminder = Reminder.objects.get(id=reminder_id)
    # Perform the reminder action, e.g., send a notification
    print(f"Sending reminder: {reminder.message} at {reminder.reminder_time}")
    # Add your reminder processing logic here
