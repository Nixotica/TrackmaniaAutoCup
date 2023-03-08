import requests
import os
import json

def lambda_handler(event, context):
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

    data = {
        "content": f"<@&1080011219043360819> Another edition of Auto Cup will be starting in 1 hour! Join \"Auto Events\" Club to play!"
    }
    json_data = json.dumps(data)

    requests.post(url=webhook_url, data=json_data, headers={"Content-Type": "application/json"})
