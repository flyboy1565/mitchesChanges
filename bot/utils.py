import requests

def make_requests(url, type, headers=None, params=None, data=None):
    if type == 'get':
        response = requests.get(url, headers=headers, params=params, data=data)
    else:
        response = requests.post(url, headers=headers, params=params, data=data)
    if response.status_code > 300:
        raise BaseException(f'Failed to Make Successful request: {url} {data}')
    return response.json()    

# https://www.twitch.tv/kitboga

from twitchrealtimehandler import TwitchAudioGrabber
import numpy as np
audio_grabber = TwitchAudioGrabber(
    twitch_url="https://www.twitch.tv/kitboga",
    blocking=True,
    segment_length=2,
    rate=16000,
    channels=2,
    dtype=np.int16)

audio_segment = audio_grabber.grab()
audio_grabber.terminate()

