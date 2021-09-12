import datetime
import requests
import os
from DotEnvHandler import set_environ

set_environ()

def send_webhook(webhook_url, data, is_embed, color):

    #https://discord.com/developers/docs/resources/webhook
    #https://discord.com/developers/docs/resources/channel#embed-object
   
    message = data["message"]
    title = data["title"]
    full_message = data["full_message"]
    replit_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Repl.it_logo.svg/1200px-Repl.it_logo.svg.png"


    if is_embed:
        timestamp = datetime.datetime.now().astimezone().isoformat()
        embed = {
            "title": title,
            "description": message,
            "color" : color,
            "timestamp": timestamp,
            }

        webhook_data = {
            "embeds" : [embed],
            "username": "Replit",
            "avatar_url" : replit_image
        }

    else:
        webhook_data = {
            "content" : full_message,
            "username": "Replit",
            "avatar_url" : replit_image
        }

    r = requests.post(webhook_url, json=webhook_data, headers={'Content-Type': 'application/json'})
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)

if __name__ == "__main__":

  webhook_data = {
    "message" : "It works!!",
    "title" : "Replit Server Update",
    "full_message" : "Replit Server has been updated"
  }
  webhook_url = os.environ["DiscordWebhook"]

  send_webhook(webhook_url, webhook_data, True, 38655)