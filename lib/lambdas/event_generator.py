import datetime
import json
import os.path
import requests as requests

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
    payload = json.load(open(os.path.join(os.path.curdir, "../payloads/CreateEvent.json")))

    token = authenticate("NadeoClubServices", os.environ["AUTHORIZATION"])

    date_format = "%Y-%m-%dT%H:%M:%S.000Z"
    now = datetime.datetime.now(datetime.timezone.utc)
    registrationStart = datetime.datetime.strftime(now + datetime.timedelta(minutes=1), date_format)
    registrationEnd = datetime.datetime.strftime(now + datetime.timedelta(minutes=5), date_format)
    qualifierStart = datetime.datetime.strftime(now + datetime.timedelta(minutes=6), date_format)
    qualifierEnd = datetime.datetime.strftime(now + datetime.timedelta(minutes=15), date_format)
    round1Start = datetime.datetime.strftime(now + datetime.timedelta(minutes=16), date_format)
    round1End = datetime.datetime.strftime(now + datetime.timedelta(minutes=25), date_format)
    round2Start = datetime.datetime.strftime(now + datetime.timedelta(minutes=26), date_format)
    round2End = datetime.datetime.strftime(now + datetime.timedelta(minutes=35), date_format)

    qualifierMap = get_random_map_uid()
    round1Map = get_random_map_uid()
    round2Map = get_random_map_uid()

    payload["registrationEndDate"] = registrationEnd
    payload["registrationStartDate"] = registrationStart
    payload["rounds"][0]["qualifier"]["startDate"] = qualifierStart
    payload["rounds"][0]["qualifier"]["endDate"] = qualifierEnd
    payload["rounds"][0]["qualifier"]["config"]["maps"] = [qualifierMap]
    payload["rounds"][0]["startDate"] = round1Start
    payload["rounds"][0]["endDate"] = round1End
    payload["rounds"][0]["config"]["maps"] = [round1Map]
    payload["rounds"][1]["startDate"] = round2Start
    payload["rounds"][1]["endDate"] = round2End
    payload["rounds"][1]["config"]["maps"] = [round2Map]

    club_services_header = {"Authorization": "nadeo_v1 t=" + token}
    create_comp_url = "https://competition.trackmania.nadeo.club/api/competitions/web/create"
    response = requests.post(
        url=create_comp_url,
        headers=club_services_header,
        json=payload
    ).json()
    print(response)


lambda_handler(None, None)
