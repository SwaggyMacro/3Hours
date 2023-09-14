import json

import pymem
import win32gui
from pymem.exception import CouldNotOpenProcess
from win32process import GetWindowThreadProcessId


def enum_windows_callback(hwnd: int, hwnd_list: list):
    hwnd_list.append(hwnd)


HWND_LIST = []
win32gui.EnumWindows(enum_windows_callback, HWND_LIST)

T_HOURS_PIDS = []

MINIGRAM_TITLE = '人人3小时'


def is_minigram_running():
    for hwnd in HWND_LIST:
        title = win32gui.GetWindowText(hwnd)
        if MINIGRAM_TITLE in title:
            return True
    return False


def get_token_uuid_new():
    global T_HOURS_PIDS, HWND_LIST
    for hwnd in HWND_LIST:
        title = win32gui.GetWindowText(hwnd)
        if MINIGRAM_TITLE in title:
            # print(title, hwnd)
            T_HOURS_PIDS = GetWindowThreadProcessId(hwnd)
            break
    # print(T_HOURS_PIDS)
    if len(T_HOURS_PIDS) == 0:
        return None, None

    for pid in T_HOURS_PIDS:
        # print(pid)
        token = None
        uuid = None
        try:
            pm = pymem.Pymem(pid)
            # bytes_pattern = r'&env=production#sid='.encode('utf-8')
            bytes_pattern = r'requestHeaders'.encode('utf-8')
            character_count_address = pymem.pattern.pattern_scan_all(pm.process_handle, bytes_pattern,
                                                                     return_multiple=True)
            # print(character_count_address)
            for address in character_count_address:
                try:
                    text = pm.read_string(address, 600)
                    text = text.replace(" ", '').replace('\\', '')[text.find('requestHeaders":"') +
                                                                   17:text.find('","responseHeaders')]
                    # find the last }" and remove the rest
                    text = text[:text.rfind('}') + 1]

                    # print(text)

                    req_headers = json.loads(text)

                    # print(req_headers)

                    if "csr-uuid" in req_headers.keys() and "csr-token" in req_headers.keys():
                        uuid = req_headers["csr-uuid"]
                        token = req_headers["csr-token"]
                        break

                except:
                    continue

            return token is not None and token.strip() or None, uuid is not None and uuid.strip() or None

        except CouldNotOpenProcess as e:
            pass


def get_token_uuid():
    global T_HOURS_PIDS, HWND_LIST
    for hwnd in HWND_LIST:
        title = win32gui.GetWindowText(hwnd)
        if MINIGRAM_TITLE in title:
            # print(title, hwnd)
            T_HOURS_PIDS = GetWindowThreadProcessId(hwnd)
            break
    # print(T_HOURS_PIDS)
    if len(T_HOURS_PIDS) == 0:
        return None, None

    for pid in T_HOURS_PIDS:
        # print(pid)
        token = None
        uuid = None
        try:
            pm = pymem.Pymem(pid)
            bytes_pattern = 't{"data"'.encode('utf-8')

            character_count_address = pymem.pattern.pattern_scan_all(pm.process_handle, bytes_pattern,
                                                                     return_multiple=True)
            # print(character_count_address)
            for address in character_count_address:
                try:
                    token = pm.read_string(address, 80)
                except:
                    continue
                token = token[token.find('cacheData') + 12:token.find('expiration') - 3].replace('\\"', '')
                if token:
                    break

            # print('----------------')

            bytes_pattern = 'i{"data"'.encode('utf-8')
            character_count_address = pymem.pattern.pattern_scan_all(pm.process_handle, bytes_pattern,
                                                                     return_multiple=True)
            # print(character_count_address)
            try:
                for address in character_count_address:
                    try:
                        uuid = pm.read_string(address, 80)
                    except:
                        continue
                    uuid = uuid[uuid.find('cacheData') + 12:uuid.find('expiration') - 3].replace('\\"', '')
                    if uuid:
                        break
            except:
                uuid = None

            return token is not None and token.strip() or None, uuid is not None and uuid.strip() or None

        except CouldNotOpenProcess as e:
            pass
