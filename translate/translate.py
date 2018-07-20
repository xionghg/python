#! /usr/bin/python3
# -*- coding: utf-8 -*-
import time
import re
import sys

from http.client import HTTPConnection
from contextlib import closing
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


def trans(query, fromLanguage, toLanguage):
    appid = '20151113000005349'
    secretKey = 'osubCEzlGjzvw8qdQc41'

    httpClient = None
    myurl = '/api/trans/vip/translate'

    q = query
    # 'zh'
    fromLang = fromLanguage
    # 'cht'
    toLang = toLanguage
    salt = random.randint(32768, 65536)

    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode(encoding='utf-8'))
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    # try:
    #     httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
    #     httpClient.request('GET', myurl)
    #     #response是HTTPResponse对象
    #     response = httpClient.getresponse()
    #     return response.read().decode("unicode_escape")
    # except Exception as e:
    #     print(e)
    # finally:
    #     if httpClient:
    #         httpClient.close()

    with closing(HTTPConnection('api.fanyi.baidu.com')) as conn:
        conn.request('GET', myurl)
        response = conn.getresponse()
        return response.read().decode("unicode_escape")


def other():
    content = []
    content.append('asdf')
    content.append('aswrewer')
    print(content)


def readFile(fileName):
    inFile = open(fileName, "r", encoding="utf-8")
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
            outFile.write("read" + ": " + m.group('value'))
            outFile.write('\n')
        else:
            outFile.write('\n')


def readFileToDict(fileName):
    dict = {}
    regex = '\s*<string.+name\s*=\s*"(?P<name>[^"]+("\s*product\s*=\s*"(?P<product>[^"]+))?)"[^>]*>(?P<value>.*)</string'
    pattern = re.compile(regex, re.S)

    with open(fileName, "r", encoding="utf-8") as f:
        read = f.readline()
        while read:
            if 'string' in read:
                while '</string' not in read:
                    read += f.readline()
                m = pattern.match(read)
                if m:
                    dict[m.group('name')] = read
            read = f.readline()

    return dict


def readFileToArray(fileName):
    array = []
    lineNumber = 0
    regex = '\s*<string.+name\s*=\s*"(?P<name>[^"]+("\s*product\s*=\s*"(?P<product>[^"]+))?)("\s*msgid\s*=\s*"(?P<msgid>[^"]+))?"[^>]*>(?P<value>.*)</string'
    pattern = re.compile(regex, re.S)

    with open(fileName, "r", encoding="utf-8") as f:
        read = f.readline()
        while read:
            lineNumber += 1
            temp = 0
            if 'string' in read:
                while '</string' not in read:
                    read += f.readline()
                    temp += 1
                m = pattern.match(read)
                if m:
                    if m.group('msgid'):
                        msgid = m.group('msgid')
                    else:
                        msgid = ''
                    array.append(StringLine(m.group('name'), msgid, m.group('value'), lineNumber, False))
                lineNumber += temp
            else:
                array.append(StringLine('UnknownString', '', read.replace('\n', ''), lineNumber, True))
            read = f.readline()

    return array


def writeToFile(fileName, array, result, printLine):
    regex = '"dst":"((?P<index>[^"]+)@(?P<line>[^"]*))"'
    pattern = re.compile(regex, re.S)
    # m = pattern.search(str(result))
    for m in pattern.finditer(result):
        index = m.group('index')
        line = m.group('line')
        line = line.replace('“', '"').replace('”', '"').replace('\/', '/')
        array[int(index)].setValue(line)

    if printLine:
        for line in array:
            # print('line: ' + str(line.lineNumber) + '    key: ' + line.key + '    value: ' + line.value.replace('\n',''))
            print('line:%-4d key: %s    value: %s' % (line.lineNumber, line.key, line.value))
    preName = fileName.split('.xml')[0] + '_'
    tamp = time.strftime('%Y%m%d_%H%M%S')
    outFilename = preName + tamp + ".xml"

    print('结果写入文件: ' + outFilename + '\n')
    # outFile = open(outFilename, "w", encoding="utf-8")
    with open(outFilename, "w", encoding="utf-8") as f:
        for line in array:
            if line.key in 'UnknownString':
                f.write(line.value)
            else:
                if len(line.msgid) > 0:
                    f.write('    <string name="%s" msgid="%s">%s</string>\n' % (line.key, line.msgid, line.value))
                else:
                    f.write('    <string name="%s">%s</string>\n' % (line.key, line.value))


def translate(fileName, fromLang, toLang):
    array = readFileToArray(fileName)
    transArray = []
    index = 0
    for line in array:
        if line.key not in 'UnknownString':
            transArray.append(str(index) + '@' + line.value)
        index += 1
        continue
    print('需翻译行数: ' + str(len(transArray)) + '\n')
    transStr = ''
    for i in range(len(transArray) - 1):
        transStr += transArray[i] + '\n'
    if len(transArray) > 0:
        transStr += transArray[-1]
    # print(transStr)
    result = trans(transStr, fromLang, toLang)
    # print(result)
    writeToFile(fileName, array, result, True)


def translateAfterCompare(file1, file2, fromLang, toLang):
    print('对比文件: ' + file2 + '\n')
    array = readFileToArray(file1)
    dict = readFileToDict(file2)
    for i in (range(len(array))):
        if (array[i].key in dict.keys()):
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
    for i in range(len(transArray) - 1):
        transStr += transArray[i] + '\n'
    if len(transArray) > 0:
        transStr += transArray[-1]
    result = trans(transStr, fromLang, toLang)
    # print(result)

    print('从对比文件中插入行数: ' + str(len(dict)) + '\n')
    for key in dict.keys():
        array.append(StringLine('UnknownString', '', dict[key], 0, True))

    writeToFile(file1, array, result, False)


if __name__ == '__main__':
    # 预设参数
    if 'linux' in sys.platform:
        basefile = '/home/xionghg/test/translate/'
        file = basefile + 'strings.xml'
        file2 = basefile + 'strings2.xml'
    if 'win32' in sys.platform:
        file = "D:\strings.xml"
    fromLang = 'zh'
    toLang = 'cht'
    choice = 6

    # 读取命令行参数
    if len(sys.argv) > 3:
        print('读取命令行参数1')
        fromLang = sys.argv[1]
        toLang = sys.argv[2]
        file = sys.argv[3]
        choice = 5
    if len(sys.argv) == 5:
        print('读取命令行参数2')
        file2 = sys.argv[4]
        choice = 6
    # TODO 支持相对路径

    print('待翻译文件: ' + file + '\n')

    if choice == 1:
        readFile(file)
    if choice == 2:
        dict = readFileToDict(file)
        for key in dict:
            print('key: ' + key + '    value: ' + dict[key])
    if choice == 3:
        array = readFileToArray(file)
        for line in array:
            print('line: ' + str(
                line.lineNumber) + '  key: ' + line.key + '  msgid: ' + line.msgid + '  value: ' + line.value)
    if choice == 4:
        other()
    if choice == 5:
        translate(file, fromLang, toLang)
    if choice == 6:
        translateAfterCompare(file, file2, fromLang, toLang)
