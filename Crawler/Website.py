from Crawler.Session import Session
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from re import sub


class Website(object):

    def __init__(self, url: str):
        self.Session = Session()
        self.url: url = url
        self.response = self.Session.get(name='WebSite', url=url)
        self.url_list: list = []

    @property
    def urls(self):
        """
        Crawl children URLs from a given parent (Website) URL. Ignoring external urls (not likely base_url)
        :return:
        """
        if self.response is not None:
            # exception for cases where the url is 'https://site.com/new/'
            url = urlsplit(self.response.url)
            if (url.path[0] == '/') and (url.path[-1] == '/'):
                base_url = self.response.url
            else:
                base_url = f"{url.scheme}://{url.netloc}"
            if self.response.status_code == 200:
                bs = BeautifulSoup(self.response.content, features='html.parser')
                url_list = set()
                url_list.add(self.response.url)
                for anchor in bs.find_all('a'):
                    if "href" in anchor.attrs:
                        if base_url in anchor.attrs['href']:
                            url = anchor.attrs['href'].strip()
                        elif ('htt' in anchor.attrs['href']) or ('www.' in anchor.attrs['href']):
                            # ignore external links
                            continue
                        elif '#' in anchor.attrs['href']:
                            # ignore scroll links
                            continue
                        elif 'mailto:' in anchor.attrs['href']:
                            # ignore emails
                            continue
                        else:
                            url = urlsplit(f"{base_url}/{anchor.attrs['href'].strip()}")
                            url = f"{url.scheme}://{url.netloc}" + sub(r'\/\/+', '/', url.path)

                        # append url to list
                        if url not in url_list:
                            url_list.add(url)
                return url_list
        return None
