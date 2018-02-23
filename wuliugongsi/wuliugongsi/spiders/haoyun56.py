# -*- coding:utf-8 -*-
import scrapy
import re

class Haoyun56(scrapy.Spider):
    name = 'haoyun56'
    line_property = {'lineone':'单向', 'linetwo':'双向'}
    
    def start_requests(self):
        yield scrapy.http.Request(
            url = 'http://www.haoyun56.com/company/',
            callback = self.parse_list
        )
        
    def parse_list(self, response):
        print('parse_list:', response.url, response.status)
        for company_url in response.xpath("//tr[@style='padding-top: 6px;']/td/a/@href").extract():
            yield scrapy.http.Request(
                url = company_url,
                callback = self.parse_urls
            )
        if response.xpath("//a[contains(text(),'下一页')]/@href"):
            yield scrapy.http.Request(
                url = response.urljoin(response.xpath("//a[contains(text(),'下一页')]/@href").extract()[0]),
                callback = self.parse_list
            )
            
    def parse_urls(self, response):
        print('parse_urls:', response.url, response.status)
        details_url = response.xpath("//div/a[@class='red']/@href").extract()[0]
        try:
            line_url = response.xpath("//div[@id='ctl05_div_line']//a[@class='black_no']/@href").extract()[0]
        except Exception as e:
            line_url = ''
            print(e)
        yield scrapy.http.Request(
            url = details_url,
            callback = self.parse_info,
            meta = {'line_url':line_url}
        )
        
    def parse_info(self, response):
        print('parse_info:', response.url, response.status)
        datas = {}
        datas['line'] = ''
        datas['introdution'] = re.sub('\s|\\xa0','',''.join(response.xpath("//div[@class='content2_2']//text()").extract()))
        datas['type'] = response.xpath("//tr[contains(td/text(),'类别')]/td[2]/text()").extract()[0].strip()
        datas['name'] = response.xpath("//tr[contains(td/text(),'名称')]/td[2]/text()").extract()[0].strip()
        datas['main'] = response.xpath("//tr[contains(td/text(),'业务')]/td[2]/text()").extract()[0].strip()
        datas['scope'] = re.sub('\s|\\u3000','',response.xpath("//tr[contains(td/text(),'范围')]/td[2]/text()").extract()[0]).strip()
        datas['principal'] = response.xpath("//tr[contains(td/text(),'负责人')]/td[2]/text()").extract()[0].strip()
        datas['datetime'] = response.xpath("//tr[contains(td/text(),'时间')]/td[2]/text()").extract()[0].strip()
        datas['num_people'] = response.xpath("//tr[contains(td/text(),'人数')]/td[2]/text()").extract()[0].strip()
        datas['property'] = response.xpath("//tr[contains(td/text(),'性质')]/td[2]/text()").extract()[0].strip()
        datas['register'] = response.xpath("//tr[contains(td/text(),'登记')]/td[2]/text()").extract()[0].strip()
        datas['capital'] = response.xpath("//tr[contains(td/text(),'资本')]/td[2]/text()").extract()[0].strip()
        datas['account'] = response.xpath("//tr[contains(td/text(),'开户行')]/td[2]/text()").extract()[0].strip()
        datas['business_num'] = response.xpath("//tr[contains(td/text(),'工商')]/td[2]/text()").extract()[0].strip()
        datas['taxation_num'] = response.xpath("//tr[contains(td/text(),'税务')]/td[2]/text()").extract()[0].strip()
        datas['tel'] = response.xpath("//tr[contains(td/text(),'电话')]/td[2]/text()").extract()[0].strip()
        datas['fax'] = response.xpath("//tr[contains(td/text(),'传真')]/td[2]/text()").extract()[0].strip()
        datas['postalcode'] = response.xpath("//tr[contains(td/text(),'邮编')]/td[2]/text()").extract()[0].strip()
        datas['location'] = response.xpath("//tr[contains(td/text(),'所在地')]/td[2]/text()").extract()[0].strip()
        datas['address'] = response.xpath("//tr[contains(td/text(),'地址')]/td[2]/text()").extract()[0].strip()
        datas['main_page'] = response.xpath("//tr[contains(td/text(),'主页')]/td[2]/a/@href").extract()[0].strip()
        
        if response.meta['line_url']:
            yield scrapy.http.Request(
                url = response.meta['line_url'],
                callback = self.parse_line,
                meta = {'datas':datas}
            )
        else:
            yield(datas)
    
    def parse_line(self, response):
        print('parse_line:', response.url, response.status)
        datas = response.meta['datas']
        line_list = []
        for td in response.xpath("//table[@id='ctl05_rptList']//td"):
            if td.xpath(".//a"):
                line_loc = td.xpath(".//a//text()").extract()
                line_img = td.xpath(".//a/img/@src").extract()[0]
                line_prop = self.line_property[re.findall('/(line.*?)\.gif', line_img)[0]]
                line_loc.append(line_prop)
                line = '%s-%s(%s)' % (tuple(line_loc))
                line_list.append(line)
        datas['line'] += ';'.join(line_list)
        if response.xpath("//a[contains(text(),'下一页')]/@href"):
            yield scrapy.http.Request(
                url = response.xpath("//a[contains(text(),'下一页')]/@href").extract()[0],
                callback = self.parse_line,
                meta = {'datas':datas}
            )
        else:
            yield(datas)
    
    
    
    
    