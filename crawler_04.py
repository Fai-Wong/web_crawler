#-*- coding:utf-8 -*-

#------
#   程序：蜂鸟模特库爬虫
#   版本：0.1
#   语言：Python 2.7
#   工具：urllib2，正则表达式
#   功能：下载每个模特的个人信息，照片，分别保存各自文件夹
#------

import re
import urllib2
import os


class fnModel():
    
    def __init__(self):
        self.siteURL = 'http://model.fengniao.com/model_list.php?sortid=1'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        self.tool = Tool()
    
    
    def getPage(self, pageIndex):
        url = self.siteURL + '&page=' + str(pageIndex)
        request = urllib2.Request(url, headers=self.headers)
        response = urllib2.urlopen(request)
        return response.read().decode('utf-8')
        
    def getContents(self, pageIndex):
        page = self.getPage(pageIndex)
        pattern1 = re.compile('<ul class="model-list clearfix">(.*?)</ul>', re.S)
        result = re.search(pattern1, page)
        pattern2 = re.compile('<li>.*?<a href="(.*?)" class="pic">.*?<img src="(.*?)".*?<span>(.*?)</span>.*?<a.*?>(.*?)</a>.*?<.*?click">(.*?)</span>.*?</li>',re.S)
        items = re.findall(pattern2, result.group(1))
        contents = []
        for item in items:
            contents.append([item[0],item[1],item[2],item[3],item[4]])
        return contents


    #获取个人详情页面
    def getDetailPage(self, infoURL):
        response = urllib2.urlopen(infoURL)
        return response.read().decode('utf-8')

    #获取个人文字简介
    def getBrief(self, page):
        pattern = re.compile('<div class="info-list">(.*?)<div class="info-interact">', re.S)
        result = re.search(pattern, page)
        return self.tool.replace(result.group(1))

    #获取页面所有图片
    def getAllImgs(self, page):
        pattern1 = re.compile('<div class="wrapper summary-pic mt20">(.*?)<div class="wrapper mt20 clearfix info-container">', re.S)
        content = re.search(pattern1, page)
        pattern2 = re.compile('<img.*?src="(.*?)"', re.S)
        images = re.findall(pattern2, content.group(1))
        return images

    #传入图片url，文件名，保存单张图片
    def saveImg(self, imageURL, fileName):
        u = urllib2.urlopen(imageURL)
        data = u.read()
        f = open(fileName, 'wb')
        f.write(data)
        print u'正在悄悄保存她的一张照片为', fileName
        f.close()

    #保存头像
    def saveIcon(self, iconURL, name):
        splitPath = iconURL.split('.')
        fTail = splitPath.pop()
        fileName = name + '/icon.' + fTail
        self.saveImg(iconURL, fileName)

    #保存个人简介
    def saveBrief(self, content, name):
        fileName = name + '/' + name + '.txt'
        f = open(fileName, 'w+')
        f.write(content.encode('utf-8'))
        print u'正在偷偷保存她的个人信息为', fileName
        f.close()

    #保存多张图片
    def saveImgs(self, images, name):
        number = 1
        for imageURL in images:
            splitPath = imageURL.split('.')
            fTail = splitPath.pop()
            if len(fTail) > 3:
                fTail = 'jpg'
            fileName = name + '/' + str(number) + '.' + fTail
            self.saveImg(imageURL, fileName)
            number += 1

    #创建新目录
    def mkdir(self, path):
        path = path.strip()
        if not os.path.isdir(path):
            os.makedirs(path)
            print u'偷偷新建了名字叫做', path, u'文件夹'
            return True
        else:
            print u'名为', path, u'地文件夹已经创建成功'
            return False

    #将一页mm信息保存起来
    def savePageInfo(self, pageIndex):
            contents = self.getContents(pageIndex)
            for item in contents:
                try:
                    #0个人链接,1头像,2地区,3名字,4人气
                    print u'发现一位模特，名字叫做', item[3], u'地区', item[2], u'人气', item[4]
                    print u'正在偷偷地保存', item[3], u'的信息'
                    print u'又意外地发现她的个人地址是', item[0]
                    detailURL = 'http://model.fengniao.com'+ item[0]
                    detailPage = self.getDetailPage(detailURL)
                    brief = self.getBrief(detailPage)
                    images = self.getAllImgs(detailPage)
                    self.mkdir(item[3])
                    self.saveBrief(brief, item[3])
                    self.saveIcon(item[1], item[3])
                    self.saveImgs(images, item[3])
                except Exception, e:
                    print u'抓取失败，异常：', e

    #传入起始页， 获取mm图片
    def savePagesInfo(self, start, end):
        for i in range(start, end+1):
            print u'正在偷偷地寻找第', i, u'个地方， 看看mm在不在'
            self.savePageInfo(i)

            
#处理页面标签类
class Tool:
    removeImg = re.compile(' +|&nbsp;')
    removeAddr = re.compile('<a.*?>|</a>')
    replaceLine = re.compile('<div.*?>|</div>')
    replaceTD = re.compile('\t+')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')
    removeNoneLine = re.compile('\n+')

    def replace(self, x):
        x = re.sub(self.removeImg, '', x)
        x = re.sub(self.removeAddr, '', x)
        x = re.sub(self.replaceLine, '\n', x)
        x = re.sub(self.replaceTD, '', x)
        x = re.sub(self.replaceBR, '\n', x)
        x = re.sub(self.removeExtraTag, '', x)
        x = re.sub(self.removeNoneLine, '\n', x)
        return x.strip()
            
            
def main():
    spider = fnModel()
    #获取1-10页的模特
    spider.savePagesInfo(1, 2)

if __name__ == '__main__':
    main()
