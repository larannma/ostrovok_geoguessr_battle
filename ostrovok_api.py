import requests
import urllib

base_url = "https://larannma.fun/"


def create_user(effective_user_id, effective_user_username, chat_id):
    payload = {
            "effective_user_id": effective_user_id,
            "effective_user_username": effective_user_username,
            "chat_id": chat_id
            }
    en = urllib.parse.urlencode(payload)
    res = requests.post(base_url + '/create_user?' + en)

if __name__ == '__main__':
    exit(0)