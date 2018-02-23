# -*- coding:utf-8 -*-
import scrapy
import re

class Haoyun56(scrapy.Spider):
    name = 'zghy'
    line_property = {'keyboard_d2':'单向', 'keyboard':'双向'}
    
    def start_requests(self):
        yield scrapy.http.Request(
            url = 'http://www.zghy.com/Page/index.aspx?page=1',
            callback = self.parse_list
        )
        
    def parse_list(self, response):
        print('parse_list:', response.url, response.status)
        for company_url in response.xpath("//div[@class='List_ItemList']//li[@class='Title']//a/@href").extract():
            yield scrapy.http.Request(
                url = response.urljoin(company_url),
                callback = self.parse_info
            )
        nextpage = response.xpath("//div[@id='ctl00_ContentPlaceHolder1_CarListPager']/div/a[not(contains(text(),'>>')) and contains(text(),'>')]/@href")
        if nextpage:
            yield scrapy.http.Request(
                url = response.urljoin(nextpage.extract()[0]),
                callback = self.parse_list
            )     
        
    def parse_info(self, response):
        print('parse_info:', response.url, response.status)
        datas = {}
        datas['introdution'] = ''.join(response.xpath("//span[@id='ctl00_ContentPlaceHolder1_lbIntro']/text()").extract())
        datas['name'] = response.xpath("//span[@id='ctl00_ContentPlaceHolder1_lbETName1']/text()").extract()[0].strip()
        datas['principal'] = ''.join(response.xpath("//td[contains(b/text(),'联系人')]/span/text()").extract())
        datas['phone'] = ''.join(response.xpath("//td[contains(b/text(),'手机')]/span/text()").extract())
        datas['tel'] = ''.join(response.xpath("//td[contains(b/text(),'电话')]/span/text()").extract())
        datas['fax'] = ''.join(response.xpath("//td[contains(b/text(),'传真')]/span/text()").extract())
        datas['address'] = ''.join(response.xpath("//td[contains(b/text(),'地址')]/span/text()").extract())
        id = response.url.split('=')[-1]
        yield scrapy.http.Request(
            url = 'http://www.zghy.com/Page/company/line.aspx?id=' + id,
            callback = self.parse_line,
            meta = {'datas':datas}
        )
    
    def parse_line(self, response):
        print('parse_line:', response.url, response.status)
        datas = response.meta['datas']
        line_list = []

        for tr in response.xpath("//table[@class='bottom_line']/tr"):
            temp_line_loc = tr.xpath(".//td[1]/a[1]//text()").extract()
            line_loc = [i.strip() for i in temp_line_loc if i.strip()]
            line_img = tr.xpath(".//td[1]/a[1]/img/@src").extract()[0]
            line_prop = self.line_property[re.findall('/(key.*?)\.gif',line_img)[0]]
            line_loc.append(line_prop)
            line = '%s-%s(%s)' % (tuple(line_loc))
            line_list.append(line)
            
        datas['line'] = ';'.join(line_list)
        yield(datas)
        
  
    
    
    
    
    