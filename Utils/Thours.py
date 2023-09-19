import datetime
import random

import requests as req
import json

from config import *


class Thours:
    Headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh',
        'content-type': 'application/json;charset=UTF-8',
        'referer': 'https://cwp.alibabafoundation.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; Redmi K30 Pro) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36',
        'csr-account-v2': 'true',
        'csr-front-v': '1.1.3',
    }

    def __init__(self, token: str, uuid: str):
        self.token = token
        self.uuid = uuid
        self.Headers['csr-token'] = token
        self.Headers['csr-uuid'] = uuid

    def get_question_list(self):
        type_id_ret = req.get('https://m.3hours.taobao.com/ewrite/type?channelCode=',
                              headers=self.Headers, verify=VERIFY_SSL).json()
        question_list = []
        for q_type in type_id_ret['data']:
            question_ret = req.get(f'https://m.3hours.taobao.com/ewrite/exclusiveLetter?'
                                   f'typeId={q_type["typeId"]}'
                                   f'&pageIndex=1'
                                   f'&pageSize=20',
                                   headers=self.Headers, verify=VERIFY_SSL).json()
            for question in question_ret['data']['list']:
                question_list.append(question)
            pages = question_ret['data']['pages']
            for page in range(2, pages + 1):
                question_ret = req.get(f'https://m.3hours.taobao.com/ewrite/exclusiveLetter?'
                                       f'typeId={q_type["typeId"]}'
                                       f'&pageIndex={page}'
                                       f'&pageSize=20',
                                       headers=self.Headers, verify=VERIFY_SSL).json()
                for question in question_ret['data']['list']:
                    question_list.append(question)
        return question_list

    def get_question_detail(self, question_id: str) -> dict:
        return req.get(f'https://m.3hours.taobao.com/ewrite/questionDetail?id={question_id}',
                       headers=self.Headers, verify=VERIFY_SSL).json()

    def answer_question(self, question_id: str, answer: str) -> dict:
        return req.post('https://m.3hours.taobao.com/ewrite/reply',
                        headers=self.Headers, verify=VERIFY_SSL,
                        data=json.dumps({
                            'id': question_id,
                            'replyContent': answer,
                            'showState': 1
                        })).json()

    def get_topic_list(self):
        return req.get('https://ef.3hours.taobao.com/eknow/activity/getFirstPage?activityId=1&from=3hours',
                       headers=self.Headers, verify=VERIFY_SSL).json()

    def get_topic_detail(self, topic_id: str, activity_id: str) -> dict:
        return req.get(f'https://ef.3hours.taobao.com/eknow/activity/getQuestionPage?'
                       f'topicId={topic_id}&activityId={activity_id}',
                       headers=self.Headers, verify=VERIFY_SSL).json()

    def process_topic(self, topic_id: int, activity_id: int, page_id: int):
        return req.post('https://ef.3hours.taobao.com/eknow/user/processUserAnswer',
                        headers=self.Headers, verify=VERIFY_SSL, data=json.dumps({
                            'topicId': topic_id,
                            'activityId': activity_id,
                            'pageId': page_id,
                            'totalSeconds': random.randint(40, 60)
                        })).json()

    def save_topic_answer(self, topic_id: str | int, activity_id: str | int, page_id: str | int, option_id: str,
                          question_id: int) -> dict:
        return req.post('https://ef.3hours.taobao.com/eknow/user/saveUserAnswer?threehours-from-channel=',
                        headers=self.Headers, verify=VERIFY_SSL,
                        data=json.dumps({
                            'activityId': activity_id,
                            'topicId': topic_id,
                            'pageId': page_id,
                            'optionId': option_id,
                            'questionId': question_id
                        })).json()

    def get_book_donate_project(self):
        return req.get('https://m.3hours.taobao.com/donateRead/project/list?openBizCode=e_read_95_27&limit=1',
                       headers=self.Headers, verify=VERIFY_SSL).json()

    def get_book_list(self):
        # return req.get('https://m.3hours.taobao.com/read/teamBook?pageSize=20&pageIndex=1&teamId=1708',
        #               headers=self.Headers, verify=VERIFY_SSL).json()
        book_list = []
        total = 0
        page_size = 20
        page_index = 1
        while True:
            ret = req.get(f'https://m.3hours.taobao.com/read/get_subject_text?'
                          f'threehours-from-channel=&pageSize={page_size}&pageIndex={page_index}',
                          headers=self.Headers, verify=VERIFY_SSL).json()
            if 'data' not in ret or len(ret['data']['list']) == 0:
                break
            for index, book in enumerate(ret['data']['list']):
                # print(book)
                book_list.append(book)
                total += 1
            page_index += 1
            if total >= ret['data']['total']:
                break
        return book_list

    def read_donate(self, project_id: int | str, book_id: int | str, team_id: int | str,
                    voice_time: int | str, audio_link: str):
        return req.post('https://m.3hours.taobao.com/read/donate',
                        headers=self.Headers, verify=VERIFY_SSL,
                        data=json.dumps({
                            'projectId': project_id,
                            'bookId': book_id,
                            'teamId': team_id,
                            'voiceTime': voice_time,
                            'audioLink': audio_link
                        })).json()

    def step_donate(self):
        data = {
            'donateSteps': random.randint(10000, 20000),
            'scene': 'loveBean',
        }
        return req.post('https://m.3hours.taobao.com/donateStep/dailyDonate', headers=self.Headers,
                        verify=VERIFY_SSL, data=data).json()

    def get_today_charity_history_list(self):
        # 本地获取今年是多少年
        now = datetime.datetime.now().year
        today = datetime.date.today()
        charity_date = today
        page_index = 1
        history_list = []
        left_write = 0
        left_read = 0
        left_topic = 0
        while charity_date == today:
            ret = req.get(f'https://m.3hours.taobao.com/charityAccount/getUserCharityActionList?'
                          f'pageIndex={page_index}&pageSize=10&charityAcType=BENEFIT_UP&searchYear={now}',
                          headers=self.Headers, verify=VERIFY_SSL).json()
            if 'data' not in ret or len(ret['data']['list']) == 0:
                break
            for index, charity in enumerate(ret['data']['list']):
                charity_date = datetime.datetime.fromtimestamp(charity['approveDate'] / 1000).date()
                if charity_date == today:
                    history_list.append(charity)
                    if charity['subTitle'] == '益起写':
                        left_write += 1
                    if charity['subTitle'] == '益起读-捐声':
                        left_read += 1
                    if charity['subTitle'] == '益起猜-绿色答题互动':
                        left_topic += 1
                else:
                    break
            page_index += 1

        # if left_write == 10:
        #     left_write = True
        # else:
        #     left_write = False
        # if left_read == 5:
        #     left_read = True
        # else:
        #     left_read = False
        # if left_topic != 0:
        #     left_topic = True
        # else:
        #     left_topic = False

        return history_list, left_write, left_read, left_topic
