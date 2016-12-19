# -*- coding: utf-8 -*-
import time
import re
import sys

import http.client
import hashlib
import urllib
import random

class StringLine(object):
	def __init__(self, key, msgid, value, lineNumber, isTranslated):
		self.key = key
		self.msgid = msgid
		self.value = value
		self.lineNumber = lineNumber
		self.isTranslated = isTranslated
	def setKey(self, key):
		self.key = key
	def setMsgid(self, msgid):
		self.msgid = msgid
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
	toLang = 'cht'
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
	    return response.read().decode("unicode_escape")
	except Exception as e:
	    print(e)
	finally:
	    if httpClient:
	        httpClient.close()


def other():
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
	regex = '\s*<string.+name\s*=\s*"(?P<name>[^"]+("\s*product\s*=\s*"(?P<product>[^"]+))?)"[^>]*>(?P<value>.*)</string'
	pattern = re.compile(regex, re.S)

	read = inFile.readline()
	while read:
		if 'string' in read:
			while '</string' not in read:
				read += inFile.readline()
			m = pattern.match(read)
			if m:
				dict[m.group('name')] = read
		read = inFile.readline()
	return dict


def readFileToArray(fileName):
	inFile = open(fileName,"r",encoding="utf-8")
	array = []
	lineNumber = 0
	regex = '\s*<string.+name\s*=\s*"(?P<name>[^"]+("\s*product\s*=\s*"(?P<product>[^"]+))?)("\s*msgid\s*=\s*"(?P<msgid>[^"]+))?"[^>]*>(?P<value>.*)</string'
	pattern = re.compile(regex, re.S)

	read = inFile.readline()
	while read:
		lineNumber += 1
		temp = 0
		if 'string' in read:
			while '</string' not in read:
				read += inFile.readline()
				temp += 1
			m = pattern.match(read)
			if m:
				if m.group('msgid'):
					msgid = m.group('msgid')
				else:
					msgid = ''
				array.append(StringLine(m.group('name'), msgid, m.group('value'),lineNumber,False))
			lineNumber += temp
		else:
			array.append(StringLine('UnknownString','',read,lineNumber,True))
		read = inFile.readline()
	return array


def writeToFile(fileName, array, result, printLine):
	regex = '"dst":"((?P<index>[^"]+)@(?P<line>[^"]*))"'
	pattern = re.compile(regex, re.S)
	# m = pattern.search(str(result))
	for m in pattern.finditer(result):
		index = m.group('index')
		line = m.group('line')
		line = line.replace('“','"').replace('”','"').replace('\/','/')
		array[int(index)].setValue(line)

	if printLine:
		for line in array:
			print('line: ' + str(line.lineNumber) + '    key: ' + line.key + '    value: ' + line.value)

	preName = fileName.split('.xml')[0] + '_'
	tamp = time.strftime('%Y%m%d_%H%M%S')
	outFilename = preName + tamp + ".xml"
	outFile = open(outFilename, "w", encoding="utf-8")
	print('结果写入文件: ' + outFilename + '\n')
	for line in array:
		if line.key in 'UnknownString':
			outFile.write(line.value)
		else:
			if len(line.msgid) > 0:
				outFile.write('    <string name="%s" msgid="%s">%s</string>\n' %(line.key, line.msgid, line.value))
			else:
				outFile.write('    <string name="%s">%s</string>\n' %(line.key, line.value))


def translate(fileName):
	array = readFileToArray(fileName)
	transArray = []
	index = 0
	for line in array:
		if line.key not in 'UnknownString':
			transArray.append(str(index) + '@' + line.value)
		index += 1
		continue
	transStr = ''
	for i in range(len(transArray)-1):
		transStr += transArray[i] + '\n'
	transStr += transArray[-1]
	print(transStr)
	print('需翻译行数: ' + str(len(transArray)) + '\n')
	result = trans(transStr)
	print(result)

	writeToFile(fileName, array, result, True)


def translateAfterCompare(file1,file2):
	print('对比文件: ' + file2 + '\n')
	array = readFileToArray(file1)
	dict = readFileToDict(file2)
	for i in (range(len(array))):
		if(array[i].key in dict.keys()):
			array[i].value = dict[array[i].key]
			array[i].isTranslated = True
			del dict[array[i].key]
			array[i].key = 'UnknownString'

	transArray = []
	index = 0
	for line in array:
		if line.key not in 'UnknownString' and line.isTranslated == False:
			transArray.append(str(index) + '@' + line.value)
		index += 1
		continue
	print('需翻译行数: ' + str(len(transArray)) + '\n')
	transStr = ''
	for i in range(len(transArray)-1):
		transStr += transArray[i] + '\n'
	if len(transArray) > 0:
		transStr += transArray[-1] 
	result = trans(transStr)
	# print(result)
	print('从对比文件中插入行数: ' + str(len(dict)) + '\n')
	for key in dict.keys():
		array.append(StringLine('UnknownString','',dict[key],0,True))

	writeToFile(file1, array, result, False)


if __name__ == '__main__':
	if 'linux2' in sys.platform:
		file =  "/home/xionghg/test/translate/string.xml"
		# basefile = '/home/xionghg/SharedFolder/workarea/translate/branch_oversea_pvt_Amigo_SystemManager_AndroidM_PowerDev_V3.0.9_rel/res/values-zh-rTW/'
		# basefile = '/home/xionghg/SharedFolder/workarea/7558/gionee_packages_apk_amigo_4.0/mtk/packages_6.0/services/Telephony_mt6755c/res/values-zh-rCN/'
	if 'win32' in sys.platform:
		file = "D:\strings.xml"
	print('待翻译文件: ' + file + '\n')
	choice = 6
	if choice == 1:
		readFile(file)
	if choice == 2:
		dict = readFileToDict(file)
		for key in dict:
			print('key: ' + key + '    value: ' + dict[key])
	if choice == 3:
		array = readFileToArray(file)
		for line in array:
			print('line: ' + str(line.lineNumber) + '  key: ' + line.key + '  msgid: ' + line.msgid + '  value: ' + line.value)
	if choice == 4:
		other()
	if choice == 5:
		translate(file)
	if choice == 6:
		basefile = '/home/xionghg/test/translate/'
		file = basefile+'strings.xml'
		file2 = basefile+'strings2.xml'
		translateAfterCompare(file,file2)


