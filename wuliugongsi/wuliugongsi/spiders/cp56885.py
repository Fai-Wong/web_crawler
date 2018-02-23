# -*- coding:utf-8 -*-
import scrapy
import re

class Haoyun56(scrapy.Spider):
    name = 'cp56885'
    
    def start_requests(self):
        yield scrapy.http.Request(
            url = 'http://www.56885.net/yuanqu/?0_0_0_0_1.html',
            callback = self.parse_list
        )
        
    def parse_list(self, response):
        print('parse_list:', response.url, response.status)
        for company_url in response.xpath("//ul[@class='tywlist']/li[2]/h3/a/@href").extract():
            yield scrapy.http.Request(
                url = response.urljoin(company_url),
                callback = self.parse_info
            )
        if response.xpath("//div[@class='manu']/a[not(contains(text(),'>>')) and contains(text(),'>')]"):
            yield scrapy.http.Request(
                url = response.urljoin(response.xpath("//div[@class='manu']/a[not(contains(text(),'>>')) and contains(text(),'>')]/@href").extract()[0]),
                callback = self.parse_list
            )     
        
    def parse_info(self, response):
        print('parse_info:', response.url, response.status)
        datas = {'evaluete':'','authentication':'','phone':'','fax':'','wechat':'','email':'',}
        datas['line'] = ''.join(response.xpath("//div[contains(div/text(),'经营路线')]/div[@class='nycontent']/text()").extract())
        datas['introdution'] = re.sub('\s','',''.join(response.xpath("//div[contains(div/text(),'公司介绍')]/div[@class='nycontent']//text()").extract()))
        datas['market'] = ''.join(response.xpath("//ul[@class='zxlists']/li[contains(span/text(),'市场')]/text()").extract())
        if response.xpath("//ul[@class='cxlist']"):
            temp_evaluate = response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'总评')]/em/em/@style").extract()[0]
            
            datas['evaluete'] = str(int(re.findall('width\:(\d+)px',temp_evaluate)[0]) // 20) + ' star'
            datas['name'] = response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'名称')]/text()").extract()[0].strip()
            datas['authentication'] = ';'.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'认证')]//em/@title").extract())
            datas['principal'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'联 系 人')]/text()").extract())
            datas['phone'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'手机')]/text()").extract())
            datas['tel'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'电话')]/text()").extract())
            datas['fax'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'传真')]/text()").extract())
            datas['wechat'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'微信')]/text()").extract())
            datas['email'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'邮箱')]/text()").extract())
            datas['location'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'地区')]/text()").extract())
            datas['address'] = ''.join(response.xpath("//ul[@class='cxlist']/li[contains(span/text(),'地址')]/text()").extract())
        else:
            datas['name'] = ''.join(response.xpath("//ul[@class='zxlists']/li[contains(span/text(),'名称')]/text()").extract())
            datas['location'] = ''.join(response.xpath("//ul[@class='zxlists']/li[contains(span/text(),'省市')]/text()").extract())
            datas['principal'] = ''.join(response.xpath("//ul[@class='zxlists']/li[contains(span/text(),'联 系 人')]/text()").extract())
            datas['tel'] = ''.join(response.xpath("//ul[@class='zxlists']/li[contains(span/text(),'电话')]/text()").extract())
            datas['address'] = ''.join(response.xpath("//ul[@class='zxlists']/li[contains(span/text(),'地址')]/text()").extract())
        yield(datas)

  
    
    
    
    
    