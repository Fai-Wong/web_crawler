# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime

class Tmall(scrapy.Spider):
    name = "tmall"
    download_delay = 1
    custom_settings = {
        'COOKIES_ENABLED': True
    }
    def __init__(self, settings, top_num=None):
        
        self.key_words = settings['KEY_WORDS']
        self.cookies = settings['COOKIES']
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
            kw_code = request.quote(kw.encode('gbk'))   #gbk编码
            search_url = 'https://list.tmall.com/search_product.htm?q=%s' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                cookies = self.cookies,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        flag = 0
        for li in response.xpath("//div[@id='J_ItemList']/div[@class='product  ']"):
            if flag < self.top_num:   #前20个商品
                id = li.xpath("./@data-id").extract()[0]
                datas = {}
                datas['srcsys'] = '天猫'
                datas['batchno'] = self.batchno
                datas['key_word'] = response.meta['kw']
                datas['url'] =  response.urljoin(li.xpath(".//*[@class='productTitle productTitle-spu' or @class='productTitle ' or @class='productTitle']/a/@href").extract()[0])
                datas['title'] = re.sub(',|，|\n', ' ', ''.join(li.xpath(".//*[@class='productTitle productTitle-spu' or @class='productTitle ' or @class='productTitle']//text()").extract())).strip()
                print('发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                com_url = 'https://rate.tmall.com/list_detail_rate.htm?sellerId=1&order=1&currentPage=1&itemId=%s' % id
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
        datas['com_cnt'] = re.search('"items":(\d+),',response.text).group(1)
        print('评论数：' + datas['com_cnt'])
        yield datas

            
    