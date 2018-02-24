# -*- coding:utf-8 -*-
import datetime
import time
import json
import re 
import scrapy 
from scrapy.http import Request,FormRequest

class Bluemc(scrapy.Spider):
    name = 'top10ZW'
    
    def __init__(self):
        self.updatetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        
    def start_requests(self):
        for line in open('user_id.txt'):
            line = line.strip().split()
            yield Request(
                url = 'http://www.bluemc.cn/_billBoard/publicNo/getPost.show?urn=3136949-{}&typeTop10=CNTREAD'.format(line[1]),
                callback = self.parse_post,
                meta = {'line':line}
            )
    def parse_post(self, response):
        print('parse_post:', response.url, response.status)
        line = response.meta['line']
        jsondata = json.loads(response.text)
        if jsondata['data']:
            for info in jsondata['data']:
                datas = {}
                datas['updatetime'] = self.updatetime
                datas['postId'] = info['postId']
                datas['postUrl'] = info['postUrl']
                datas['postdate'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(info['createdAt']/1000))
                datas['name'] = line[0]
                datas['userId'] = line[1]
                datas['title'] = info['title']
                datas['cntRead'] = info['cntRead']
                datas['cntLikes'] = info['cntLikes']
                yield Request(
                    url = datas['postUrl'],
                    callback = self.parse_content,
                    meta = {'datas':datas}
                )
    def parse_content(self, response):
        print('parse_post:', response.url, response.status)
        datas = response.meta['datas']
        datas['content'] = re.sub('\s+','',''.join(response.xpath("//div[@id='js_content']//text()").extract()))
        yield datas
        
        
        
        
        
        
        
        
        
        
        
        
        
        