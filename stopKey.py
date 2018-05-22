#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import json
import time
import urllib
import os
from urllib.request import Request, urlopen
from urllib.error import URLError
from tqdm import *

index_logined_menu = '''
-------------------------------------------------------------------------
                         Zabbix API程序


-------------------------------------------------------------------------
【1】获取监控流量数据 【2】批处理主机监控项 【3】退出程序
'''

url = "http://172.25.25.57/zabbix/api_jsonrpc.php"
header = {"Content-Type": "application/json"}

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
    # create request object
    req = urllib.request.Request(url, data)
    for key in header:
        req.add_header(key, header[key])

    result = urllib.request.urlopen(req)
    response = json.loads(result.read().decode('utf-8'))

    return (response['result'])

def get_Host():
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
    # create request object
    req = urllib.request.Request(url, data)
    for key in header:
        req.add_header(key, header[key])
    result = urllib.request.urlopen(req)
    response = json.loads(result.read().decode('utf-8'))
    #print("主机名\thostid")
    for host in response['result']:
        #print('{0} {1}'.format(host['name'],host['hostid']))
        print(host)
    return response['result']

def get_ItemID():
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
    # create request object
    req = urllib.request.Request(url, data)
    for key in header:
        req.add_header(key, header[key])
    result = urllib.request.urlopen(req)
    response = json.loads(result.read().decode('utf-8'))
    for item in response['result']:
        print(item)
    return response['result']

def get_upkey(upfile):       # 获得文件中up的端口
    keyList = []
    with open(upfile,'r') as f:
        for line in f.readlines():
            if 'up                    up' in line:
            #if 'up' in line:
                keyboj = '[' + line.split(" ",1)[0] + ']'
                keyList.append(keyboj)
    return keyList

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
    req = urllib.request.Request(url, data)
    for key in header:
        req.add_header(key, header[key])
    result = urllib.request.urlopen(req)
    response = json.loads(result.read().decode('utf-8'))

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
    req = urllib.request.Request(url, data)
    for key in header:
        req.add_header(key, header[key])
    result = urllib.request.urlopen(req)
    response = json.loads(result.read().decode('utf-8'))

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
    req = urllib.request.Request(url, data)
    for key in header:
        req.add_header(key, header[key])
    result = urllib.request.urlopen(req)
    response = json.loads(result.read().decode('utf-8'))
    dir = os.getcwd() + '\\output'
    if not os.path.exists(dir):
        os.mkdir(dir)
    with open(dir + '\\' + file_name + '.txt', 'w') as f:
        for item in tqdm(response['result']):
            if value_format == 1:
                time, value = timestamp_datatime(int(item['clock'])), item['value']
            else:
                time, value = timestamp_datatime(int(item['clock'])), round(int(item['value']) / value_format, 2)
            f.write(time + '  ' + str(value) + '\n')


if __name__ == '__main__':
    exit_flag = False
    ID_auth = get_AuthID()  # 登录zabbix，获取token
    #hostlist = get_Host()  # 获取所有hosts的hostid以及name
    print(index_logined_menu)
    while not exit_flag:
        choose_input = input('选择功能编号[1-3] >>> ')
        if choose_input == "1":
            get_Host()          #打印host以及hostid
            input_hostid = input('输入hostid >>> ')
            ID_item = get_ItemID()   #打印Key以及itemid
            while True:
                search_key = input('请输入想要查找的键值 >>> ')
                for id in ID_item:
                    if search_key in id['key_']:
                        print(id)
                choose2_input = input('继续请输入1，再次查找请输入2 >>> ')
                if choose2_input == "1":
                    itemid_input = input('请输入要获取监控数据的itemid >>> ')

                    start_time_t = input('起始时间(ex 2016-11-24 09:27:00): ')

                    end_time_t = input('结束时间(ex 2016-11-24 10:27:00): ')
                    value_format = input('请输入单位倍数(KB、MB、GB)：')
                    if value_format == 'MB':
                        value_format = 1048576
                    elif value_format == 'KB':
                        value_format = 1024
                    elif value_format == 'GB':
                        value_format = 1073741824
                    elif value_format == '1':
                        value_format = 1
                    file_name = input('请输入保存的文件名：')
                    start_time = datatime_timestamp(start_time_t)
                    end_time = datatime_timestamp(end_time_t)
                    get_history()
                elif choose2_input == "2":
                    continue

        if choose_input == "2":   #批处理主机监控项
            dir = os.getcwd() + '\\filter'         #创建filter目录
            if not os.path.exists(dir):
                os.mkdir(dir)
            listfile = os.listdir(dir)
            print('''----- fliter目录下的文件 ----''')
            for i in listfile:                    #获取filter目录下的文件
                print(i)
            in_upfile = input("请选择输入对应主机的文件>>> ")
            upfile = os.getcwd() + '\\filter\\' + in_upfile
            get_Host()          #打印host以及hostid
            input_hostid = input('输入hostid(exit退出) >>> ')
            ID_item = get_ItemID()               #获取键值
            upitemid_list = []                   #定义up接口的itemid列表
            res_item = ID_item
            upkey_list = get_upkey(upfile)             #获取up的接口
            downitemid_list = []                 #定义非up接口的itemdid列表

            for i in upkey_list:
                for x in ID_item:
                    if i == x['key_'][-len(i):]:
                        upitemid_list.append(x['itemid'])  # 获取up接口的itemid存入upitemid_list列表
                        res_item.remove(x)
            for i in res_item:
                downitemid_list.append(i['itemid'])  # 获取down接口的itemid存入downitemid_list列表

            for id in downitemid_list:             #循环 禁用非up接口
                item_disabled(id)
            for id in upitemid_list:               #循环 启用up接口
                item_enbled(id)
            print("已处理")

        if choose_input == "3":
            exit_flag = True
            continue
