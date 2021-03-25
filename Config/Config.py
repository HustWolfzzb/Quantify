import json

class Config():
    def __init__(self, type, info='../Config/info.json'):
        self.data = {}
        self.type = type
        with open(info,'r', encoding='utf8') as f:
            data = json.load(f)

    def getInfo(self):
        if self.type.find('百度')!=-1 or self.type.find('baidu')!=-1:
            return self.data['百度文字识别']
        if self.type.find('mysql')!=-1 or self.type.find('Mysql')!=-1 or self.type.find('MYSQL')!=-1:
            return self.data['Mysql']
        if self.type.find('Tushare')!=-1 or self.type.find('TUSHARE')!=-1 or self.type.find('tushare')!=-1 or self.type.find('ts')!=-1:
            return self.data['Tushare']
        if self.type.find('Neo4j') != -1 or self.type.find('neo4j') != -1:
            return self.data['Neo4j']