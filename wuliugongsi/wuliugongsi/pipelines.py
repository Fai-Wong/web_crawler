# -*- coding: utf-8 -*-
import pymssql
from scrapy.conf import settings

class WuliugongsiPipeline(object):

    def __init__(self):
        self.conn = pymssql.connect(host=settings['HOST'], database=settings['DATABASE'], user=settings['USER'], password=settings['PASSWORD'])
        self.cur = self.conn.cursor()
        
    def process_item(self, item, spider):
        colums_str = ','.join(sorted(item.keys()))
        values_str = ','.join([repr(item[key]) for key in sorted(item.keys())])
        sql = "insert into %s(%s) values(%s)" % (spider.name, colums_str, values_str)
        self.cur.execute(sql)
        self.conn.commit()
        return item
        
    def process_close(self, spider):
        self.cur.close
        self.conn.close
        