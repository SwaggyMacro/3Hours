import sys

import requests as req
import json
from config import *

def get_config() -> dict:
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.loads(f.read())


TOKEN = get_config()['token']

HEADERS = {
    'content-type': 'application/json;charset=UTF-8',
    'Token': TOKEN,
}

DATA = {
    "prompt": "",
    "parentMessageId": "",
    "options": {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "max_tokens": 2000
    }
}


def get_api_reply(question: str) -> str:
    result = ""
    DATA['prompt'] = question

    ret = req.post('https://chat.ncii.cn/api/v2/chat/completions', headers=HEADERS, data=json.dumps(DATA).encode('utf-8'),
                   stream=True, verify=VERIFY_SSL)
    print("AI答复：")
    for content in ret.iter_lines():
        if content == '':
            continue
        json_ret = json.loads(content)
        if 'content' in json_ret.keys():
            result += json_ret['content']
        sys.stdout.write(json_ret['content'])
        sys.stdout.flush()

    return result
