from session import Session
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from re import sub


class Website(object):

    def __init__(self, url: str = None):
        self.url: url = url
        self.Session = Session()
        self.response = None if url is None else self.Session.get(name='WebSite', url=url)
        self.url_list = None
        self._email_addresses = None

    @property
    def children_urls(self):
        return self.url_list

    @children_urls.setter
    def children_urls(self, response=None):
        """
        Crawl children URLs from a given parent (Website) URL. Ignoring external urls (not likely base_url)
        :param response: requests.get response object
        :return:
        """
        if response is None:
            response = self.response

        if response is not None:
            # exception for cases where the url is 'https://site.com/new/'
            url = urlsplit(response.url)
            if (url.path[0] == '/') and (url.path[-1] == '/'):
                base_url = response.url
            else:
                base_url = f"{url.scheme}://{url.netloc}"
            if response.status_code == 200:
                bs = BeautifulSoup(response.content, features='html.parser')
                url_list = set()
                url_list.add(response.url)
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
                self.url_list = url_list
            else:
                self.url_list = None
