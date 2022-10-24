import codecs
import hashlib
import hmac
import json
from datetime import datetime
from urllib.parse import urlparse

import requests
from django.utils.http import http_date


def headers(http_verb, api_url):
    user = "kinoapp"
    secrets = "WvYXTIwEB5x1EjdGAq6Dvz6NMFBM0J"

    if not api_url:
        return

    if not api_url.startswith("http"):
        api_url = "http://" + api_url

    date = http_date(datetime.now().timestamp())
    path = urlparse(api_url).path
    signature = hmac.new(
        codecs.encode(secrets),
        codecs.encode("\n".join([http_verb, path, date])),
        hashlib.sha256,
    ).hexdigest()

    return {
        "Date": date,
        "Authorization": " ".join(["videos", user, signature]),
        "Content-Type": "application/json",
    }


def get_video(video_id):
    if not video_id:
        return

    api_url = f"http://videos.stroeermediabrands.de/videos/{video_id}"
    head = headers("GET", api_url)
    path = urlparse(api_url).path

    s = requests.Session()
    result = s.get(url=api_url, headers=head)

    data = json.loads(result.text)
    return data


def delete_video(video_id):
    if not video_id:
        return

    api_url = f"http://videos.stroeermediabrands.de/videos/{video_id}"
    head = headers("DELETE", api_url)
    path = urlparse(api_url).path

    s = requests.Session()
    result = s.delete(url=api_url, headers=head)

    return result.status_code


def update_video(video_id, media, data_props=None, preview_image=None):
    api_url = f"http://videos.stroeermediabrands.de/videos/{video_id}"
    head = headers("PUT", api_url)
    path = urlparse(api_url).path
    # if preview_image:
    #     params = json.dumps({"title": media.name, "preview_image": preview_image})
    # else:
    #     params = json.dumps({"title": media.name})
    params = json.dumps({"title": media.name})

    s = requests.Session()
    result = s.put(url=api_url, data=params, headers=head)
    return result.status_code


def set_video(video_url, priority=3):
    api_url = "http://videos.stroeermediabrands.de/import-start"
    head = headers("POST", api_url)
    uri = urlparse(api_url)
    params = json.dumps({"url": video_url, "priority": priority})
    s = requests.Session()
    result = s.post(url=api_url, headers=head, data=params)
    data = json.loads(result.text)
    return data


def fine_uploader_data(path, filename, callback, priority):
    api_url = "http://videos.stroeermediabrands.de/" + path
    head = headers("POST", api_url)
    uri = urlparse(api_url)

    params = json.dumps(
        {"filename": filename, "target": callback, "priority": priority}
    )
    s = requests.Session()
    result = s.post(url=api_url, headers=head, data=params)
    data = json.loads(result.text)
    return data


def fine_uploader_config(path):
    api_url = "http://videos.stroeermediabrands.de/" + path
    head = headers("GET", api_url)
    uri = urlparse(api_url)

    s = requests.Session()
    result = s.get(url=api_url, headers=head)

    data = json.loads(result.text)
    return data


def fine_uploader_policy(path, header):
    api_url = "http://videos.stroeermediabrands.de/" + path
    head = headers("POST", api_url)
    uri = urlparse(api_url)
    params = json.dumps({"headers": header})
    s = requests.Session()
    result = s.post(url=api_url, headers=head, data=params)
    data = json.loads(result.text)
    return data
