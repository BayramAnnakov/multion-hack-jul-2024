
import requests

# replace your vercel domain
base_url = 'https://suno-api-gamma-six.vercel.app'


def custom_generate_audio(prompt:str,):
    url = f"{base_url}/api/generate"


    payload = {
        "prompt": prompt,
        "make_instrumental": False,
        "wait_audio": True
    }
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})

    print(response)


    return response.json()





