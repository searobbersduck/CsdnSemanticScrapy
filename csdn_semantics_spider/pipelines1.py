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
    def __init__(self, conn):
        self.conn = conn
    
    @classmethod
    def from_settings(cls, settings):
        conn=MySQLdb.connect(host='localhost',user='root',passwd='123456',port=3306)
        cur=conn.cursor()
        cur.execute('create database if not exists csdn_semantics_db default character set utf8 collate utf8_general_ci')
        conn.select_db('csdn_semantics_db')
        cur.execute('create table if not exists csdn_semantics_info(linkmd5id char(32) NOT NULL, title text, link text, description text, updated datetime DEFAULT NULL, primary key(linkmd5id)) ENGINE=MyISAM DEFAULT CHARSET=utf8')
        conn.commit()
        cur.close()
        return cls(conn)

    #pipeline默认调用
    def process_item(self, item, spider):
        linkmd5id = self._get_linkmd5id(item)
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
        cur=self.conn.cursor()
        insertcmd="insert into csdn_semantics_info values('%s','%s','%s','%s', '%s') on duplicate key update title='%s', link='%s', description='%s', updated='%s'"%(linkmd5id, item['title'].encode('utf8'), item['link'].encode('utf8'),item['desc'].encode('utf8'), now, item['title'].encode('utf8'), item['link'].encode('utf8'),item['desc'].encode('utf8'), now)
        insertcmd1='insert into csdn_semantics_info values("%s","%s","%s","%s", "%s") on duplicate key update title="%s", link="%s", description="%s", updated="%s"'%(linkmd5id, item['title'].encode('utf8'), item['link'].encode('utf8'),item['desc'].encode('utf8'), now, item['title'].encode('utf8'), item['link'].encode('utf8'),item['desc'].encode('utf8'), now)
        insertcmd2="insert into csdn_semantics_info values('a38f286ce7b9257fb03ed14fd4c68587','使用java读取文件中的中文问题 - y22222ly的专栏 - 博客频道 - CSDN.NET','http://blog.csdn.net/y22222ly/article/details/38706193','使用java读取文件中的中文问题 - y22222ly的专栏        - 博客频道 - CSDN.NET', '2016-07-15 05:55:12') on duplicate key update title='使用java读取文件中的中文问题 - y22222ly的专栏        - 博客频道 - CSDN.NET', link='http://blog.csdn.net/y22222ly/article/details/38706193', description='使用java读取文件中的中文问题 - y22222ly的专栏        - 博客频道 - CSDN.NET', updated='2016-07-15 05:55:12';"
        print(insertcmd)
	cur.execute(insertcmd2)
        #cur.execute("insert into csdn_semantics_info values(%s,%s,%s,%s,%s) on duplicate key update title=%s, link=%s, description=%s, updated=%s", 
         #           (linkmd5id, item['title'], item['link'],item['desc'], now, item['title'], item['link'],item['desc'], now))
        
        self.conn.commit()
        cur.close()
    #获取url的md5编码
    def _get_linkmd5id(self, item):
        #url进行md5处理，为避免重复采集设计
        return md5(item['link']).hexdigest()
