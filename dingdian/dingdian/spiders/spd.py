# -*- coding:utf-8 -*-
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from dingdian.items import DingdianItem, DcontentItem
import sys
from ..mysqlpipelines.sql import Sql

reload(sys)
#改变默认编码方式（原来是ascii）
sys.setdefaultencoding('utf-8')

class Myspider(scrapy.Spider):
    name = 'spd'
    #allowed_domin指定Spider在哪个网站爬取数据
    allowed_domains = ['23us.com']
    bash_url = 'http://www.23us.com/class/'
    bashurl = '.html'

    # 爬虫的入口，可以在此进行一些初始化工作，比如从某个文件或者数据库读入起始url
    def start_requests(self):
        for i in range(1, 10):
            #scrapy会自行调度，并访问该url然后把内容拿回来
            url = self.bash_url + str(i) + '_1' + self.bashurl
            #此处会告诉scrapy去抓取这个url，然后把抓回来的页面用回调函数parse进行解析。
            yield Request(url, self.parse)

    #分类页面解析函数
    def parse(self, response):
        #使用BeautifulSoup解析器
        max_num = BeautifulSoup(response.text, 'lxml').find('div', class_='pagelink').find_all('a')[-1].get_text()
        bash_url = response.url[:-7]
        for num in range(1, int(max_num)+1):
            #拼接分类下每一页的url
            url = bash_url + '_' + str(num) + self.bashurl
            yield Request(url, callback=self.get_name)

    #小说url解析函数
    def get_name(self, response):
        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor="#FFFFFF")
        for td in tds:
            novelname = td.find_all('a')[1].get_text()
            novelurl = td.find('a')['href']
            #meta字典，这是Scrapy中传递额外数据的方法
            yield Request(novelurl, callback=self.get_chapterurl, meta={'name': novelname, 'url': novelurl})

    #小说简介解析函数
    def get_chapterurl(self, response):
        # 创建个DingdianItem对象把我们爬取的东西放进去
        item = DingdianItem()
        item['name'] = str(response.meta['name']).replace(u'\xa0', u'') #前置替换动作，因为unicode中的‘\xa0’字符在转换成gbk编码时会出现问题
        item['novelurl'] = response.meta['url']
        soup = BeautifulSoup(response.text, 'lxml')
        category = soup.table.a.get_text()
        author = soup.table.find_all('td')[1].get_text()
        bash_url = soup.find('p', class_='btnlinks').find('a', class_='read')['href']
        name_id = str(bash_url)[-6:-1].replace(u'/', u'')
        item['category'] = str(category).replace(u'/', u'')
        item['author'] = str(author).replace(u'/', u'')
        item['name_id'] = name_id
        yield item
        yield Request(bash_url, callback=self.get_chapter, meta={'name_id': name_id})

    #章节url解析函数
    def get_chapter(self, response):
        urls = re.findall(r'<td class="L"><a href="(.*?)">(.*?)</a></td>', response.text)
        num = 0
        for url in urls:
            num += 1
            chapterurl = response.url + url[0]
            chaptername = url[1]
            #去重，记住已经爬取过的数据
            rets = Sql.select_chapter(chapterurl)
            if rets[0] == 1:
                print (u'章节已经存在了')
                pass
            else:
                yield Request(chapterurl, callback=self.get_chaptercontent, meta={'num': num,
                                'name_id': response.meta['name_id'],
                                'chaptername': chaptername,
                                'chapterurl': chapterurl
                            })

    #章节内容解析函数
    def get_chaptercontent(self, response):
        item = DcontentItem()
        item['num'] = response.meta['num']
        item['id_name'] = response.meta['name_id']
        item['chaptername'] = response.meta['chaptername']
        item['chapterurl'] = response.meta['chapterurl']
        content = BeautifulSoup(response.text, 'lxml').find('dd', id='contents').get_text()
        item['chaptercontent'] = str(content).replace(u'\xa0', u'')
        return item
        
