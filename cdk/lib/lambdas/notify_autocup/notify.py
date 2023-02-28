import requests
import json

def lambda_handler(event, context):
    webhook_url = "https://discord.com/api/webhooks/1080032572429565992/13j6IcLkdbWZHU47eFgTCbHJAPJnu0a6fulHuP64zS8VgMn9fnB6ffh61M6n3TpDD85a"

    data = {
        "content": f"<@&1080011219043360819> Another edition of Auto Cup will be starting in 1 hour! Join \"Auto Events\" Club to play!"
    }
    json_data = json.dumps(data)

    requests.post(url=webhook_url, data=json_data, headers={"Content-Type": "application/json"})
