from sep_spider.custom_settings import RELOAD_PATH, CUSTOM_FILES_STORE
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def reload():
    os.system('scrapy crawl sep_spider')
    try:
        os.system("chown -R ftpuser %s" % CUSTOM_FILES_STORE)
        os.system("chgrp -R ftpuser %s" % CUSTOM_FILES_STORE)
    except:
        pass


prev_reload_mtime = os.stat(RELOAD_PATH).st_mtime
while True:
    cur_mtime = os.stat(RELOAD_PATH).st_mtime
    if prev_reload_mtime != cur_mtime:
        print('reloading...')
        reload()
        print('finished')
        prev_reload_mtime = cur_mtime
    time.sleep(1)
