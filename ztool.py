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

index_logined_menu = '''
-------------------------------------------------------------------------
                         Zabbix API程序

-------------------------------------------------------------------------
                        【1】获取监控流量数据

                        【2】批处理主机监控项

                        【3】获取监控数据图表

                        【4】退出程序
'''

headers = {"Content-Type": "application/json"}
api_url = "http://172.25.25.57/zabbix/api_jsonrpc.php"
login_url = "http://172.25.25.57/zabbix/index.php"
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
    r = requests.post(api_url, data=data, headers=headers)
    result_auth = json.loads(r.text)['result']
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
    r = requests.post(api_url, headers=headers, data=data)
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
    r = requests.post(api_url, headers=headers, data=data)
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
    r = requests.post(api_url, headers=headers, data=data)
    result_graphid = json.loads(r.text)['result'][0]['graphid']
    return result_graphid


def item_disabled(disabled_id):
    data_values = {
        "jsonrpc": "2.0",
        "method": "item.update",
        "params": {
            "itemid": disabled_id,
            "status": 1  # 0 is enable,1 is disable
        },
        "auth": ID_auth,
        "id": 1
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    # create request object
    r = requests.post(api_url, headers=headers, data=data)
    result_disitem = json.loads(r.text)['result']


def item_enbled(enabled_id):
    data_values = {
        "jsonrpc": "2.0",
        "method": "item.update",
        "params": {
            "itemid": enabled_id,
            "status": 0  # 0 is enable,1 is disable
        },
        "auth": ID_auth,
        "id": 1
    }
    data = json.dumps(data_values, ensure_ascii=False).encode('utf-8')
    # create request object
    r = requests.post(api_url, headers=headers, data=data)
    result_enitem = json.loads(r.text)['result']


def get_history():
    # get history
    data_values = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": "3",  # 3 - numeric unsigned
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


def get_upkey(upfile):  # 获得文件中up的端口
    keyList = []
    with open(upfile, 'r') as f:
        for line in f.readlines():
            if 'up                    up' in line:
                # if 'up' in line:
                keyboj = '[' + line.split(" ", 1)[0] + ']'
                keyList.append(keyboj)
    return keyList


def get_Pic(graphid, period, stime, width, height,pic_name):
    # 创建session对象，保存cookie值
    s = requests.session()
    postData = {
        "name": "Admin",
        "password": "Esunny123",
        "autologin": 1,
        "enter": "Sign in"
    }
    # 发送带有账号密码的post,并获取cookie存储在session中
    s.post(url=login_url, data=postData, headers=headers_graph)
    graph_url = 'http://172.25.25.57/zabbix/chart2.php'
    payload = {'graphid': graphid,
               'period': period,
               'stime': stime,
               'width': width,
               'height': height
               }
    r = s.get(url=graph_url, params=payload, headers=headers_graph)
    dir = os.getcwd() + '\\image'
    if not os.path.exists(dir):
        os.mkdir(dir)
    with open(dir + '\\' + pic_name + '.png', 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    exit_flag = False
    ID_auth = get_AuthID()  # 登录zabbix，获取token

    while not exit_flag:
        print(index_logined_menu)
        choose_input = input('选择功能编号[1-4] >>> ')
        if choose_input == "1":
            # 获取监控流量数据
            get_Host(ID_auth)  # 打印host以及hostid
            input_hostid = input('输入hostid >>> ')
            ID_item = get_ItemID(input_hostid)  # 打印Key以及itemid
            break_flag = False
            continue_flag = False
            while not break_flag:
                search_key = input('请输入想要查找的键值 >>> ')
                for id in ID_item:
                    if search_key in id['key_']:
                        print(id)
                choose1_input1 = input('继续请输入1，再次查找请输入2 >>> ')
                if choose1_input1 == "1":
                    itemid_input = input('请输入要获取监控数据的itemid >>> ')
                    start_time_t = input('起始时间(eg. 2017-11-24 09:27:00): ')
                    end_time_t = input('结束时间(eg. 2017-11-24 10:27:00): ')
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
                    time.sleep(1)
                    choose1_input2 = input('回到主页面请输入1，继续查找请输入2 >>> ')
                    if choose1_input2 == "1":
                        break_flag = True
                        break
                    if choose1_input2 == "2":
                        continue
                if break_flag == True:
                    break
                elif choose1_input1 == "2":
                    continue

        if choose_input == "2":  # 批处理主机监控项
            # 批处理主机监控项
            dir = os.getcwd() + '\\filter'  # 创建filter目录
            if not os.path.exists(dir):
                os.mkdir(dir)
            listfile = os.listdir(dir)
            print('''----- fliter目录下的文件 ----''')
            for i in listfile:  # 获取filter目录下的文件
                print(i)
            in_upfile = input("请选择输入对应主机的文件>>> ")
            upfile = os.getcwd() + '\\filter\\' + in_upfile
            get_Host(ID_auth)  # 打印host以及hostid
            input_hostid = input('输入hostid(exit退出) >>> ')
            ID_item = get_ItemID(input_hostid)  # 获取键值
            upitemid_list = []  # 定义up接口的itemid列表
            res_item = ID_item
            upkey_list = get_upkey(upfile)  # 获取up的接口
            downitemid_list = []  # 定义非up接口的itemdid列表

            for i in upkey_list:
                for x in ID_item:
                    if i == x['key_'][-len(i):]:
                        upitemid_list.append(x['itemid'])  # 获取up接口的itemid存入upitemid_list列表
                        res_item.remove(x)
            for i in res_item:
                downitemid_list.append(i['itemid'])  # 获取down接口的itemid存入downitemid_list列表

            for id in downitemid_list:  # 循环 禁用非up接口
                item_disabled(id)
            for id in upitemid_list:  # 循环 启用up接口
                item_enbled(id)
            print("已处理")

        if choose_input == "3":
            # 获取监控数据图表
            get_Host(ID_auth)  # 打印host以及hostid
            input_hostid = input('输入hostid >>> ')
            ID_item = get_ItemID(input_hostid)  # 打印Key以及itemid
            break_flag = False
            continue_flag = False
            while not break_flag:
                search_key = input('请输入想要查找的键值 >>> ')
                for id in ID_item:
                    if search_key in id['key_']:
                        print(id)
                choose3_input1 = input('继续请输入1，再次查找请输入2 >>> ')
                if choose3_input1 == "1":
                    itemid_input = input('请输入要获取监控图表的itemid >>> ')
                    ID_graph = get_GraphID(itemid_input)
                    period_input = input('请输入要截取的时长(s) >>> ')
                    stime_input = input('请输入开始时间eg. 20180710000000 >>> ')
                    width_input = input('请输入图片的width >>> ')
                    height_input = input('请输入图片的height >>> ')
                    pic_name_input = input('请输入图片的文件名 >>> ')
                    get_Pic(graphid=ID_graph, period=period_input, stime=stime_input, width=width_input,
                            height=height_input,pic_name=pic_name_input)
                    choose3_input2 = input('回到主页面请输入1，继续查找请输入2 >>> ')
                    if choose3_input2 == "1":
                        break_flag = True
                        break
                    if choose3_input2 == "2":
                        continue
                if break_flag == True:
                    break
                elif choose3_input1 == "2":
                    continue

        if choose_input == "4":
            break
