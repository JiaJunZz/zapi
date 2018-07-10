#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/9 11:12
# @Author  : ZJJ
# @Email   : 597105373@qq.com
import json
import time
import requests
import datetime
import os
from tqdm import *


headers = {"Content-Type": "application/json"}
api_url = "http://172.25.25.57/zabbix/api_jsonrpc.php"
login_url ="http://172.25.25.57/zabbix/index.php"
headers_graph = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}

def timestamp_datatime(value):
    # UNIX时间戳转换成普通时间
    format = '%Y-%m-%d %H:%M:%S'
    # value 为时间戳值,如:1460073600
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt

def datatime_timestamp(dt):
    # 普通时间转换成UNIX时间戳
    time.strptime(dt, '%Y-%m-%d %H:%M:%S')
    s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
    return int(s)

def get_AuthID():
    # get Auth ID
    data_values = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": "Admin",
            "password": "Esunny123"
        },
        "id": 1,
        "auth": None
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    r = requests.post(api_url,data=data,headers=headers)
    result_auth = json.loads(r.text)['result']
    print(r.cookies)
    return result_auth

def get_Host(ID_auth):
    # get host list
    data_values = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "name"],
            "filter": {"host": ""}
        },
        "auth": ID_auth,  # this is string.
        "id": 1,
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    r = requests.post(api_url,headers=headers,data=data)
    result_hostid = json.loads(r.text)['result']
    for host in result_hostid:
        print(host)
    return result_hostid

def get_ItemID(input_hostid):
    # get ItemID list
    data_values = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["itemids", "key_"],
            "hostids": input_hostid,
        },
        "auth": ID_auth,
        "id": 1,
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    r= requests.post(api_url,headers=headers,data=data)
    result_itemid = json.loads(r.text)['result']
    for item in result_itemid:
        print(item)
    return result_itemid

def get_GraphID(ID_item):
    # get ItemID list
    data_values = {
        "jsonrpc": "2.0",
        "method": "graph.get",
        "params": {
            "output": "extend",
            "itemids": ID_item
        },
        "auth": ID_auth,
        "id": 1,
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    r= requests.post(api_url,headers=headers,data=data)
    result_graphid = json.loads(r.text)['result'][0]['graphid']
    return result_graphid

def item_disabled(disabled_id):
    data_values = {
        "jsonrpc": "2.0",
        "method": "item.update",
        "params": {
            "itemid": disabled_id,
            "status": 1    #0 is enable,1 is disable
        },
        "auth": ID_auth,
        "id": 1
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    # create request object
    r = requests.post(api_url,headers=headers,data=data)
    result_disitem = json.loads(r.text)['result']

def item_enbled(enabled_id):
    data_values = {
        "jsonrpc": "2.0",
        "method": "item.update",
        "params": {
            "itemid": enabled_id,
            "status": 0    #0 is enable,1 is disable
        },
        "auth": ID_auth,
        "id": 1
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    # create request object
    r = requests.post(api_url,headers=headers,data=data)
    result_enitem = json.loads(r.text)['result']

def get_history():
    # get history
    data_values = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": "3",  #3 - numeric unsigned
            "time_from": start_time,
            "time_till": end_time,
            "itemids": itemid_input,
            # "limit": 11
        },
        "auth": ID_auth,
        "id": 1,
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    # create request object
    r = requests.post(api_url, headers=headers, data=data)
    result_history = json.loads(r.text)['result']
    dir = os.getcwd() + '\\output'
    if not os.path.exists(dir):
        os.mkdir(dir)
    with open(dir + '\\' + file_name + '.txt', 'w') as f:
        for item in tqdm(result_history):
            if value_format == 1:
                time, value = timestamp_datatime(int(item['clock'])), item['value']
            else:
                time, value = timestamp_datatime(int(item['clock'])), round(int(item['value']) / value_format, 2)
            f.write(time + '  ' + str(value) + '\n')

def get_upkey(upfile):       # 获得文件中up的端口
    keyList = []
    with open(upfile,'r') as f:
        for line in f.readlines():
            if 'up                    up' in line:
            #if 'up' in line:
                keyboj = '[' + line.split(" ",1)[0] + ']'
                keyList.append(keyboj)
    return keyList

def get_Pic(graphid,period,stime,width,height):
    # 创建session对象，保存cookie值
    s = requests.session()
    postData = {
        "name": "Admin",
        "password": "Esunny123",
        "autologin": 1,
        "enter": "Sign in"
    }
    # 发送带有账号密码的post,并获取cookie存储在session中
    s.post(url=login_url,data=postData,headers=headers_graph)
    now = datetime.datetime.now()
    nowtime = now.strftime('%Y%m%d%H%M%S')
    graph_url = 'http://172.25.25.57/zabbix/chart2.php'
    payload = {'graphid': graphid,
               'period': period,
               'stime':stime,
               'width': width,
               'height': height,
               }
    r = s.get(url=graph_url,params=payload,headers=headers_graph)
    with open('1870.png','wb') as f:
        f.write(r.content)

if __name__ == '__main__':
    exit_flag = False
    ID_auth = get_AuthID()  # 登录zabbix，获取token
    get_Pic(graphid=1870,period=36000,stime=201807100000,width=800, height=100)
