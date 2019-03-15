from datetime import datetime, timezone
from Crawler.session import Session
from Crawler.Page.page import Page
from urllib.parse import urlsplit
from multiprocessing import Pool
from typing import Dict, List
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
            self.response = response

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
        self.url_list = None

    @property
    def email(self):
        return self._email_addresses

    @email.setter
    def email(self, response=None):
        crawled_url_list = self.children_urls()
        with Pool() as p:
            contacts_pool = p.map(Page.email_addresses, crawled_url_list.children_urls)
            p.close()
            p.join()

        # Uniqueness and formatting return
        json: Dict[str, str, List[Dict[str, set]]] = {"timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                                                      "url": self.url, "data": []}
        for dictionary in contacts_pool:
            if dictionary is not None:

                emails_return = set()
                phonenum_return = set()

                if dictionary.get('email') is not None:
                    for email in dictionary["email"]:
                        if not any(email in d.get("email", {}) for d in json["data"]):
                            emails_return.add(email)
                if dictionary.get('phone') is not None:
                    for phone in dictionary["phone"]:
                        if not any(phone in d.get("phone", {}) for d in json["data"]):
                            phonenum_return.add(phone)

                bool_emails_return = len(emails_return) > 0
                bool_phonenum_return = len(phonenum_return) > 0

                if bool_emails_return and bool_phonenum_return:
                    json["data"].append(
                        {"path": dictionary['url_path'], "email": emails_return, "phone": phonenum_return})
                elif bool_emails_return:
                    json["data"].append({"path": dictionary['url_path'], "email": emails_return})
                elif bool_phonenum_return:
                    json["data"].append({"path": dictionary['url_path'], "phone": phonenum_return})

        self._email_addresses = json
