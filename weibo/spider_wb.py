import random
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class WeiboHotSearchSpider:
    def __init__(self):
        self.url = 'https://s.weibo.com/top/summary?cate=realtimehot'
        self.userAgent = UserAgent

    @staticmethod
    def get_proxy():
        min_port = 5001
        max_port = 10196
        port = random.randint(min_port, max_port)
        return {"http": "http://172.16.5.15:%d" % port, "https": "https://172.16.5.15:%d" % port}

    def req_url(self, url=None):
        if url is None:
            url = self.url
        headers = {"User-Agent": UserAgent().random}
        proxys = self.get_proxy()
        res = requests.get(url, headers, proxies=proxys, headers=headers, timeout=30)
        if res.status_code == 200:
            content = res.content.decode('utf-8')
            infos = self.parse_response(content)

    @staticmethod
    def parse_response(content):
        base_url = "https://s.weibo.com/"
        soup = BeautifulSoup(content, "html.parser")
        tbody = soup.find_all(name="tbody")[0]
        td_list = tbody.find_all(name="td")
        datas = []
        data = {"rank": None, "href": None, "title": None}
        for i, td in enumerate(td_list):
            if i >= 3:
                if 'class="td-01 ranktop"' in str(td):
                    data["rank"] = td.get_text().strip()

                elif 'class="td-02"' in str(td):
                    data["href"] = base_url + td.find_all(name="a")[0]["href"]
                    _str = td.get_text().strip().split('\n')
                    if len(_str) >= 2:
                        data["hot"] = _str[1]
                    data["title"] = _str[0]

                if (i+1) % 3 == 0:
                    print(data)
                    datas.append(data)
                    data = {"rank": None, "href": None, "title": None, "hot": None}

        return datas


if __name__ == "__main__":
    WeiboHotSearchSpider().req_url()

