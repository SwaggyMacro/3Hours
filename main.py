import random
import re
import string

from Utils import Memory
from Utils.Memory import is_minigram_running
from Utils.Other import random_replace_star
from Utils.Thours import Thours
from Utils.ChatGPT import *
from sys import exit
import traceback

WRITE_LIMIT_PER_DAY = 10
READ_LIMIT_PER_DAY = 5
TOPIC_LIMIT_PER_DAY = 1


def question_func(hours: Thours, wrote_times: int = 0):
    print('正在获取问题列表...\n')
    question_list = hours.get_question_list()
    print(f'获取完毕，总共 {len(question_list)} 个问题。\n')
    for index, question in enumerate(question_list):

        if wrote_times >= WRITE_LIMIT_PER_DAY:
            print(f"今日已经回答了10个问题，跳过\n")
            break

        print(f"正在回答第 {index + 1} 个问题: \n问题内容: {question['content']}")
        question_detail = hours.get_question_detail(question['id'])
        if question_detail['data']['hasReply']:
            print(f"\n问题已经回答过了，跳过\n")
            continue

        print(f"询问AI中...\n")
        try:
            answer = get_api_reply(
                f"我希望你能扮演一个心理学家。我将向你提供我的想法。我希望你能给我科学的建议，使我感觉更好，你不需要说明你的身份，"
                f"并且你给我的回答最好只有50至100字的文章篇幅。"
                f"我的第一个问题是：\n{question['content']}").replace('\n\n', '\n')
        except:
            # 超时就再来一次，JSONDecodeError一般为服务器问题或超时
            answer = get_api_reply(
                f"我希望你能扮演一个心理学家。我将向你提供我的想法。我希望你能给我科学的建议，使我感觉更好，你不需要说明你的身份，"
                f"并且你给我的回答最好只有50至100字的文章篇幅。"
                f"我的第一个问题是：\n{question['content']}").replace('\n\n', '\n')
        # 正则表达式删除掉 "作为xxx，"
        answer = re.sub(r'^作为\w+，', '', answer)
        print(f"\n\n提交回答：\n{answer}\n")
        print(f"正在提交回答...\n")
        answer_result = hours.answer_question(question['id'], answer)
        if answer_result['code'] == 200:
            # print(f"回答成功，审核通过后，请到“人人3小时公益”-“养豆”频道，领取爱能，积攒爱能还可兑换丰富好礼哟～\n")
            print(f"回答完毕\n")
        elif answer_result['code'] == 201:
            print(f"{answer_result['msg']}\n")
        elif answer_result['code'] == 1017:
            input("回答失败，用户未授权! \
            亲您手动前往益起写界面随便点击一个问题回答，授权信息后再来运行本程序！\n")
        else:
            print(f"回答失败，错误信息: {answer_result}\n")
        print('----------------------------------')
        wrote_times += 1

    print('\n益起写执行完毕，开始执行益起猜。\n')


def topic_func(hours: Thours):
    topic_list = hours.get_topic_list()
    topic_id = topic_list['data']['knowTopic']['topicId']
    activity_id = topic_list['data']['knowActivity']['activityId']
    topic_detail = hours.get_topic_detail(topic_id, activity_id)
    page_id = topic_detail['data']['pageId']
    for index, question in enumerate(topic_detail['data']['questionList']):
        print(f"正在回答第 {index + 1} 个问题: \n问题内容: {question['content']}")
        print(f"问题选项: {', '.join(str(v['optionText']) for v in question['optionList'])}")
        random_option_id = random.randint(0, len(question['optionList']) - 1)
        save_result = hours.save_topic_answer(topic_id,
                                              activity_id,
                                              topic_detail['data']['pageId'],
                                              question['optionList'][random_option_id]['optionId'],
                                              question['questionId'])
        print("\n保存答案中...\n")
        print(f"已随机选择: {question['optionList'][random_option_id]['optionText']}\n")
        if save_result['code'] == 200:
            print(f"答案{save_result['data']['correct'] is True and '正确' or '错误'}")
        elif save_result['code'] == 2003:
            print(f"{save_result['msg']}")
            break
        else:
            print(f"答案保存失败，错误信息: {save_result}\n")
        print("答案保存成功\n")
        print('----------------------------------')
    topic_ret = hours.process_topic(topic_id, activity_id, page_id)
    if topic_ret['code'] == 200:
        print('\n益起猜执行完毕\n')
    elif topic_ret['code'] == 2003:
        print(f"今日益起猜已完成答题，跳过答题，直接结束任务。\n")
    else:
        print(f"益起猜执行失败，错误信息: {topic_ret}\n")
    print('----------------------------------')


def read_book_func(hours: Thours, read_times: int = 0):
    team_id = "1708"  # fixed value
    book_list = hours.get_book_list()
    project = hours.get_book_donate_project()
    project_id = project['data'][0]['id']
    project_title = project['data'][0]['extResources']['title']

    print(f"\n助力项目: {project_title}\n")
    print(f"\n开始朗读书籍\n\n")
    for index, book in enumerate(book_list):
        if read_times >= READ_LIMIT_PER_DAY or index >= READ_LIMIT_PER_DAY:
            print(f"\n今日朗读已捐声5次，跳过朗读。\n\n益起读任务执行完毕\n")
            break
        audio_link = "https://piccommon.oss-cn-beijing.aliyuncs.com/e_read/voice/" + \
                     str(''.join(
                         random.sample(string.ascii_letters + string.digits, 8))).lower() + ".mp4"  # random link
        print(f"正在朗读第 {index + 1} 本书: \n书籍名称: {book['title']}\n书籍作者：{book['author']}\n"
              f"数量：{book['subTitle']}\n书籍内容：{book['content']}\n最短时间：{book['minTime']}\n")
        ret = hours.read_donate(project_id, book['bookId'], team_id, book['minTime'] + 10, audio_link)
        if ret['code'] == 200 and ret['msg'] in ['success', '']:
            print(f"\n朗读成功\n")
        else:
            print(f"\n朗读失败，错误信息: {ret}\n")
            if ret['code'] == 201:
                continue  # 朗读失败，跳过本次朗读
        print('----------------------------------')
        read_times += 1
    print('----------------------------------')


def donate_steps_func(hours: Thours):
    print(hours.step_donate())
    print('\n益起跑步数捐赠执行完毕\n')
    print('----------------------------------')


def main():
    print('######《人人3小时》全自动捐步、益起写、益起猜、益起读程序######\n')
    token, uuid = Memory.get_token_uuid_new()
    if token is None:
        if not is_minigram_running():
            print('获取TOKEN失败，请检查是否已经登录PC端微信并打开人人3小时小程序！\n')
            input("按下回车键退出程序...")
            exit(0)

        input(
            '获取TOKEN失败，请务必点击小程序中 "下方导航栏→《公益机会》→《益起动》(去捐步)" 微信授权后回车重试！\n等待回车后开始执行程序...\n')
        token, uuid = Memory.get_token_uuid_new()

    print("TOKEN: ", random_replace_star(token))
    print("UUID: ", uuid is not None and random_replace_star(uuid) or '获取失败')

    hours = Thours(token, uuid)
    # print('\n获取用户信息成功，开始执行益起跑捐赠任务\n')
    #
    # try:
    #     donate_steps_func(hours)
    # except:
    #     print('执行"益起跑"遇到错误: \n' + traceback.format_exc() + '\n')
    #     if str(input('输入"r"重试，输入任意字符退出程序（按下回车键)')) == 'r':
    #         question_func(hours)
    #     else:
    #         exit(0)
    print('\n获取用户信息成功，开始执行益起写问答任务\n')

    history_list, write, read, topic = hours.get_today_charity_history_list()
    print(
        f"今日需要执行的任务：\n益起写：{WRITE_LIMIT_PER_DAY - write}次\n"
        f"益起读：{READ_LIMIT_PER_DAY - read}次\n益起猜：{TOPIC_LIMIT_PER_DAY - topic}次\n")
    try:
        if write >= WRITE_LIMIT_PER_DAY:
            print('今日益起写已完成答题，跳过答题，直接结束任务。\n')
        else:
            question_func(hours, write)
    except:
        print('执行"益起写"遇到错误: \n' + traceback.format_exc() + '\n')
        if str(input('输入"r"重试，输入任意字符退出程序（按下回车键)')) == 'r':
            question_func(hours, write)
        else:
            exit(0)

    print('\n开始执行益起读 朗读任务\n')

    try:
        if read >= READ_LIMIT_PER_DAY:
            print('今日益起读已完成答题，跳过答题，直接结束任务。\n')
        else:
            read_book_func(hours, read)
    except:
        print('执行"益起读"遇到错误: \n' + traceback.format_exc() + '\n')
        if str(input('输入"r"重试，输入任意字符退出程序（按下回车键)')) == 'r':
            question_func(hours, read)
        else:
            exit(0)

    print('\n开始执行益起猜任务\n')

    try:
        if topic >= TOPIC_LIMIT_PER_DAY:
            print('今日益起猜已完成答题，跳过答题，直接结束任务。\n')
        else:
            topic_func(hours)
    except:
        print('执行"益起猜"遇到错误: \n' + traceback.format_exc() + '\n')
        if str(input('输入"r"重试，输入任意字符退出程序（按下回车键)')) == 'r':
            topic_func(hours)
        else:
            exit(0)

    print('任务执行完毕，感谢使用\n')
    input("按下回车键退出程序...")


if '__main__' == __name__:
    try:
        main()
    except:
        print('程序运行出错: \n' + traceback.format_exc() + '\n')
        flag = str(input('输入"r"重试，输入任意字符退出程序（按下回车键)'))
        if flag == 'r':
            main()
        else:
            exit(0)
