#!/usr/bin/env python
#-*- coding:utf-8 -*-
#============================================
# Author:dh
# date:
# description: 解析人人网全国高中信息
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


#初始化一个CookieJar来处理Cookie的信息#
cookie = cookielib.CookieJar()

#创建一个新的opener来使用我们的CookieJar#
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

# 获取当前系统的编码方式
type = sys.getfilesystemencoding()

provinceMap = {
    "北京":1101,
    "上海":3101,
    "天津":1201,
    "重庆":5001,
    "黑龙江":2301,
    "吉林":2201,
    "辽宁":2101,
    "山东":3701,
    "山西":1401,
    "陕西":6101,
    "河北":1301,
    "河南":4101,
    "湖北":4201,
    "湖南":4301,
    "海南":4601,
    "江苏":3201,
    "江西":3601,
    "广东":4401,
    "广西":4501,
    "云南":5301,
    "贵州":5201,
    "四川":5101,
    "内蒙古":1501,
    "宁夏":6401,
    "甘肃":6201,
    "青海":6301,
    "西藏":5401,
    "新疆":6501,
    "安徽":3401,
    "浙江":3301,
    "福建":3501,
    "台湾":7101,
    "香港":8101,
    "澳门":8200,
    "美国":9101,
    "澳大利亚":9102,
    "加拿大":9103,
    "英国":919001,
    "新加坡":919002,
}
provinceMap = dict([[v,k] for k,v in provinceMap.items()])

#解码字符串 北京
def getUnicodeStr(s):
    name = []
    try:
    	for word in s.split(";"):
    		name.append(unichr(int(word[2:])))
    except:
    	pass
    if name:
    	return "".join(name)
    else:
    	return s

#获得某个市级区域的学校列表，如果事直辖市，则是整个直辖市的学校
def getTownHtml(town_id):
    try:
        url = "http://support.renren.com/highschool/%s.html" % town_id
        print "请求网络数据：".decode('utf-8').encode(type),url
        return urllib2.urlopen(url).read()
    except:
        print "网络错误！".decode('utf-8').encode(type)
        return ""

fp=open('ccccc.dat','w')        
def getProvinceData():
    content = opener.open('http://s.xnimg.cn/a58580/js/cityArray.js')
    #urllib.urlretrieve('http://s.xnimg.cn/a58580/js/cityArray.js','cityArray.js')
    #content=open('cityArray.js')
    
    cons=content.read().decode('utf-8')

    #分离出市级id和名称
    partten = re.compile("(\d+):([^\"]+)")
    provinceList = []
    data = partten.findall(cons) 

    for k in provinceMap.keys():
    	citys=[]
    	province={}
    	for city in data:
    		if str(k)==city[0] and int(str(k)[:1])==9:
    			citys.append({"id":city[0],"name":city[1]})
    			
    		else:
    			if len(city[0])==len(str(k)) and str(k)[:2]==city[0][:2] and int(str(k)[:1])<9:
    				citys.append({"id":city[0],"name":city[1]} )
    	if not citys:
    		citys.append({"id":str(k),"name":provinceMap[k].decode('utf-8')})

    	province['id'] = k
    	province['name'] = provinceMap[k].decode('utf-8')
    	province['citys'] = citys
    	provinceList.append(province)
    	
    return provinceList

#获得某个的市级区域所有县区的学校
def getCitySchool(content):
    soup = BeautifulSoup(content)
    
    #某个城市的中学列表
    citySchoolData = []
    #县区的列表
    townlist = soup.findAll('a',href="#highschool_anchor") 

    for town in townlist:
        d = {}
        d['name'] = getUnicodeStr(town.string)
        d['id'] = town['onclick'][24:38]
        townSchools = []
        #获得每个县的中学列表
        for school in soup.find('ul',id=d['id']).findChildren('a'):
            townSchools.append(getUnicodeStr(school.string))
        d['schoollist'] = townSchools

        citySchoolData.append(d)

    if not townlist:
    	d = {}
    	d['name'] = ""
        d['id'] = ""
    	townSchools = []
    	for school in soup.findAll('a'):
    		townSchools.append(getUnicodeStr(school.string))
    	d['schoollist'] = townSchools
    	citySchoolData.append(d)
    
    return citySchoolData

conn = MySQLdb.connect(
    host="localhost", user="root", passwd="mysql", db="test", charset='utf8')
cursor = conn.cursor()
def mysqlInsert(in_value):
	sql = "insert into juniorschool values(%s,%s,%s,%s,%s,%s)"
	para=[i for i in in_value]
	cursor.execute(sql, para)

if __name__ == "__main__":
	provinceList = getProvinceData();  

    

	for province in provinceList:  
		for city in province['citys']:
			if province['id']:
				print province['id'],province['name'],city['id'],city['name'],
				data = {"id":city['id'],"name":city['name'],"data":getCitySchool(getTownHtml(city['id']))}
				for ss in data['data']:
					for school in ss['schoollist']:
						#print province['id'],province['name'],city['id'],city['name'],ss['name'],school
						vv=(province['id'],province['name'],city['id'],city['name'],ss['name'],school)
						mysqlInsert(vv)
		conn.commit()
	
	cursor.close()
	conn.close()
