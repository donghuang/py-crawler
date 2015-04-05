#!/usr/bin/env python
#-*- coding:utf-8 -*-
#============================================
# Author: dh
# Date  : 2014-12-27
# Desc  : 解析58同城获取全国所有小区信息
# 思路：
#============================================
import urllib
import urllib2
import cookielib
import sys
import re
import json
import MySQLdb
import os
from BeautifulSoup import BeautifulSoup
import logging
import time

# 设置默认的level为DEBUG
# 设置log的格式
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

#初始化一个CookieJar来处理Cookie的信息#
cookie = cookielib.CookieJar()

#创建一个新的opener来使用我们的CookieJar#
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

# 获取当前系统的编码方式
type = sys.getfilesystemencoding()


# 按页码访问网页
def getTownHtml(town_id):
    try:
        url = "http://sh.58.com/xiaoqu/pn_%s/" % town_id
        print "请求网络数据：".decode('utf-8').encode(type), url
        return urllib2.urlopen(url).read()
    except:
        print "网络错误！".decode('utf-8').encode(type)
        return ""

# 按网址请求网页


def getUrlHtml(url):
    try:
        logging.info("请求网络数据：%s" % url)
        outinfo = urllib2.urlopen(url).read()
        if not outinfo:
            logging.info("页面不存在：%s" % url)
            return ""
        return outinfo
    except:
        logging.info("网络错误：%s" % url)
        return ""

# 分析小区经纬度位置信息


def analyMapHtml(content):
    lat_regex = re.compile(r'lat:\'\d+.\d+\'')
    lon_regex = re.compile(r'lon:\'\d+.\d+\'')
    print lat_regex.findall(content), lon_regex.findall(content)


# 分析小区名称地址信息
def analyHtml(content):
    soup = BeautifulSoup(content)
    # ullist = soup.findAll('a',href=re.compile('http://sh.58.com/xiaoqu/'))
    ullist = soup.findAll("tr", {"xiaoquid": re.compile("\d+")})
    # ullist = soup.findAll("tr")

    for i in ullist:
        if i:
            print i['xiaoquid'],
            # 获取小区的名称
            xq_name = soup.find("tr", {"xiaoquid": i['xiaoquid']}).findChildren(
                'a', {"class": "t"})
            print xq_name[0].text,

            # 获取小区地址
            xq_addr = soup.find("tr", {"xiaoquid": i['xiaoquid']}).findChildren(
                'li', {"class": "tli2"})
            print xq_addr[0].text,

            # 获取小区经纬度
            xq_lan = soup.find("tr", {"xiaoquid": i['xiaoquid']}).findChildren(
                'a', {"class": "tli4_span3"})
            # print xq_lan[0]['href']
            analyMapHtml(getUrlHtml(xq_lan[0]['href']))


def getNextUrl(content):
    nextsoup = BeautifulSoup(content)
    href = nextsoup.find('a', {"class": "next"})
    if href:
        if href.findChildren('span')[0].string == '下一页'.decode('utf-8'):
            print href['href']
            return href['href']
    return ""

#获取所有城市列表
def getCitys():
	logging.info("获取所有城市列表")
	citylist = []
	url = "http://j2.58cdn.com.cn/js/v6/source/f2c31c3e9241183debc24391e928a80b_15972963879.js"
	info = getUrlHtml(url)
	# 匹配"[a-z]+|汉字"
	city_regex = re.compile(ur'"([a-z]+\|[\u4e00-\u9fa5]+)"')
	info = city_regex.findall(info.decode('utf8'))
	citys_1 = [i for i in info if i.split('|')[0] != 'cn']
	#去重
	citys=list(set(citys_1))
	#还原顺序
	citys.sort(key=citys_1.index)
	citys=[ i.split('|') for i in citys]

	for city in citys:
		logging.info("%s,%s" % (city[0], city[1]))
	return citys



# 获取所有城市以及区县信息
citylist = []
redolist =set()
def getCityLists(citys):
    for city in citys:
    	quxian = {}
        logging.info("%s,%s" % (city[0], city[1]))
        
        #网页错误 跳过
        city_info = getUrlHtml("http://%s.58.com/xiaoqu/" % city[0].encode('utf-8'))
        if not city_info:
        	redolist.add(tuple(city))
        	continue

        cntsoup=BeautifulSoup(city_info).find('b', {"class": "filternum"})
        if not cntsoup:
        	logging.debug("网络延迟，3秒后尝试重连")
        	time.sleep(3)
        	logging.debug("开始尝试重连...")
        	cntsoup=BeautifulSoup(city_info).find('b', {"class": "filternum"})

        if not cntsoup:
        	logging.debug("尝试重连失败,暂时跳过...")
        	redolist.add(tuple(city))
        	continue
        try:
        	redolist.remove(tuple(city))
        except Exception, e:
        	pass
        
        logging.info(cntsoup.text)
        if int(cntsoup.text)<=5000:
        	citylist.append(city)
        	continue
        
        soup = BeautifulSoup(city_info).find('dl', {"class": "secitem", "id": "filter_quyu"}).findChildren('a')
        for i in soup:
            if i['listname'] != city[0]:
                logging.info("%s,%s" % (i['listname'], i.text))
                quxian[i['listname']] = i.text
        city.append(quxian)
        citylist.append(city)


# http://sh.58.com/xiaoqu/2664/pn_1/
if __name__ == "__main__":

    #    my_url="http://sh.58.com/xiaoqu/"
    #    analyHtml(getUrlHtml(my_url))
    #    nexturl=getNextUrl(getUrlHtml(my_url))
    #
    #    while True:
    #    	if nexturl:
    #    		analyHtml(getUrlHtml(nexturl))
    #    		nexturl=getNextUrl(getUrlHtml(nexturl))
    #    	else:
    #    		break
    #getCityLists()
    citys=getCitys()
    getCityLists(citys)
     
    #redolist=set([('sw','汕尾'),('lincang','临沧'),('hami','哈密'),('yanan','延安'),('taizhou','泰州')])
    
    while True:
    	if redolist:
    		redo=[list(i) for i in redolist]
    		logging.info('重新获取请求失败的网页...')
    		getCityLists(redo)
    	else:
    		break

    for city in citylist:
    	if len(city)==3:
    		for c_key in city[2].keys():
    			my_url='http://%s.58.com/xiaoqu/%s/' % (city[0].encode('utf-8'),c_key.encode('utf-8'))
    			analyHtml(getUrlHtml(my_url))
    			nexturl=getNextUrl(getUrlHtml(my_url))
    			while True:
    				if nexturl:
    					analyHtml(getUrlHtml(nexturl))
    					nexturl=getNextUrl(getUrlHtml(nexturl))
    				else:
    					break
    	else:
    		my_url='http://%s.58.com/xiaoqu/' % city[0].encode('utf-8')
    		analyHtml(getUrlHtml(my_url))
    		nexturl=getNextUrl(getUrlHtml(my_url))
    		while True:
    			if nexturl:
    				analyHtml(getUrlHtml(nexturl))
    				nexturl=getNextUrl(getUrlHtml(nexturl))
    			else:
    				break    		