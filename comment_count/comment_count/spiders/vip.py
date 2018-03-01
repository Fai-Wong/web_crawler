# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime
import json

class Vip(scrapy.Spider):
    name = "vip"
    # download_delay = 1
    def __init__(self, settings, top_num=None):
        
        self.key_words = settings['KEY_WORDS']
        self.batchno = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if top_num:
            self.top_num = top_num
        else:
            self.top_num = 20   #默认前20个商品
    
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)
    
    def start_requests(self):
        print(self.key_words)
        for kw in self.key_words:
            kw_code = request.quote(kw)   #utf8编码
            search_url = 'https://category.vip.com/suggest.php?keyword=%s' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        data = re.findall('\'suggestMerchandiseList\', (.*?)\);', response.text, re.S)[0]  #源码匹配商品json
        data = json.loads(data)
        flag = 0
        for item in data['products']:
            if flag < self.top_num:   #前20个商品
                datas = {}
                datas['srcsys'] = '唯品会'
                datas['batchno'] = self.batchno
                datas['key_word'] = response.meta['kw']
                datas['url'] =  'https://detail.vip.com/detail-%s-%s.html' % (item['brand_id'], item['product_id'])
                datas['title'] = re.sub(',|，', ' ', '%s %s' % (item['brand_store_name'], item['product_name']))
                print('发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                com_url = 'https://pcapi.vip.com/comment/getSumInfo.php?callback=getCommentSummaryCB&spuId=%s&catId=1' % item['v_spu_id']   #构造获取评论数的url
                flag += 1
                yield scrapy.http.Request(
                    url = com_url,
                    callback = self.parse_com_cont,
                    meta = {'datas': datas},
                    dont_filter = True
                )
            else:
                break
    def parse_com_cont(self, response):
        datas = response.meta['datas']
        datas['com_cnt'] = re.search('"total_count":(\d+)', response.text).group(1)
        print('评论数：' + datas['com_cnt'])
        yield datas

            
    