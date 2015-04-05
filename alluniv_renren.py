#!/usr/bin/env python
# coding=utf8
#============================================
# Author     : dh
# Date       : 2014-12-24
# Description:解析人人网全国大学信息
#============================================

import urllib
import urllib2
import cookielib
import sys
import re
import json
import MySQLdb
import os


#初始化一个CookieJar来处理Cookie的信息#
cookie = cookielib.CookieJar()

#创建一个新的opener来使用我们的CookieJar#
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

# 获取当前系统的编码方式
type = sys.getfilesystemencoding()

class Dict(dict):
	def __init__(self, names=(), values=(), **kw):
		super(Dict, self).__init__(**kw)
		for k, v in zip(names, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

def login(email, pasword, domain='renren.com'):
    url = 'http://www.renren.com/PLogin.do'
    postdata = {
        'email': email,
        'password': pasword,
        'domain': domain
    }
    #自定义一个请求#
    req = urllib2.Request(url, urllib.urlencode(postdata))
    #访问该链接#
    result = opener.open(req)

    return result

ema = 'huang081112@126.com'
pas = 'dh081112'
#file = login(ema, pas).read()


#获取所有大学信息#
def getALLUnivs(url):
    try:
        print "请求网络数据：".decode('utf-8').encode(type), url

        # 下载js文件到本地 :
        #urllib.urlretrieve('http://s.xnimg.cn/a73949/allunivlist.js','my_allunivlist.js')

        return opener.open(url).read().decode('utf-8').encode(type)
    except:
        print "网络错误! 尝试读取本地文件...".decode('utf-8').encode(type)
        if os.path.exists(r'my_allunivlist.js'):
        	fp=open('my_allunivlist.js','rb')
        	fil=fp.read()
        	fp.close()
        	return fil.decode('utf-8').encode(type)
        print "读取本地文件失败！".decode('utf-8').encode(type)
        exit(1)

# 将str，转换成list
def strConvTolist(in_str):
    # 处理特殊字符
    print "处理特殊字符".decode('utf-8').encode(type)
    out_str = re.sub(r'{(\w+):', "{\'\g<1>\':", in_str)
    out_str = re.sub(r',(\w+):', ",\'\g<1>\':", out_str)
    out_str = out_str.replace("\t", "")

    return eval(out_str)

conn = MySQLdb.connect(
    host="localhost", user="root", passwd="mysql", db="test", charset='utf8')
cursor = conn.cursor()

def mysqlInsert(value):
	sql = "insert into school values(%s,%s,%s,%s,%s,%s)"
	para=[i.decode('gbk').encode('utf-8') for i in un_value]
	cursor.execute(sql, para)


if __name__ == '__main__':

    #所有大学信息
	str_alluniv=getALLUnivs("http://s.xnimg.cn/a73949/allunivlist.js")[16:-1]

	alluniv=strConvTolist(str_alluniv)

	un_name=("cid","cname","pid","pname","uid","uname")
	
	print "加载到mysql".decode('utf-8').encode(type)
	for country in alluniv:

		if country['univs']:
			for univ in country['univs']:
				un_value=(str(univ['id']), univ['name'],str(country['id']), country['name'],"", "")
				mysqlInsert(un_value)

		elif country['provs']:
			for provs in country['provs']:
				for univ in provs['univs']:
					un_value=(str(univ['id']), univ['name'],str(country['id']), country['name'], str(provs['id']), provs['name'])
					mysqlInsert(un_value)
		else:
			un_value=("", "",str(country['id']), country['name'], "", "")
			mysqlInsert(un_value)

		conn.commit()

	
	cursor.close()
	conn.close()
