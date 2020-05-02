# -*- coding: utf-8 -*-
import scrapy
from PIL import Image
from scrapy.http import Request
from scrapy import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from sep_spider.settings import FILES_STORE, GEOKO_PATH, IGNORE_LIST
from sep_spider.custom_settings import SEP_PASSWD, SEP_USER, YDM_INFO
from sep_spider.items import SepItemLoader, SepItem
from sep_spider.utils.yundama_demo import YDMHttp
from urllib.parse import unquote
import time
import os
import re
# import pdb

PENDING_TIME = 3


def checker(foo1, foo2=None, max_retry=20):
    retry = 0
    while True:
        if retry > max_retry:
            return None
        try:
            return foo1()
        except NoSuchElementException:
            time.sleep(PENDING_TIME)
            retry += 1
        except ElementNotInteractableException:
            foo2()
        except Exception as e:
            raise e


class SepSpider(scrapy.Spider):
    name = 'sep_spider'
    allowed_domains = [
        'sep.ucas.com',
        'course.ucas.ac.cn'
    ]
    start_urls = ['http://sep.ucas.ac.cn/']
    downloaded = []

    def __init__(self, name=None, **kwargs):
        options = webdriver.FirefoxOptions()
        options.set_headless()
        options.add_argument('--disable - gpu')

        self.browser = webdriver.Firefox(
            executable_path=GEOKO_PATH,
            options=options
        )
        self.ydm_api = YDMHttp(**YDM_INFO)
        super(SepSpider, self).__init__(name, **kwargs)

    def parse(self, response):
        name = response.css('.Mrphs-hierarchy--siteName > a:nth-child(1)::text').extract_first('')
        print(response.url, name)
        res_url = response.css('a[title="资源 - 上传、下载课件，发布文档，网址等信息"]::attr(href)').extract_first('')
        yield Request(res_url, callback=self.parse_course, meta={'page_type': 'res', 'course_name': name})

    def parse_course(self, response):
        # if response.meta.get('course_name') == '大学英语IV19-20秋季':
        #     pass
        # else:
        #     return

        file_path = [response.meta.get('course_name')]
        print('course: ', file_path[0])
        for each in response.css('#showForm>table>tbody>tr>.specialLink>a:nth-of-type(2)'):
            print(file_path)

            re_obj = re.match('.*([0-9])em', each.xpath('../@style').extract_first(''))
            depth = int(re_obj.group(1)) if len(re_obj.groups()) > 0 else 1
            while depth < len(file_path):
                file_path.pop()

            if each.css('::attr(title)').extract_first('') == '文件夹':
                dir_name = each.css('span:nth-of-type(1)::text').extract_first('')
                print('folder: ', dir_name)
                file_path.append(dir_name)
            else:
                file_url = each.css('::attr(href)').extract_first('')
                # process copyright alert
                if file_url == '#':
                    continue
                
                file_name = unquote(re.match('.*/(.*)$', file_url).group(1))
                print('file: ', file_name)

                if not os.path.exists(os.path.join(FILES_STORE, *tuple(file_path), file_name)):
                    if file_name in IGNORE_LIST:
                        print('ignore: ', file_name)
                        continue

                    print(os.path.join(FILES_STORE, *tuple(file_path), file_name))
                    loader = SepItemLoader(item=SepItem(), response=response)
                    loader.add_value('url', response.url)
                    loader.add_value('file_url', file_url)
                    loader.add_value('name', file_name)
                    file_path_str = os.path.join(*tuple(file_path))
                    loader.add_value('file_path', file_path_str)

                    self.downloaded.append(os.path.join(file_path_str, file_name))
                    item = loader.load_item()
                    yield item
        pass

    def start_requests(self):
        return self.sep_login()

    def sep_login(self):
        self.browser.get('http://sep.ucas.ac.cn')
        # print(browser.page_source)
        # t_selector = Selector(text=browser.page_source)

        self.browser.maximize_window()
        self.browser.find_element_by_css_selector('#userName').send_keys(SEP_USER)
        self.browser.find_element_by_css_selector('#pwd').send_keys(SEP_PASSWD)

        try:
            element = self.browser.find_element_by_id('code')
            left = int(element.location['x'])
            top = int(element.location['y'])
            right = int(element.location['x'] + element.size['width'])
            bottom = int(element.location['y'] + element.size['height'])

            self.browser.get_screenshot_as_file('screenshot.png')
            im = Image.open('screenshot.png')
            im = im.crop((left, top, right, bottom))
            im.save('code.png')

            self.ydm_api.login()
            _, cert_code = self.ydm_api.decode('code.png', 1004, 60)
            print('cert_code=', cert_code)
            self.browser.find_element_by_name('certCode').send_keys(cert_code)
        except Exception as e:
            print(e)
            pass

        self.browser.find_element_by_id('sb').click()
        checker(lambda: self.browser.find_element_by_css_selector('a[data-blackname="16"]').click())
        checker(lambda: self.browser.find_element_by_css_selector('a[title="我的课程 - 查看或加入站点"]').click(),
                lambda: self.browser.find_element_by_class_name('js-toggle-tools-nav').click())

        cookies = self.browser.get_cookies()
        print(cookies)

        all_urls = []
        while True:
            t_selector = Selector(text=self.browser.page_source)
            all_urls += t_selector.css("#membership > tbody:nth-child(2) tr th a::attr(href)").extract()

            nxt_btn = checker(lambda: self.browser.find_element_by_name('eventSubmit_doList_next'))
            print(nxt_btn.get_attribute("disabled"))

            if nxt_btn.get_attribute("disabled") == "true":
                break
            nxt_btn.click()
            time.sleep(PENDING_TIME)

        # test_url = 'http://course.ucas.ac.cn/portal/site/156690'
        # yield Request(url=test_url, cookies=self.browser.get_cookies(), dont_filter=True)
        # return

        for each in all_urls:
            yield Request(url=each, cookies=self.browser.get_cookies(), dont_filter=True)

    def __del__(self):
        # with open(LOG_PATH, 'w') as f:
        #     for cnt, name in enumerate(self.downloaded, 1):
        #         line = "%s: %s\n" % (cnt, name)
        #         f.write(line)
        #         print(line, end='')

        self.browser.quit()
