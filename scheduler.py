import schedule
import time
from main import full_update
from WebhookHandler import send_webhook
import os

def job():
  full_update()

# Run every morning at 4:00am Eastern Time
schedule.every().day.at("08:00").do(job)

# Send Webhook Start Message
message = ""
webhook_url = os.environ["DiscordWebhook"]
webhook_data = {
  "message" : message,
  "title" : "Replit Server Started",
  "full_message" : message
}
send_webhook(webhook_url, webhook_data, is_embed=True, color=15907099)

while True:
    schedule.run_pending()
    time.sleep(30)