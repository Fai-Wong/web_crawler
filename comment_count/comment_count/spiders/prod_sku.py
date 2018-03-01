# -*- coding:utf8 -*-
import codecs
import re
from urllib import request
import scrapy
import datetime
import json
from scrapy.conf import settings

class Taobao(scrapy.Spider):
    name = "prod_sku"
    download_delay = 1.1
    custom_settings = {
        'ITEM_PIPELINES':{
            # 'comment_count.pipelines.CommentCountPipeline': 300,
            'comment_count.pipelines.SkuPipeline': 310,
        }
    }
    
    def __init__(self, page_count=None):
        self.updatetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.pattern1 = re.compile(r'\"\"([^"]*?)\"\"')
        self.pattern2 = re.compile(r'\"(\[.*?\])\"')
        self.pattern3 = re.compile(r'\"(\{.*?\})\"')
        
    def start_requests(self):
        for line in open('prod_id.txt'):
            line = line.strip().split('\t')
            url = 'https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B"itemNumId"%3A"{}"%7D'.format(line[1]) #搜索入口
            # print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = url,
                callback = self.parse_content,
                meta = {'line': line}
            )
                
    def parse_content(self, response):
        line = response.meta['line']
        # with open('test1.txt','w',encoding='utf-8') as f:
            # f.write(repr(response.text))
        
        # with open('test2.txt','w',encoding='utf-8') as f:
            # f.write(response.text)
        try:
            data = json.loads(response.text)
        except Exception as e:
            print(e)
            # with open('test3.txt','w',encoding='utf-8') as f:
                # f.write(text)
            print('访问失败：%s %s' % (response.url,response.status))
            retryTime = response.meta.get('retryTime',0)
            if retryTime < 10:
                yield scrapy.http.Request(
                        url = response.url,
                        callback = self.parse_content,
                        meta = {
                            'line':line, 
                            'retry':True,
                            'retryTime':retryTime+1
                        },
                        dont_filter = True
                    )
            else:
                with open('err_url.txt','a',encoding='utf-8') as f:
                    f.write(str(line)+'\n')
                raise e
        else:
            # with open('test4.txt','w',encoding='utf-8') as f:
                # f.write(text)
            # if response.meta.get('retry',False):
                # print('重试成功')
            # print('parse_content:', response.url)
            # for item in data['mods']['itemlist']['data']['auctions']:
            
            datas = {}
            datas['updatetime'] = self.updatetime
            datas['商品ID'] = line[1]
            datas['flag'] = line[0]
            datas['成交量'] = line[2]
            datas['关键词'] = line[3]
            try:
                esi = data['data']['apiStack'][0]['value'].replace('\\','')
            except Exception as e:
                # with open('err_url.txt','a',encoding='utf-8') as f:
                    # f.write(response.url+'\n')
                # print(e)
                print('访问太频繁或者商品不存在：%s %s' % (response.url,response.status))
                retryTime = response.meta.get('retryTime',0)
                if retryTime < 10:
                    yield scrapy.http.Request(
                            url = response.url,
                            callback = self.parse_content,
                            meta = {
                                'line':line, 
                                'retry':True,
                                'retryTime':retryTime+1
                            },
                            dont_filter = True
                        )
                else:
                    with open('err_url.txt','a',encoding='utf-8') as f:
                        f.write(str(line)+'\n')
                    raise e
            else:
                try:
                    if response.meta.get('retry',False):
                        print('重试成功')
                    print('parse_content:', response.url)
                    esi = self.pattern1.sub(r'\"\1\"',esi)
                    esi = self.pattern2.sub(r'\1',esi)
                    esi = self.pattern3.sub(r'\1',esi)
                    esi = json.loads(esi)
                    datas['发货地址'] = esi['delivery'].get('from','')
                    datas['邮费'] = re.sub('[快递免运费包邮：:元]','',esi['delivery']['postage'])
                    datas['价格'] = esi['price']['price']['priceText']
                    try:
                        datas['原价'] = esi['price']['extraPrices'][0]['priceText']
                    except:
                        datas['原价'] = ''
                    datas['库存'] = esi['skuCore']['sku2info']['0']['quantity']
                    datas['商品链接URL'] = 'https://item.taobao.com/item.htm?id=' + datas['商品ID']
                    item = data['data']['item']
                    datas['商品名称'] = item['title']
                    datas['月销量'] = item.get('sellCount',esi['item']['sellCount'])
                    try:
                        datas['商品描述'] = item['subtitle']
                    except:
                        datas['商品描述'] = ''
                    datas['商品分类ID'] = item['categoryId']
                    datas['累计评论数'] = item['commentCount']
                    datas['收藏数'] = item['favcount']
                    try:
                        datas['基本信息'] = data['data']['props']['groupProps'][0]['基本信息']
                    except:
                        datas['基本信息'] = []
                    datas['店铺ID'] = data['data']['seller']['userId']
                    datas['店铺名称'] = data['data']['seller'].get('shopName','')
                    
                    yield datas
                except:
                    with open('err_url.txt','a',encoding='utf-8') as f:
                        f.write(str(line)+'\n')
            
            
    