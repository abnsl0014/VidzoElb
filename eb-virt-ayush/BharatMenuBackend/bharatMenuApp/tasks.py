# yourapp/tasks.py
from celery import shared_task
from .models import Reminder
from twilio.rest import Client
from urllib.parse import quote


@shared_task
def send_reminder(reminder_id):

    #I am the legitimate running task
    reminder = Reminder.objects.get(id=reminder_id)

    if reminder.status == "1":
        # Perform the reminder action, e.g., send a notification
        print(f"Sending reminder: {reminder.message} at {reminder.reminder_time}")

        reminder.status = "2"
        reminder.save()

        encoded_message = quote(reminder.message)

        url = f"http://backend.bharatmenu.com/api/callresponse/?message={encoded_message}"

        account_sid = "AC1027c48a892cea337d9d28fae752a186"
        auth_token = "7dee7fd1aff03e05b31f2500d4f1183c"
        client = Client(account_sid, auth_token)

        call = client.calls.create(
                                url=url,
                                to=reminder.phone_number,
                                from_='+14152879886'
                            )
        print(call.sid)
        reminder.call_sid = call.sid
        reminder.save()

        reminder.status = "4"
        reminder.save()

    
