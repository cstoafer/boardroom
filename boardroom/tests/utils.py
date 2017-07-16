import os
import requests

TEST_DIRECTORY = os.path.split(os.path.realpath(__file__))[0]


def internet_on():
    try:
        response = requests.get('http://www.sec.gov/', timeout=1)
        if response.status_code == 200:
            return True
    except:
        pass
    return False
