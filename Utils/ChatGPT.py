import gc
import sys
import time

import openai
import requests as req
from config import *
from Utils.Other import get_config


TOKEN = get_config('token')

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
    if USE_OPENAI_API:
        openai.api_key = TOKEN
        answer = openai_chat(question, 'gpt-3.5-turbo')
        answer_content = ''
        print("AI答复：")
        for char in answer:
            answer_content += char
            sys.stdout.write(char)
            sys.stdout.flush()
        gc.collect()
        return answer_content
    else:
        result = ""
        DATA['prompt'] = question

        ret = req.post('https://chat.ncii.cn/api/v2/chat/completions', headers=HEADERS,
                       data=json.dumps(DATA).encode('utf-8'),
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
        gc.collect()
        return result


def openai_chat(question: str, model: str, role: str = None) -> str:
    """
    :param model: the model you want to use
    :param question: what you want to ask for
    :param role: the role of the question, if None, the role will be none.
    """
    start_time = time.time()
    response = openai.ChatCompletion.create(
        model=model,
        messages=role is not None and [
            {"role": "system", "content": role},
            {"role": "user", "content": question}
        ] or [
                     {"role": "user", "content": question}
                 ],
        stream=True
    )
    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = []
    # iterate through the stream of events
    try:
        for chunk in response:
            if chunk['choices'][0]['finish_reason'] == 'stop':
                break
            chunk_time = time.time() - start_time  # calculate the time delay of the chunk
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk['choices'][0]['delta']['content']  # extract the message
            collected_messages.append(chunk_message)  # save the message
            # print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}")
            # print the delay and text
            yield chunk_message
    except Exception as e:
        print(e)
        print(collected_chunks)
        print(collected_messages)
