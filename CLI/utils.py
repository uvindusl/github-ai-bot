import requests

base_url  = "http://127.0.0.1:8000"

def send_request(endpoint, data):
    url = f'{base_url}/{endpoint}'
    r = requests.post(url=url, json=data)
    response = r.text
    print(response)