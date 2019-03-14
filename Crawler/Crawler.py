from typing import Dict, List

from phonenumbers import format_number, parse, PhoneNumberFormat
from phonenumbers.phonenumberutil import NumberParseException
from multiprocessing import Pool, current_process
from requests_html import HTMLSession as Session
from re import findall, sub, IGNORECASE
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup


class Crawler(object):

    def __init__(self):
        self.Session = Session()
        self.headers: dict = {"User-Agent": "Chrome/62.0.3202.94 Safari/537.36"}

    def get(self, name: str, url: str, params: dict = None):
        """
        function to handle all HTTP GET methods from that class
        :param name: transaction name for log control
        :param url: from where are asking data
        :param params: filters and mandatory parameters when these exists
        :return: Json or False when status_code isn't 200.
        """
        try:
            response = self.Session.get(url, params=params, headers=self.headers)
        except Exception as e:
            print("-" * 100)
            print(f" {e} happened on {name}, URL: {url}\n")
            print("-" * 100, "\n")
            return None
        if response.status_code == 200:
            return response
        else:
            print("-" * 100)
            print(f"Response code: {response.status_code} on {name}, URL: {url}\n")
            print("-" * 100, "\n")
            return None

    def crawl_urls(self, url: str):
        """
        Crawl children URLs from a given parent URL. Ignoring external urls (not likely base_url)
        :param url: a website or just a url with href links inside
        :return:
        """
        response = self.get(name='crawl_urls', url=url)
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
                return url_list
        return None

    def find_phone_numbers_on_page(self, url: str):
        """
        get phone numbers from a given URL
        :param url:
        :return: Python Dictionary: {"url_path": url.path, "phone": phone_list} or None
        """
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {url}\n")
        response = self.get(name='find_phone', url=url)
        if (response is not None) and (response.status_code == 200):
            html = sub(r'[()\-\s]', '', response.text)
            # ((?![9]{10,11}) exclude test phone number as (99) 99999-9999
            # there is not area code starting with 0
            phone_list = findall(r'(?![9]{10,11})[1-9][0-9][1-9][0-9]{7,8}', html)
            if len(phone_list) > 0:
                tmp = set()
                for number in phone_list:
                    try:
                        number = format_number(parse(str(number), 'BR'), PhoneNumberFormat.NATIONAL)
                        if '(' in number:  # adding only numbers parsed by google's module
                            tmp.add(number)
                    except NumberParseException:
                        continue
                phone_list = tmp
                url = urlsplit(url)
                return {"url_path": url.path, "phone": phone_list}
        return None

    def find_emails_on_page(self, url: str):
        """
        get email addresses from a given URL
        :param url:
        :return: Python Dictionary: {"url_path": url.path, "phone": phone_list} or None
        """
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {url}\n")
        response = self.get(name='find_emails', url=url)
        if (response is not None) and (response.status_code == 200):
            email_list = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, IGNORECASE)
            if len(email_list) > 0:
                url = urlsplit(url)
                return {"url_path": url.path, "email": email_list}
        return None

    def find_contacts_on_page(self, url: str):
        """
         get email addresses and phone numbers from a given URL
         :param url:
         :return: Python Dictionary: {"url_path": url.path, "phone": phone_list} or None
         """
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {url}\n")
        response = self.get(name='find_emails', url=url)
        if (response is not None) and (response.status_code == 200):
            url = urlsplit(url)

            # E-MAIL
            email_list = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, IGNORECASE)

            # PHONE NUMBERS
            html = sub(r'[()\-\s]', '', response.text)
            # ((?![9]{10,11}) exclude test phone number as (99) 99999-9999
            # there is not area code starting with 0
            phone_list = findall(r'(?![9]{10,11})[1-9][0-9][1-9][0-9]{7,8}', html)
            if len(phone_list) > 0:
                tmp = set()
                for number in phone_list:
                    try:
                        number = format_number(parse(str(number), 'BR'), PhoneNumberFormat.NATIONAL)
                        if '(' in number:  # adding only numbers parsed by google's module
                            tmp.add(number)
                    except NumberParseException:
                        continue
                phone_list = tmp

            # RETURN
            if all((len(email_list), len(phone_list))) > 0:
                return {"url_path": url.path, "email": email_list, "phone": phone_list}
            elif len(email_list) > 0:
                return {"url_path": url.path, "email": email_list}
            elif len(phone_list) > 0:
                return {"url_path": url.path, "phone": phone_list}
        return None

    def find_contacts_on_website(self, url: str):
        """
        get contacts from a given website
        :param url: website url
        :return: json: {"timestamp": str, "url": str, "data": [{"path": str, "email": {str}, "phone", {str}}]}
        """""
        crawled_url_list = self.crawl_urls(url)
        with Pool() as p:
            contacts_pool = p.map(self.find_contacts_on_page, crawled_url_list)
            p.close()
            p.join()

        # Uniqueness and formatting return
        json: Dict[str, str, List[Dict[str, set]]] = {"timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                                                      "url": url, "data": []}
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

        return json

    def find_phone_numbers_on_website(self, url: str):
        """
        get phone numbers from a given website
        :param url: website url
        :return: json:{"timestamp": str, "url": str, "data": [{"path": str, "phone", {str}}]}
        """""
        crawled_url_list = self.crawl_urls(url)
        with Pool() as p:
            phone_pool = p.map(self.find_phone_numbers_on_page, crawled_url_list)
            p.close()
            p.join()

        # Uniqueness and formatting return
        json: Dict[str, str, List[Dict[str, set]]] = {"timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                                                      "url": url, "data": []}
        for dictionary in phone_pool:
            if dictionary is not None:
                phones_return = set()
                for phone in dictionary["phone"]:
                    if not any(phone in d["phone"] for d in json["data"]):
                        phones_return.add(phone)
                if len(phones_return) > 0:
                    json["data"].append({"path": dictionary['url_path'], "phone": phones_return})
        return json

    def find_emails_on_website(self, url: str):
        """
        get emails from a given website
        :param url: website url
        :return: json:{"timestamp": str, "url": str, "data": [{"path": str, "email": {str}}]}
        """""
        crawled_url_list = self.crawl_urls(url)
        with Pool() as p:
            email_pool = p.map(self.find_emails_on_page, crawled_url_list)
            p.close()
            p.join()

        # Uniqueness and formatting return
        json: Dict[str, str, List[Dict[str, set]]] = {"timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                                                      "url": url, "data": []}
        for dictionary in email_pool:
            if dictionary is not None:
                emails_return = set()
                for email in dictionary["email"]:
                    if not any(email in d["email"] for d in json["data"]):
                        emails_return.add(email)
                if len(emails_return) > 0:
                    json["data"].append({"path": dictionary['url_path'], "email": emails_return})
        return json


if __name__ == '__main__':
    crawler = Crawler()
    # results = crawler.find_emails_on_website('http://www.louveira.sp.gov.br/')
    # results = crawler.find_emails_on_website('http://aracati.ce.gov.br/')
    # results = crawler.find_emails_on_website('http://www.pmcg.mg.gov.br/')
    # results = crawler.find_emails_on_website('http://www.aruana.go.gov.br/')
    results = crawler.find_contacts_on_website('https://jundiai.sp.gov.br/')
    # results = crawler.find_emails_on_website('http://www.pmcg.mg.gov.br/')
    # results = crawler.find_emails_on_website('http://www.aruana.go.gov.br/')
    print(results)
