# -*- coding: utf-8 -*-
import time
import re
import sys

import http.client
import hashlib
import urllib
import random

class StringLine(object):
	key = "UnknownString"
	value = "UnknownString"
	lineNumber = 0
	isTranslated = False
	def __init__(self, key, value, lineNumber, isTranslated):
		self.key = key
		self.value = value
		self.lineNumber = lineNumber
		self.isTranslated = isTranslated
	def setKey(self, key):
		self.key = key
	def setValue(self, value):
		self.value = value
	def setLineNumber(self, lineNumber):
		self.lineNumber = lineNumber
	def setTranslated(self, isTranslated):
		self.isTranslated = isTranslated


def trans(query):
	appid = '20151113000005349'
	secretKey = 'osubCEzlGjzvw8qdQc41'

	httpClient = None
	myurl = '/api/trans/vip/translate'

	q = query
	fromLang = 'zh'
	toLang = 'en'
	salt = random.randint(32768, 65536)

	sign = appid+q+str(salt)+secretKey
	m1 = hashlib.md5()
	m1.update(sign.encode(encoding = 'utf-8'))
	sign = m1.hexdigest()
	myurl = myurl+'?appid='+appid+'&q='+urllib.parse.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign
	 
	try:
	    httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
	    httpClient.request('GET', myurl)
	    #response是HTTPResponse对象
	    response = httpClient.getresponse()
	    print(response.read())
	except Exception as e:
	    print(e)
	finally:
	    if httpClient:
	        httpClient.close()


def other():
	# str = 'asdf.asdfasdf.xasdf.xml'
	# strs = str.split('.xml')[0]
	# print(len(strs))
	# print(type(strs))
	# for s in strs:
	# 	print(s)
	# print(re.match("rlovep","rlovep.com"))

	# line = ' <string-array name="deleteNote" product="asdf">\n删除</string>'
	# print(line)
	# regex = '<string.+name\s*=\s*"(?P<name>[^"]+)("\s*product\s*=\s*"(?P<product>[^"]+))?".*>(?P<value>.*)</string'
	# pattern = re.compile(regex, re.S)
	# # use match to find pair in line head,use search instead
	# m = pattern.search(line)
	# print("m:")
	# print(m)
	# if m:
	# 	print(m.group(0))
	# 	print(m.group('name'))
	# 	print(m.group('product'))
	# 	print(m.group('value'))

	# line2 = 'fishc'
	# pattern2 = re.compile('[a-z]+')
	# m2 = pattern2.match(line2)
	# print(m2)
	content = []
	content.append('asdf')
	content.append('aswrewer')
	print(content)


def readFile(fileName):
	inFile = open(fileName,"r",encoding="utf-8")
	preName = fileName.split('.xml')[0] + '_'
	tamp = time.strftime('%Y%m%d_%H%M%S')
	outFile = open(preName + tamp + ".xml", "w", encoding="utf-8")

	regex = '<string.+name\s*=\s*"(?P<name>[^"]+)("\s*product\s*=\s*"(?P<product>[^"]+))?".*>(?P<value>.*)</string'
	pattern = re.compile(regex, re.S)
	
	content = []
	read = inFile.readline()
	while read:
		if 'string' in read:
			while '</string' not in read:
				read += inFile.readline()
			content.append(read)
		else:
			content.append(read)
		read = inFile.readline()
	# content = inFile.readlines()
	for line in content:
		m = pattern.search(line)
		if m:
			outFile.write("hahaha" + ": " + m.group('value'))
			outFile.write('\n')
		else:
			outFile.write('\n')


def readFileToDict(fileName):
	inFile = open(fileName,"r",encoding="utf-8")
	dict = {}
	regex = '<string.+name\s*=\s*"(?P<name>[^"]+("\s*product\s*=\s*"(?P<product>[^"]+))?)".*>(?P<value>.*)</string'
	pattern = re.compile(regex, re.S)

	read = inFile.readline()
	while read:
		if 'string' in read:
			while '</string' not in read:
				read += inFile.readline()
			m = pattern.search(read)
			if m:
				dict[m.group('name')] = m.group('value')
		read = inFile.readline()

	return dict


def readFileToArray(fileName):
	inFile = open(fileName,"r",encoding="utf-8")
	array = []
	lineNumber = 0
	regex = '<string.+name\s*=\s*"(?P<name>[^"]+("\s*product\s*=\s*"(?P<product>[^"]+))?)".*>(?P<value>.*)</string'
	pattern = re.compile(regex, re.S)

	read = inFile.readline()
	while read:
		lineNumber += 1
		temp = 0
		if 'string' in read:
			while '</string' not in read:
				read += inFile.readline()
				temp += 1
			m = pattern.search(read)
			if m:
				array.append(StringLine(m.group('name'),m.group('value'),lineNumber,False))
			lineNumber += temp
		else:
			array.append(StringLine('UnknownString',read,lineNumber,True))
		read = inFile.readline()

	return array


def translate(fileName):
	array = readFileToArray(file)
	transArray = []
	index = 0
	for line in array:
		index += 1
		if line.key not in 'UnknownString':
			transArray.append(str(index) + '@' + line.value)
		continue
	transStr = ''
	for i in range(len(transArray)-1):
		transStr += transArray[i] + '\n'
	transStr += transArray[-1]
	print(transStr)
	trans(transStr)
	# decode
	# write back


if __name__ == '__main__':
	if 'linux2' in sys.platform:
		file =  "/home/xionghg/test/translate/privacy_strings.xml"
	if 'win32' in sys.platform:
		file = "D:\strings.xml"
	print(file)
	choice = 5
	if choice == 1:
		readFile(file)
	if choice == 2:
		dict = readFileToDict(file)
		for key in dict:
			print('key: ' + key + '    value: ' + dict[key])
	if choice == 3:
		array = readFileToArray(file)
		for line in array:
			print('line: ' + str(line.lineNumber) + '    key: ' + line.key + '    value: ' + line.value)
	if choice == 4:
		other()
	if choice == 5:
		translate(file)
