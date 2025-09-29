import requests
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

base_url  = os.getenv("URL")

def send_request(endpoint, data):
    url = f'{base_url}/{endpoint}'
    r = requests.post(url=url, json=data)
    response = r.text
    print(response)