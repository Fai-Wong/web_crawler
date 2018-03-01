# -*- coding: utf-8 -*-

import pymssql
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.conf import settings
import re


class ProxyMiddleware(object):
    def __init__(self):
        self.conn=pymssql.connect(host=settings['MSSQL_HOST'],database=settings['MSSQL_DB_DOWN_DEV'],user=settings['MSSQL_USER'],password=settings['MSSQL_PWD'],charset="UTF-8")
        self.cur=self.conn.cursor()
        self.proxy = self._get_ip()
        
    def process_request(self, request, spider):
        if self.proxy:
            request.meta['proxy'] = "http://%s" % self.proxy
        
    def process_response(self, request, response, spider):  
        if response.status != 200:
            print('\n\nip_port:%s访问失败\n%s %s\n\n\t重试中%s次...' % (
                        self.proxy,
                        response.url,
                        response.status,
                        request.meta.get('retry_times', 0)
                    )
                )
            return self._retry(request) or response
        return response
        
    def process_exception(self, request, exception, spider):
        print('\n\nip_port:%s访问失败\n%s\n\n\t重试中%s次\n%s...' % (
                    self.proxy, 
                    request.url,
                    request.meta.get('retry_times', 0), 
                    str(exception)
                )
            )
        return self._retry(request)
        
    def _get_ip(self):
        sql = "select ip + ':' + convert(varchar,port) from autohome_ipproxy"
        self.cur.execute(sql)
        ip_port_list = self.cur.fetchall()
        ip_port_list.append([False])    # False则不使用代理
        ip_port = random.choice(ip_port_list)[0]
        if ip_port:
            print('\n\n----------随机切换ip %s----------\n\n' % ip_port)
        else:
            print('\n\n----------不使用代理----------\n\n' )
        return ip_port
        
    def _retry(self, request):
        retries = request.meta.get('retry_times', 0) + 1
        if retries <= 20:
            self.proxy = self._get_ip()
            new_request = request.copy()
            new_request.meta['retry_times'] = retries
            new_request.dont_filter = True
            if self.proxy:
                new_request.meta['proxy'] = "http://%s" % self.proxy
            return new_request
        
class RandomUserAgent(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        # self.user_agent = user_agent
        self.user_agent = settings['UA_LIST']
        
    def process_request(self, request, spider):
        ua = random.choice(self.user_agent)
        request.headers.setdefault('User-Agent', ua)
        # print('\n','----------' + ua + '----------','\n')
        
class SaveHttpError(object):
    # def __init__(self):
        # self.index = 1
    def process_response(self, request, response, spider):
        fn = re.findall('com\.cn/(.*?)\.html',response.url)[0].replace('/','')
        if response.status in (302,307):
            with open('.\\debug\\%s.txt' % fn, 'w', encoding='utf-8') as f:
                f.write('url:%s\n\nrequest_headers:%s\n\nresponse_headers:%s\n\ncontent:%s' % (response.url,str(request.headers),str(response.headers),response.text))
            # self.index += 1
            # print('正在重试！！！')
            # redirect_url = response['Location'].decode('utf-8')
            
        return response
    

                
                
                
                
                
                
                
                
                
                
                
                