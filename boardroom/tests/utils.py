import os
import urllib2

TEST_DIRECTORY = os.path.split(os.path.realpath(__file__))[0]


def internet_on():
    try:
        response=urllib2.urlopen('http://www.sec.gov/',timeout=1)
        return True
    except urllib2.URLError as err:
        pass
    return False
