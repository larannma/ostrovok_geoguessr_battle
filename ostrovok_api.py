import requests
import urllib

base_url = "http://larannma.fun/"


def create_user(effective_user_id, effective_user_username, chat_id):
    payload = {
            "effective_user_id": effective_user_id,
            "effective_user_username": effective_user_username,
            "chat_id": chat_id
            }
    en = urllib.parse.urlencode(payload)
    res = requests.post(base_url + '/create_user?' + en)

def add_points_to_user(tg_id, points):
    payload = {
        "tg_id": tg_id,
        "points": points
    }
    response = requests.post(base_url + '/add_points', json=payload)
    return response.json()

def set_user_email(tg_id, email):
    payload = {
        "tg_id": tg_id,
        "user_email": email
    }
    response = requests.post(base_url + '/set_email', json=payload)
    return response.json()

def set_user_name(tg_id, name):
    payload = {
        "tg_id": tg_id,
        "user_name": name
    }
    response = requests.post(base_url + '/set_name', json=payload)
    return response.json()

def set_favorite_language(tg_id, lang):
    payload = {
        "tg_id": tg_id,
        "favorite_language": lang
    }
    response = requests.post(base_url + '/set_language', json=payload)
    return response.json()

def set_user_company(tg_id, company):
    payload = {
        "tg_id": tg_id,
        "user_company": company
    }
    response = requests.post(base_url + '/set_company', json=payload)
    return response.json()

def set_user_jobTitle(tg_id, jobTitle):
    payload = {
        "tg_id": tg_id,
        "user_jobTitle": jobTitle
    }
    response = requests.post(base_url + '/set_jobTitle', json=payload)
    return response.json()

def get_total_points(tg_id):
    payload = {
        "tg_id": tg_id,
    }
    response = requests.post(base_url + '/get_points', json=payload)
    return response.json()

def get_all_users():
    response = requests.get(base_url + '/get_all_users')
    return response.json()

if __name__ == '__main__':
    exit(0)