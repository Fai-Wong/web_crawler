#-*- coding:utf-8 -*-

#------
#   程序：百度贴吧爬虫
#   版本：0.1
#   语言：Python 2.7
#   工具：urllib2库，正则表达式
#   功能：下载帖子的内容，可选只看楼主，保存text
#------

import urllib
import urllib2
import re

#处理页面标签类
class Tool(object):
    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    replaceTD = re.compile('<td>')
    replacePara = re.compile('<p.*?>')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')
    
    def replace(self, x):
        x = re.sub(self.removeImg, '', x)
        x = re.sub(self.removeAddr, '', x)
        x = re.sub(self.replaceLine, '\n', x)
        x = re.sub(self.replaceTD, '\t', x)
        x = re.sub(self.replacePara, '\n  ', x)
        x = re.sub(self.replaceBR, '\n', x)
        x = re.sub(self.removeExtraTag, '', x)
        return x.strip()
        
        
#百度贴吧爬虫类
class Bdtb(object):
    #初始化，传入基地址，是否只看楼主的参数
    def __init__(self, baseUrl, seeLZ, floorTag):
        self.baseURL = baseUrl
        self.seeLZ = '?see_lz=' + str(seeLZ)
        self.tool = Tool()
        self.file = None
        self.floor = 1
        self.defaultTitle = u'百度贴吧'
        self.floorTag = floorTag
    
    #传入页码，获取该页帖子的代码
    def getPage(self, pageNum):
        try:
            url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print u'百度贴吧连接失败', e.reason
                return None

    #获取帖子标题
    def getTitle(self, page):
        pattern = re.compile('<h1 class="core_title_txt.*?>(.*?)</h1>' \
                            , re.S)
        result = re.search(pattern, page)
        if result:
            #print result.group(1)
            return result.group(1).strip()
        else:
            return None
        
    #获取帖子一共有多少页
    def getPageNum(self, page):
        pattern = re.compile('<li class="l_reply_num".*?>.*?</span>'+ \
            '.*?<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            print result.group(1)
            return result.group(1).strip()
        else:
            return None
            
    #获取每一层楼的内容,传入页面内容
    def getContent(self, page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)'+ \
            '</div>', re.S)
        items = re.findall(pattern, page)
        contents = []
        for item in items:
            content = '\n'+self.tool.replace(item)+'\n'
            contents.append(content.encode('utf-8'))
        return contents

    #如果标题不是为None，即成功获取到标题
    def setFileTitle(self, title):
        if title:
            self.file = open(title+'.txt', 'w+')
        else:
            self.file = open(self.defaultTitle + '.txt', 'w+')

    #向文件写入每一楼的信息
    def writeData(self, contents):
        for item in contents:
            if self.floorTag == '1':
                floorLine = '\n' + str(self.floor) + '楼--------------\n'
                self.file.write(floorLine)
            self.file.write(item)
            self.floor += 1
    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        if pageNum == None:
            print u'URL已失效，请重试'
            return
        try:
            print u'该帖子共有' + str(pageNum) + u'页'
            for i in range(1, int(pageNum)+1):
                print u'正在写入第' + str(i) + u'页数据'
                page =self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        except IOError, e:
            print u'写入异常，原因' + e.message
        finally:
            print u'写入任务完成'
        

def main():
    print u'请输入帖子代号'
    baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
    seeLZ = raw_input(u'是否只获取楼主发言，是输入1，否输入0\n')
    floorTag =raw_input(u'是否写入楼层信息，是输入1，否输入0\n')
    bdtb = Bdtb(baseURL, seeLZ, floorTag)
    bdtb.start()


if __name__ =='__main__':
    main()