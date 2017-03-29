#-*- coding:utf-8 -*-

#------
#   程序：淘宝mm爬虫
#   版本：0.1
#   语言：Python 2.7
#   工具：pyspider框架（自带PyQuery），PhantomJS
#   功能：下载每个mm的个人信息，爱秀照片，分别保存各自文件夹
#------

from pyspider.libs.base_handler import *
import os

PAGE_START = 1
PAGE_END = 30
DIR_PATH = 'D:/web_develop/python/mm'
        
        
class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.base_url = 'https://mm.taobao.com/json/request_top_list.htm?page='
        self.page_num = PAGE_START
        self.total_num = PAGE_END
        self.deal = Deal()
        
    def on_start(self):
        while self.page_num <= self.total_num:
            url = self.base_url + str(self.page_num)
            self.crawl(url , callback=self.index_page, validate_cert=False)
            self.page_num += 1
    
    def index_page(self, response):
        for each in response.doc('.lady-name').items():
            self.crawl(each.attr.href, callback=self.detail_page, fetch_type='js', validate_cert=False)
            
    def detail_page(self, response):
        domain = response.doc('.mm-p-domain-info li > span').text()
        if domain:
            page_url = 'https:' + domain
            self.crawl(page_url, callback=self.domain_page, validate_cert=False)

    def domain_page(self, response):
        name = response.doc('.mm-p-model-info-left-top dd > a').text()
        dir_path = self.deal.mkDir(name)
        brief = response.doc('.mm-aixiu-content').text()
        if dir_path:
            imgs = response.doc('.mm-aixiu-content img').items()
            count = 1
            self.deal.saveBrief(brief, dir_path, name)
            for img in imgs:
                url = img.attr.src
                if url:
                    extension = self.deal.getExtension(url)
                    file_name = name + str(count) + '.' + extension
                    count += 1
                    self.crawl(img.attr.src, callback=self.save_img, 
                                save={'dir_path': dir_path, 'file_name': file_name}, validate_cert=False)
                                
    def save_img(self, response):
        content = response.content
        dir_path = response.save['dir_path']
        file_name = response.save['file_name']
        file_path = dir_path + '/' + file_name
        self.deal.saveImg(content, file_path)

        
class Deal():

    def __init__(self):
        self.path = DIR_PATH
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    
    def mkDir(self, path):
        path = path.strip()
        dir_path = self.path + path
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
            return dir_path
        else:
            return dir_path
    
    def saveImg(self, content, path):
        f = open(path, 'wb')
        f.write(content)
        f.close
        
    def saveBrief(self, content, dir_path, name):
        file_name = dir_path + '/' + name + '.txt'
        f = open(file_name, 'w+')
        f.write(content.encode('utf-8'))
        f.close()
    
    def getExtension(self, url):
        extension = url.split('.')[-1]
        return extension