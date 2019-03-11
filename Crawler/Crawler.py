from requests_html import HTMLSession as Session
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup


class Crawler(object):

    def __init__(self):
        self.Session = Session()
        self.base_url: str = ""
        self.headers: dict = {"User-Agent": "Chrome/62.0.3202.94 Safari/537.36"}

    def get(self, name: str, url: str, params: dict = None):
        """
        function to get json data from API
        :param name: transaction name for log control
        :param url: from where are asking data
        :param params: filters and mandatory parameters
        :return: Json or False when status_code isn't 200.
        """
        try:
            response = self.Session.get(url, params=params, headers=self.headers)
        except Exception as e:
            print(f" {e} happened on {name} with param list:\n{params}\n")
            return False

        if response.status_code == 200:
            return response
        else:
            print("-" * 100)
            print(f"Response code: {response.status_code} on {name} with param list:\n{params}")
            print("-" * 100, "\n")
            return {}

    def update_base_url(self, url: str):
        url = urlsplit(url)
        self.base_url = f"{url.scheme}://{url.netloc}"

    def find_all_href(self, url: str):
        self.update_base_url(url)
        response = self.get(name='find_all_href', url=url)
        if response.status_code == 200:
            bs = BeautifulSoup(response.content, features='html.parser')
            url_list = deque()
            for anchor in bs.find_all('a'):
                if "href" in anchor.attrs:
                    if self.base_url in anchor.attrs['href']:
                        link = anchor.attrs['href']
                    elif 'htt' in anchor.attrs['href']:
                        # ignore external links
                        continue
                    elif '#' in anchor.attrs['href']:
                        # ignore scroll links
                        continue
                    elif '/' in anchor.attrs['href']:
                        link = f"{self.base_url}{anchor.attrs['href']}"
                    else:
                        link = f"{self.base_url}/{anchor.attrs['href']}"
                    if url not in url_list:
                        url_list.append(link)
            return url_list
        return []


if __name__ == '__main__':
    crawler = Crawler()
    url = 'http://www.pmcg.mg.gov.br/'
    r = crawler.find_all_href(url)
    print(r)
