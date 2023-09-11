import os

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERIFY_SSL = False
USE_OPENAI_API = True

if USE_OPENAI_API:
    # set proxy for openai API
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:10801"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10801"