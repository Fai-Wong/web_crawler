# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime
import json
from scrapy.conf import settings

class Taobao(scrapy.Spider):
    name = "taobao_test1"
    download_delay = 1
    
    def __init__(self, page_count=None, *args, **kwargs):
        super(Taobao, self).__init__(*args, **kwargs)
        # self.key_words = settings['KEY_WORDS']
        self.flag = 0
        self.updatetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if page_count:
            self.page_count = page_count
        else:
            self.page_count = 10
    
    def start_requests(self):
        # print(self.key_words)
        
        for kw in open('key_words.txt'):
            kw = kw.strip()
            for i in range(self.page_count):
                search_url = 'https://s.taobao.com/search?q=%s&bcoffset=4&s=%d&sort=sale-desc&cat=50106154' % (request.quote(kw), i*44) #搜索入口
                print(u'开始搜索' + kw)
                yield scrapy.http.Request(
                    url = search_url,
                    callback = self.parse_list,
                    meta = {'kw': kw}
                )
            # break
        # yield scrapy.http.Request(
                    # url = 'https://s.taobao.com/search?q=%E6%AD%A3%E6%B0%94&bcoffset=4&s=264&sort=sale-desc',
                    # callback = self.parse_list,
                    # meta = {'kw': '正气'}
                # )
    def parse_list(self, response):
        if re.findall('g_page_config\s?=\s?({.*?});', response.text):
            data = re.findall('g_page_config\s?=\s?({.*?});', response.text)[0]  #源码匹配商品json
            data = json.loads(data) #json转字典
            print('parse_list:', response.url, '发现有%s项' % len(data['mods']['itemlist']['data']['auctions']))
            for item in data['mods']['itemlist']['data']['auctions']:
                datas = {}
                # print(type(item['shopcard']['isTmall']))
                datas['来源'] = {True:'天猫',False:'淘宝'}[\
                                    item['shopcard']['isTmall']]
                datas['updatetime'] = self.updatetime
                datas['关键词'] = response.meta['kw']
                datas['url'] =  response.urljoin(item['detail_url'])
                datas['标题'] = item['raw_title']
                datas['价格'] = item['view_price']
                datas['地址'] = item['item_loc']
                try:
                    datas['销量'] = item['view_sales']
                except:
                    datas['销量'] = ''
                datas['评论数'] = item['comment_count']
                datas['卖家'] = item['nick']
                datas['物流评分'] = int(str(item['shopcard']['delivery'][0])[:2])/10
                datas['描述评分'] = int(str(item['shopcard']['description'][0])[:2])/10
                datas['服务评分'] = int(str(item['shopcard']['service'][0])[:2])/10
                # datas['信用'] = item['shopcard']['sellerCredit']
                datas['店铺url'] = response.urljoin(item['shopLink'])
                
                sellerCredit = item['shopcard']['sellerCredit']
                if sellerCredit > 15:
                    datas['信用'] = str(sellerCredit - 15) + '金冠'
                elif sellerCredit > 10:
                    datas['信用'] = str(sellerCredit - 10) + '皇冠'
                elif sellerCredit > 5:
                    datas['信用'] = str(sellerCredit - 5) + '钻'
                else:
                    datas['信用'] = str(sellerCredit) + '心'
                yield datas
            else:
                print('正则匹配失败：%s' % response.url)
                yield scrapy.http.Request(
                    url = response.url,
                    callback = self.parse_list,
                    meta = {'kw':response.meta['kw']}
                )
            
            
            
    