import os

import urllib3

from Utils.Other import get_config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERIFY_SSL = False
USE_OPENAI_API = get_config('use_openai')

if USE_OPENAI_API:
    # set proxy for openai API
    os.environ["HTTP_PROXY"] = get_config('http_proxy')
    os.environ["HTTPS_PROXY"] = get_config('https_proxy')
