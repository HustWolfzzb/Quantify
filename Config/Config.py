import json
import os
import sys

def getFileAbsolutePath(nowDir):
    if sys.platform == 'linux':
        return "/home/zzb/Quantify/Config/info.json"
    elif sys.platform == 'darwin':
        return "/Users/zhangzhaobo/PycharmProjects/Quantify/Config/info.json"
    else:
        return os.path.join(os.getcwd(), 'Config\info.json')

def get_BASE_DIR():
    d = os.getcwd()
    if d.find('\\') != -1:
        return d[:d.rfind('\\')]
    else:
        return d[:d.rfind('/')]

class Config():
    def __init__(self, type):
        info = getFileAbsolutePath('../')
        self.data = {}
        self.type = type
        with open(info,'r', encoding='utf8') as f:
            self.data = json.load(f)

    def getInfo(self):
        if self.type.find('百度')!=-1 or self.type.find('baidu')!=-1:
            return self.data['百度文字识别']
        if self.type.find('mysql')!=-1 or self.type.find('Mysql')!=-1 or self.type.find('MYSQL')!=-1:
            return self.data['Mysql']
        if self.type.lower().find('mongo')!=-1 or self.type.lower().find('mongdb')!=-1 :
            return self.data['Mongo']
        if self.type.find('Tushare')!=-1 or self.type.find('TUSHARE')!=-1 or self.type.find('tushare')!=-1 or self.type.find('ts')!=-1:
            return self.data['Tushare']
        if self.type.find('Neo4j') != -1 or self.type.find('neo4j') != -1:
            return self.data['Neo4j']
