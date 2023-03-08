import boto3
import os
import requests as requests

s3_resource = boto3.resource('s3')

def authenticate(service: str, auth: str) -> str:
    """
    Authenticates with Nadeo Club Services and returns an access token.
    :service: Audience (e.g. "NadeoClubServices", "NadeoLiveServices")
    :auth: Authorization (e.g. "Basic <user:pass base 64>")
    :return: Authorization token
    """
    url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
    headers = {
        "Content-Type": "application/json",
        "Ubi-AppId": "86263886-327a-4328-ac69-527f0d20a237",
        "Authorization": auth,
        "User-Agent": "https://github.com/Nixotica/NadeoEventCreateAPI",
    }
    result = requests.post(url, headers=headers).json()

    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices"
    ticket = result["ticket"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"ubi_v1 t={ticket}"
    }
    body = {
        "audience": service
    }
    result = requests.post(url, headers=headers, json=body)
    return result.json()["accessToken"]

def lambda_handler(event, context):
    token = authenticate("NadeoClubServices", os.environ["AUTHORIZATION"])
    club_services_header = {"Authorization": "nadeo_v1 t=" + token}

    # Get the logo and competition id from s3
    bucket = s3_resource.Bucket(os.environ['STORAGE_BUCKET_NAME'])
    comp_id = int.from_bytes(bucket.Object('comp_id').get()['Body'].read(), 'big')

    # Delete the competition 
    delete_event_url = f"https://competition.trackmania.nadeo.club/api/competitions/{comp_id}/delete"
    requests.post(url=delete_event_url, headers=club_services_header)