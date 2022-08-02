# -*- coding: utf-8 -*-
from asyncio.windows_events import NULL
from io import BytesIO
from urllib import request
import re
import gzip
import time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import init


cid_filename = datetime.now().date().strftime('%Y%m%d')+'_cid.txt'
web_filename = datetime.now().date().strftime('%Y%m%d')+'_web.txt'

# 获取不同公益src的CID


class CIDSpider(object):
    # 定义常用变量
    def __init__(self) -> None:
        self.url_id = 'https://www.butian.net/Company/{}'

    # 获取响应内容函数，随机的User-Agent

    def get_cid(self, url):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        req = requests.get(url=url, headers=init.headers,
                           verify=False, allow_redirects=False)
        return req.status_code

    def write_html(self, data):
        with open(cid_filename, 'a')as f:
            f.write(data)

    # 主函数，用于控制整体逻辑
    def run(self):
        print("获取可用CID中...")
        time_start = time.time()
        for i in range(1, 64220):
            if self.get_cid(url=self.url_id.format(i)) == 200:
                self.write_html(str(i)+'\n')
        time_end = time.time()
        print("获取完成,共用时:", time_end-time_start, 's')

# 通过CID去获取域名或ip


class WebSpider(object):
    # 定义常用变量
    def __init__(self) -> None:
        self.url = 'https://www.butian.net/Loo/submit?cid={}'

    # 获取响应内容函数，随机的User-Agent
    def get_html(self, url):
        req = request.Request(url=url, headers=init.headers)
        res = request.urlopen(req)
        html = res.read()
        buff = BytesIO(html)
        result = gzip.GzipFile(fileobj=buff)
        html = result.read().decode('utf-8')
        data = self.parse_html(html)
        return data

    # 正则表达式解析页面，提取数据
    def parse_html(self, html):
        pattren = re.compile(
            # 正则匹配
            r'"[\w.-]+\.[\w.-]+\..*?"|value="[\w.-]+://[\w.-]+\..*?"', re.S)
        re_list = pattren.findall(html)
        if len(re_list):
            # 去除不存在域名与双引号
            data = re.compile(r"\"(.*?)\"", re.S).findall(re_list[0])[0]
            self.write_html(data+'\n')
            return data
        else:
            return

    # 将提取的数据保存
    def write_html(self, data):
        with open(web_filename, 'a')as f:
            f.write(data)

    # 主函数，用于控制整体逻辑
    def run(self):
        cids = open(cid_filename).readlines()
        for i in cids:
            url = self.url.format(i)
            cid_web = i.strip('\n') + ":"+self.get_html(url)+'\n'
            with open('cid_web.txt', 'a') as f:
                f.writelines(cid_web)
            print(cid_web.strip('\n'))
            time.sleep(1)
        print("Complete!")


# 主程序入口
if __name__ == '__main__':

    cid = CIDSpider()
    web = WebSpider()
    cid.run()
    web.run()
