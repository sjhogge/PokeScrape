import schedule
import time
from main import full_update

def job():
  full_update()

# Run every morning at 4:00am Eastern Time
schedule.every().day.at("08:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(30)