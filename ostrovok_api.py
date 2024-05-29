import requests
import json
import urllib

base_url = "https://larannma.fun/"

def create_character(effective_user_id, effective_user_username, chat_id):
    data = {
            "effective_user_id": effective_user_id,
            "effective_user_username": effective_user_username,
            "chat_id": chat_id
            }
    response = requests.post(base_url, json=data)

if __name__ == '__main__':
  exit(0)