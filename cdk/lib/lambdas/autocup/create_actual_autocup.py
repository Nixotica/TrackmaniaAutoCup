add_registrants_payload = {"participant":"dadbaf28-e7b5-429b-bf37-8c8c1419fcf4","seed":1}

add_participants_url = "https://competition.trackmania.nadeo.club/api/competitions/5059/register"


def lambda_handler(event, context):
    get_participants_url = "https://competition.trackmania.nadeo.club/api/competitions/5059/participants?offset=0&length=30"
    