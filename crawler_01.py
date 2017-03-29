#-*- coding:utf-8 -*-

#------
#   程序：糗事百科爬虫
#   版本：0.1
#   语言：Python 2.7
#   操作：输入带分页的地址，去掉最后面的数字，设置一下起始页数和终点页数。
#   功能：按回车查看新段子
#------

import urllib
import urllib2
import re
import thread
import time

class Qsbk(object):
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mazilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}
        #存放段子的变量，每一个元素是每一页的段子们
        self.stories = []
        #存放程序是否继续运行的变量
        self.enable = False
        
    #传入某一页的索引获得页面代码    
    def getPage(self, pageIndex):    
        try:
            url = 'http://www.qiushibaike.com/8hr/page/' + str(self.pageIndex)
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            #将页面转化为UTF-8编码
            pageCode = response.read().decode('utf-8')
            return pageCode
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print u'连接糗事百科失败，错误原因：',e.reason
                return None
                
    #传入某一页代码，返回本页不带图片的段子列表            
    def getPageItems(self, pageIndex):
        pageCode = self.getPage(pageIndex)
        if not pageCode:
            print '页面连接失败...'
            return None
        pattern = re.compile('<div class="author clearfix">.*?<h2>(.*?)'+ \
            '</h2>.*?<div.*?content">.*?<span>(.*?)</span>.*?</a>'+ \
            '(.*?)<div class="stats">.*?<span.*?vote">.*?'+ \
            '<i class="number">(.*?)</i>',re.S)
        items = re.findall(pattern, pageCode)
        #用来存储每页的段子们
        pageStories = []
        #遍历正则表达式匹配的信息
        for item in items:
            #是否含有图片
            haveImg = re.search('img', item[2])
            if not haveImg:
                replaceBR = re.compile('<br/>')
                #替换抓取内容中的<br/>为换行符\n
                text = re.sub(replaceBR, '\n', item[1])                #item[0]是发布者，item[1]是内容,item[3]是点赞数
                pageStories.append([item[0].strip(), text.strip(), item[3].strip()])
        return pageStories
    
    #加载并提取页面的内容，加入到列表中
    def loadPage(self):
        #如果当前未看的页数少于2页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                #获取新一页
                pageStories = self.getPageItems(self.pageIndex)
                #将该页的段子存放到全局list中
                if pageStories:
                    self.stories.append(pageStories)
                    self.pageIndex += 1
    
    def getOneStory(self, pageStories, page):
        for story in pageStories:
            input = raw_input()
            self.loadPage()
            if input == 'Q':
                self.enable = False
                return
            sty_content = u'第%d页\n发布人：%s\n赞：%s\n%s\n------' \
                % (page, story[0], story[2], story[1] )
            print sty_content.encode('gbk', 'ignore')            #Windows中的cmd，默认GBK的编码，所以需要先将上述Unicode的字符content的先编码为GBK
    
    #开始方法
    def start(self):
        print u'正在读取糗事百科，按回车查看新段子，Q退出'
        #使变量为True，程序可以正常运行
        self.enable = True
        #先加载一页内容
        self.loadPage()
        #局部变量，控制当前读到了第几页
        nowPage = 0
        while self.enable:
            if len(self.stories) > 0:
                #从全局list中获取一页的段子
                pageStories = self.stories[0]
                 #当前读到的页数加一
                nowPage += 1
                #将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                self.getOneStory(pageStories, nowPage)
                
if __name__ == '__main__':                
    spider = Qsbk()
    spider.start()

