#!/usr/bin/env python
#-*- coding:utf-8 -*-
#============================================
# Author:
# date:
# description: 解析人人网全国中学信息
# 思路：
#============================================
import urllib2
import re
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient

db_host = "127.0.0.1"
db_port = 27017
db_name = "openclass"

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
    "香港":8101,
}
provinceMap = dict([[v,k] for k,v in provinceMap.items()])

#解码字符串 北京
def getUnicodeStr(s):
    name = []
    for word in s.split(";"):
        try:
            name.append(unichr(int(word[2:])))
        except:
            pass    
    return "".join(name)

#获得某个市级区域的学校列表，如果事直辖市，则是整个直辖市的学校
def getTownHtml(town_id):
    try:
        url = "http://support.renren.com/juniorschool/%s.html" % town_id
        print "请求网络数据：",url
        return urllib2.urlopen(url).read()
    except:
        print "网络错误！"
        pass
         
def getProvinceData():
    content = open("/home/xiyang/workspace/school-data/cityArray.js")
    #分离出市级id和名称
    partten = re.compile("(\d+):([\w\d\\\\]+)")
    provinceList = []
    for line in content.readlines():
        data = partten.findall(line)
        citys = []
        province = {} 
        for s in data:
            if len(s[0]) == 4:#城市
                #print s[0],s[1].decode('unicode_escape')
                citys.append({"id":s[0],"name":s[1].decode('unicode_escape')})
            
        province_id = len(data[0][0])==4 and data[0][0] or data[0][0][0:4]
    
        #只处理列表中的几个省
        if provinceMap.has_key(int(province_id)):
            province['id'] = province_id
            province['name'] = provinceMap[int(province_id)]
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
    
    return citySchoolData

conn = MongoClient(db_host)
db = conn.openclass
juniorschool = db.juniorschool

if __name__ == "__main__":
    provinceList = getProvinceData();
    print provinceList
    
    for province in provinceList:
        citys = province['citys']
        #print province
        if citys:#有城市，说明不是直辖市
            for city in citys:
                data = {"id":city['id'],"name":city['name'],"data":getCitySchool(getTownHtml(city['id']))}     
                print "insert into mongodb:",city['name']
                juniorschool.insert(data)          
        
        else:#直辖市
            data = {"id":province['id'],"name":province['name'],"data":getCitySchool(getTownHtml(province['id']))}   
            print "insert into mongodb:",province['name']           
            juniorschool.insert(data)