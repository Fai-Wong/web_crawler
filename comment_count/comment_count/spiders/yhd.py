# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime

class Yhd(scrapy.Spider):
    name = "yhd"
    
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
            search_url = 'http://search.yhd.com/c0-0/k%s' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        datas = {}
        datas['srcsys'] = '一号店'
        datas['batchno'] = self.batchno
        datas['key_word'] = response.meta['kw']
        flag = 0
        for li in response.xpath("//div[@id='itemSearchList']/div[@class='mod_search_pro']"):
            if flag < self.top_num:   #前20个商品
                datas['title'] = re.sub('\u2022|\xa0|\n|\r|,|，', ' ', ''.join(li.xpath(".//p[@class='proName clearfix' or @class='proName bookName clearfix']/a[1]/text()").extract())).strip()
                # print(title)
                datas['url'] = response.urljoin(li.xpath(".//p[@class='proName clearfix' or @class='proName bookName clearfix']/a[1]/@href").extract()[0])
                print(u'发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                try:
                    datas['com_cnt'] = li.xpath(".//p/span[@class='comment']/a/text()").extract()[1]
                except:
                    datas['com_cnt'] = '0'
                print(u'评论数:' + datas['com_cnt'])
                flag += 1
                
                yield datas
                # print(datas)
            else:
                break

            
    