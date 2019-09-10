# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline
from sep_spider.settings import FILES_STORE, CONVERT_FORMAT_LIST
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
import os
import re


class SepFilesPipeline(FilesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            if not ok:
                print("Error get: " + item['url'])
                continue

            # move file
            new_path = os.path.join(FILES_STORE, item['file_path'])
            if not os.path.exists(new_path):
                os.popen('mkdir -p "%s"' % new_path)
            old_path = os.path.join(FILES_STORE, value['path'])
            new_path = os.path.join(new_path, item['name'])
            os.popen('mv "%s" "%s"' % (old_path, new_path))

            # convert office to pdf
            # re_groups = re.match(r"^(.*)\.(.*)$", new_path).groups()
            # if len(re_groups) > 1 and re_groups[1] in CONVERT_FORMAT_LIST:
            #     os.popen('unoconv -f pdf "%s"' % new_path)


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8mb4',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        # insert_sql, params = item.fix_date_sql()
        cursor.execute(insert_sql, params)

