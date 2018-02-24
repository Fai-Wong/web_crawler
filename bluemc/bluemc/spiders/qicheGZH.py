# -*- coding:utf-8 -*-
import datetime
import json
import re 
import scrapy 
from scrapy.http import Request,FormRequest

class Bluemc(scrapy.Spider):
    name = 'qicheGZH'
    
    def __init__(self):
        self.updatetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.cookies = {
            'Hm_lvt_7661f5a78a72e3a4e7aab72d9b7fb6d9':'1508999597,1509505837',
            'gr_user_id':'c5180bda-8d2d-4c6d-a4ce-79980da8fa7a',
            'route':'b1c603b22ed83eebf3a877f3114fddf7',
            'JSESSIONID':'D75F49A52654F94CCBC057874280BA7E',
            'JSESSIONID':'D75F49A52654F94CCBC057874280BA7E',
            'Hm_lpvt_7661f5a78a72e3a4e7aab72d9b7fb6d9':'1509508225',
            'PORTAL_LOGIN_NAME':'17130845058',
            'PORTAL_LOGIN_PWD':'432a606dbb3690850085005d3f9390a7',
            'bvc_having_login_user':'"Wed Nov 01 11:11:10 CST 2017"'
        }
        self.urls = [
        'http://www.bluemc.cn/wechat_pn_search/searchList.do?page=0&size=1000&sort=bwi%2CDESC&allClass=%2C&queryParam=%7B%22scope%22%3A%5B%22screenName%22%2C%22userUrn%22%5D%2C%22class%22%3A%5B3%2C4%2C6%2C5%2C79%5D%2C%22filter%22%3A%7B%7D%7D',
        'http://www.bluemc.cn/wechat_pn_search/searchList.do?page=0&size=1000&sort=bwi%2CDESC&allClass=%2C&queryParam=%7B%22scope%22%3A%5B%22screenName%22%2C%22userUrn%22%5D%2C%22class%22%3A%5B80%2C84%2C81%2C82%2C83%5D%2C%22filter%22%3A%7B%7D%7D',
        ]
        
    def start_requests(self):
        for line in open('urls.txt'):
            line = line.strip().split(',')
            yield Request(
                url = line[1],
                callback = self.parse_content,
                cookies = self.cookies,
                meta = {'classify':line[0]}
            )
    def parse_content(self, response):
        print('parse_content:', response.url, response.status)
        classify = response.meta['classify']
        jsondata = json.loads(response.text)
        if jsondata['data']:
            typeRanking = jsondata['typeRanking']
            for info in jsondata['data']:
                datas = {}
                datas['updatetime'] = self.updatetime
                datas['类别'] = classify
                datas['name'] = info['screenName']
                datas['userId'] = info['userId']
                datas['粉丝'] = info['userVisits']
                datas['头条阅读数'] = info['headLinein1ReadMedia']
                datas['次条条阅读数'] = info['headLinein2ReadMedia']
                datas['3~N条阅读数'] = info['headLinein3ReadMedia']
                datas['最高阅读数'] = info['allMaxReadNum']
                datas['头条点赞数'] = info['headLinein1LikeMedia']
                datas['次条点赞数'] = info['headLinein2LikeMedia']
                datas['3~N条点赞数'] = info['headLinein3LikeMedia']
                datas['最高点赞数'] = info['headLinein1MaxLike']
                datas['10W+文章'] = info['allMoreThan10W']
                datas['发布文章'] = info['cntMonthPosts']
                datas['发布次数'] = info['cntMonthTimes']
                datas['BW指数'] = info['bwi']
                userUrn = info['userUrn']
                ranking = []
                for rank in eval(typeRanking[userUrn]):
                   ranking.append('%s:%s' % (rank['rankName'],rank['rangValue']))
                datas['分类排名'] = ','.join(ranking)
                yield datas
            
