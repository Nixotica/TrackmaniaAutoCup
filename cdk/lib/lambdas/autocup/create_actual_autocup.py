import datetime
import json
import os
import requests as requests
import openai
import boto3

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
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


def get_random_map_uid() -> str:
    url = "https://trackmania.exchange/mapsearch2/search?api=on&random=1"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Get-random-map / nixotica@gmail.com"
    }
    max_author_time = 70000
    min_author_time = 30000
    actual_author_time = 0
    while actual_author_time > max_author_time or actual_author_time < min_author_time:
        map_info = requests.post(url, headers=headers).json()
        actual_author_time = map_info["results"][0]["AuthorTime"]
    return map_info["results"][0]["TrackUID"]


def lambda_handler(event, context):
    token = authenticate("NadeoClubServices", os.environ["AUTHORIZATION"])
    club_services_header = {"Authorization": "nadeo_v1 t=" + token}

    # Get the logo and competition id from s3
    bucket = s3_resource.Bucket(os.environ['STORAGE_BUCKET_NAME'])
    # logo = bucket.Object('logo.png').get()['Body']
    comp_id = int.from_bytes(bucket.Object('comp_id').get()['Body'].read(), 'big')

    # Get the registered players from original competition
    get_participants_url = f"https://competition.trackmania.nadeo.club/api/competitions/{comp_id}/participants?offset=0&length=50"
    response = requests.get(url=get_participants_url, headers=club_services_header).json()
    
    participants = []
    for participant_data in response:
        participants.append(participant_data['participant'])

    # Delete the registration competition 
    delete_event_url = f"https://competition.trackmania.nadeo.club/api/competitions/{comp_id}/delete"
    response = requests.post(url=delete_event_url, headers=club_services_header)

    # Create actual competition
    payload = json.load(open(os.path.join(os.path.curdir, "CreateRegistrationEvent8.json")))

    date_format = "%Y-%m-%dT%H:%M:%S.000Z"
    now = datetime.datetime.now(datetime.timezone.utc)
    qualifierStart = datetime.datetime.strftime(now + datetime.timedelta(minutes=1), date_format)
    qualifierEnd = datetime.datetime.strftime(now + datetime.timedelta(minutes=11), date_format)
    round1Start = datetime.datetime.strftime(now + datetime.timedelta(minutes=12), date_format)
    round1End = datetime.datetime.strftime(now + datetime.timedelta(minutes=30), date_format)
    round2Start = datetime.datetime.strftime(now + datetime.timedelta(minutes=31), date_format)
    round2End = datetime.datetime.strftime(now + datetime.timedelta(minutes=50), date_format)

    qualifierMap = get_random_map_uid()
    round1Map = get_random_map_uid()
    round2Map = get_random_map_uid()

    payload["rounds"][0]["qualifier"]["startDate"] = qualifierStart
    payload["rounds"][0]["qualifier"]["endDate"] = qualifierEnd
    payload["rounds"][0]["qualifier"]["config"]["maps"] = [qualifierMap]
    payload["rounds"][0]["startDate"] = round1Start
    payload["rounds"][0]["endDate"] = round1End
    payload["rounds"][0]["config"]["maps"] = [round1Map]
    payload["rounds"][1]["startDate"] = round2Start
    payload["rounds"][1]["endDate"] = round2End
    payload["rounds"][1]["config"]["maps"] = [round2Map]

    create_comp_url = "https://competition.trackmania.nadeo.club/api/competitions/web/create"
    response = requests.post(
        url=create_comp_url,
        headers=club_services_header,
        json=payload
    ).json()
    comp_id: int = response["competition"]["id"]

    s3_client.put_object(
        Bucket=os.environ['STORAGE_BUCKET_NAME'],
        Key="comp_id",
        Body=comp_id.to_bytes(32, 'big')
    )

    # image_files = {"image": logo}

    # upload_logo_url = f"https://competition.trackmania.nadeo.club/api/competitions/{comp_id}/upload/logo"
    # response = requests.post(
    #     url=upload_logo_url,
    #     headers=club_services_header,
    #     files=image_files
    # )

    # Add registrants
    add_registrants_payload = {}
    seed = 1
    for participant in participants:
        add_registrants_payload = {"participant": participant, "seed": seed}
        add_participants_url = f"https://competition.trackmania.nadeo.club/api/competitions/{comp_id}/register"
        requests.post(url=add_participants_url, json=add_registrants_payload, headers=club_services_header)
        seed += 1
