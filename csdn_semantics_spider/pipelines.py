# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs

from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class JsonWithEncodingCsdnSemanticsPipeline(object):
    def __init__(self):
        self.file = codecs.open('csdn_semantics.json', 'w', encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
    def spider_closed(self, spider):
        self.file.close()

class MySQLStoreCsdnSemanticsPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
    
    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True,
        )        
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    #pipeline默认调用
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d    
    
        #将每行更新或写入数据库中
    def _do_upinsert(self, conn, item, spider): 
        linkmd5id = self._get_linkmd5id(item)
        #print linkmd5id
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        insertcmd="insert into csdn_semantics_info values('%s','%s','%s','%s', '%s') on duplicate key update title='%s', link='%s', description='%s', updated='%s'" % (linkmd5id, item['title'], item['link'],item['desc'], now, item['title'], item['link'],item['desc'], now)
        #insertcmd2="insert into csdn_semantics_info values('a38f286ce7b9257fb03ed14fd4c68587','使用java读取文件中的中文问题 - y22222ly的专栏 - 博客频道 - CSDN.NET','http://blog.csdn.net/y22222ly/article/details/38706193','使用java读取文件中的中文问题 - y22222ly的专栏        - 博客频道 - CSDN.NET', '2016-07-15 05:55:12') on duplicate key update title='使用java读取文件中的中文问题 - y22222ly的专栏        - 博客频道 - CSDN.NET', link='http://blog.csdn.net/y22222ly/article/details/38706193', description='使用java读取文件中的中文问题 - y22222ly的专栏        - 博客频道 - CSDN.NET', updated='2016-07-15 05:55:12';"

        #print(insertcmd2)
        conn.execute(insertcmd)
        
    #获取url的md5编码
    def _get_linkmd5id(self, item):
        #url进行md5处理，为避免重复采集设计
        return md5(item['link']).hexdigest()
    #异常处理
    def _handle_error(self, failue, item, spider):
        log.err(failure)
