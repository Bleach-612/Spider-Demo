import re
import time
import random
import requests

from peewee import *
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


chinaz_db = MySQLDatabase('chinaz', host="127.0.0.1", user="root", password="root", charset='utf8mb4')


"""
在数据库中创建domains_info表

CREATE TABLE `domains_info` (
  `domain` varchar(255) NOT NULL COMMENT '域名',
  `title` varchar(255) default NULL COMMENT '名称',
  `rank` int default NULL COMMENT '排名',
  `weights` int COMMENT '百度权重',
  `PR` int NOT NULL COMMENT '谷歌权重',
  `description` varchar(255) NOT NULL COMMENT '描述',
  `score` int NOT NULL COMMENT '得分',
  `add_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT '入库时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP() COMMENT '更新时间',
  `status` varchar(2) NOT NULL DEFAULT '0' COMMENT '状态',
  PRIMARY KEY (`domain`),
  KEY `add_time` (`add_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4

"""


class DomainsInfo(Model):
    domain = CharField(max_length=255, primary_key=True)
    title = CharField(max_length=255)
    description = CharField(max_length=255)
    rank = IntegerField()
    weights = IntegerField()
    score = IntegerField()
    PR = IntegerField()
    update_time = DateTimeField()
    add_time = DateTimeField()
    status = CharField()

    class Meta:
        database = chinaz_db
        table_name = "domains_info"


class ChinazSpider:
    def __init__(self):
        self.max_workers = 32
        self.base_url = "https://top.chinaz.com/all/"

    @staticmethod
    def get_proxy():
        min_port = 5001
        max_port = 10196
        port = random.randint(min_port, max_port)
        return {"http": "http://172.16.5.15:%d" % port, "https": "https://172.16.5.15:%d" % port}

    def req_url(self, url):
        # 设置请求头和代理
        headers = {"User-Agent": UserAgent().random}
        proxys = self.get_proxy()
        res = requests.get(url, headers, proxies=proxys, headers=headers, timeout=30)
        if res.status_code == 200:
            content = res.content.decode('utf-8')
            infos = self.parse_response(content)
            self.batch_insert_db(infos)

    def parse_response(self, content):
        # 解析数据，粗略用bs处理，也可以使用xpath，正则等
        soup = BeautifulSoup(content, "html.parser")
        li_list = soup.find_all(name="li", attrs={"class": "clearfix"})
        datas = []
        for li in li_list:
            cent_txt = li.find(name="div", attrs={"class": "CentTxt"})

            # 获取title和domain
            right_txt_head = cent_txt.find(name="h3", attrs={"class": "rightTxtHead"})
            title = right_txt_head.find("a")["title"]
            domain = right_txt_head.find(name="span", attrs={"class": "col-gray"}).get_text().strip()

            # 获取rank,weights,pr,description
            clearfix = cent_txt.find(name="div", attrs={"class": "RtCPart clearfix"})
            p_li = clearfix.find_all("p")
            rank = p_li[0].find("a").get_text().strip()
            weights = re.findall("\\d+", p_li[1].find("a").find("img")["src"])[0]
            pr = re.findall("\\d+", p_li[2].find("a").find("img")["src"])[0]
            description = cent_txt.find(name="p", attrs={"class": "RtCInfo"}).get_text().strip().replace("网站简介：", "")

            # 获取得分
            rt_crate_wrap = li.find(name="div", attrs={"class": "RtCRateWrap"})
            score_str = rt_crate_wrap.get_text()
            score = score_str.split(":")[1].replace("\n", "")
            add_time = self.get_now()
            update_time = self.get_now()
            fields = ["domain", "title", "description", "rank", "weights", "score", "PR", "update_time", "add_time"]
            data = [domain, title, description, rank, weights, score, pr, update_time, add_time]
            datas.append(dict(zip(fields, data)))

        return datas

    @staticmethod
    def get_now():
        now = int(time.time())
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))

    def run(self):
        # ps 可以抓首页判定末页值，这里省略，直接写死1923+1
        self.req_url(self.base_url)
        urls = []
        for i in range(2, 1924):
            urls.append(self.base_url + "index_{}.html".format(i))
        # 多线程爬取
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            all_tasks = [executor.submit(self.req_url, url) for url in urls]
            wait(all_tasks, return_when=ALL_COMPLETED)

    @staticmethod
    def batch_insert_db(datas):
        with chinaz_db.atomic():
            try:
                DomainsInfo.insert_many(datas).execute()
            except Exception as e:
                print(e)
                for data in datas:
                    domain = data['domain']
                    del data['domain']
                    del data["add_time"]
                    print(data)
                    DomainsInfo.update(data).where(DomainsInfo.domain == domain).execute()


if __name__ == '__main__':
    spider = ChinazSpider()
    spider.run()








