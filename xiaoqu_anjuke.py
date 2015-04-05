#!/usr/bin/env python
#-*- coding:utf-8 -*-
#============================================
# Author: dh
# Date  : 2014-12-27
# Desc  : 解析安居客获取全国所有小区信息
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

#python默认的递归深度是很有限的，大概是900+ 解决的方式是手工设置递归调用深度:
sys.setrecursionlimit(100000) #这里设置10万的递归深度

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

conn = MySQLdb.connect(
    host="localhost", user="root", passwd="mysql", db="test", charset='utf8')
cursor = conn.cursor()

def communityinfo_Insert(in_value):
	sql = "insert into community_info values(%s,%s,%s,%s,%s,%s,%s)"
	para=[i for i in in_value]
	cursor.execute(sql, para)


# 按网址请求网页
def getUrlHtml(url, msg=""):
	try:
		logging.info("请求网络数据：%s %s" % (msg, url.encode('utf-8')))
		outinfo=urllib2.urlopen(url).read()
		if not outinfo:
			logging.info("页面不存在：%s %s" % (msg, url.encode('utf-8')))
			return ""
		return outinfo
	except:
		logging.info("网络错误：%s %s" % (msg, url.encode('utf-8')))
		return ""

#解析小区经纬度
ll_regex=re.compile(r'#l1=(\d+\.\d+)&l2=(\d+\.\d+)&')

#解析小区地址
add_regex=re.compile(r'\[()&nbsp;()\]()')
def soupGetaddr(str):
	str=str.replace('[','')
	return re.sub('&nbsp;|\]','|',str).split('|')


# 分析小区名称地址信息
def analyHtml(cityurl):
	re_info=[]
	context=getUrlHtml(cityurl[0])
	consoup=BeautifulSoup(context)

	#获取下一页地址
	nexturl=""
	aNxt=consoup.find('a',{'class':'aNxt'})
	if aNxt and aNxt.text.replace(' &gt;','')=='下一页'.decode('utf-8'):
		nexturl=aNxt['href']

	#获取小区信息
	
	for info in consoup.findAll('div',{'class':'details'}):
		if info:
			name=[xq.text for xq in info.findChildren('a',{'id':True})]
			addr=[soupGetaddr(xq.text) for xq in info.findChildren('p')]
			latlon=[ll_regex.findall(xq['href']) for xq in info.findChildren('a',{'rel':"nofollow"})]
			addr1,addr2,add3,lat,lon=('','','','','')
			if addr and addr[0]:
				addr1,addr2,add3=addr[0][0],addr[0][1],addr[0][2]
			if latlon:
				try:
					lat,lon=latlon[0][0]
				except Exception, e:
					pass
				
			print cityurl[1],addr1,addr2, name[0],add3,lat,lon

			communityinfo_Insert((cityurl[1],addr1,addr2, name[0],add3,lat,lon))
	conn.commit()
	
	#无下一页，跳出循环
	if not nexturl:
		logging.info('无下一页，请求结束 !')
		return ""
	logging.info('下一页地址:%s' % nexturl.encode('utf-8'))
	analyHtml((nexturl,cityurl[1]))




#获取所有城市URL列表
def getCityUrls():
	city_url=[]
	logging.info("获取所有城市列表")
	url = "http://www.anjuke.com/index.html"
	info = getUrlHtml(url)
	#info=open('anjukeindex.html').read()
	soup=BeautifulSoup(info)
	for city in soup.find('div',{'class':'cities_boxer'}).findChildren('a'):
		if city.text!='保定'.decode('utf-8') and  city.text!='北京'.decode('utf-8'):
			print city['href']+'/community/',city.text
			city_url.append((city['href']+'/community/',city.text))
	return city_url




# http://sh.58.com/xiaoqu/2664/pn_1/
if __name__ == "__main__":

    #citys_Url=getCityUrls()
    #citys_Url=[('http://shanghai.anjuke.com/community/W0QQpZ1060','上海')]
    citys_Url=[
#    ('http://shanghai.anjuke.com/community/W0QQpZ1060','上海'),
#    ('http://shenzhen.anjuke.com/community/','深圳'),
#    ('http://suzhou.anjuke.com/community/','苏州'),
#    ('http://sy.anjuke.com/community/','沈阳'),
#    ('http://sanya.anjuke.com/community/','三亚'),
#    ('http://sjz.anjuke.com/community/','石家庄'),
#    ('http://shaoxing.anjuke.com/community/','绍兴'),
#    ('http://tianjin.anjuke.com/community/','天津'),
#    ('http://ty.anjuke.com/community/','太原'),
#    ('http://tangshan.anjuke.com/community/','唐山'),
#    ('http://taizhou.anjuke.com/community/','泰州'),
#    ('http://wuhan.anjuke.com/community/','武汉'),
#    ('http://wuxi.anjuke.com/community/','无锡'),
#    ('http://weihai.anjuke.com/community/','威海'),
#    ('http://weifang.anjuke.com/community/','潍坊'),
#    ('http://xm.anjuke.com/community/','厦门'),
#    ('http://xa.anjuke.com/community/','西安'),
    ('http://xuzhou.anjuke.com/community/W0QQpZ33','徐州'),
    ('http://yinchuan.anjuke.com/community/','银川'),
    ('http://yangzhou.anjuke.com/community/','扬州'),
    ('http://yt.anjuke.com/community/','烟台'),
    ('http://yichang.anjuke.com/community/','宜昌'),
    ('http://zhengzhou.anjuke.com/community/','郑州'),
    ('http://zh.anjuke.com/community/','珠海'),
    ('http://zs.anjuke.com/community/','中山'),
    ('http://zhenjiang.anjuke.com/community/','镇江'),
    ('http://zibo.anjuke.com/community/','淄博')]
    map(analyHtml,citys_Url)
    cursor.close()
    conn.close()

