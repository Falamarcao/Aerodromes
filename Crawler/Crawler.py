# from phonenumbers import format_number, parse, PhoneNumberFormat
# from phonenumbers.phonenumberutil import NumberParseException
from multiprocessing import Pool, current_process
from requests_html import HTMLSession as Session
from re import findall, sub, IGNORECASE
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from collections import deque


class Crawler(object):

    def __init__(self):
        self.Session = Session()
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
            print("-" * 100)
            print(f" {e} happened on {name}, URL: {url}\n")
            print("-" * 100, "\n")
            return False

        if response.status_code == 200:
            return response
        else:
            print("-" * 100)
            print(f"Response code: {response.status_code} on {name}, URL: {url}\n")
            print("-" * 100, "\n")
            return response

    def find_urls(self, url: str):
        response = self.get(name='find_all_href', url=url)
        if response:
            # exception for cases where the url is 'https://site.com/new/'
            url = urlsplit(response.url)
            if (url.path[0] == '/') and (url.path[-1] == '/'):
                base_url = response.url
            else:
                base_url = f"{url.scheme}://{url.netloc}"
            if response.status_code == 200:
                bs = BeautifulSoup(response.content, features='html.parser')
                url_list = deque()
                url_list.append(response.url)
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
                            url_list.append(url)
                return url_list
        return []

    def find_emails(self, url: str):
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {url}\n")
        response = self.get(name='find_emails', url=url)
        if response:
            if response.status_code == 200:
                email_list = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, IGNORECASE)
                if len(email_list) > 0:
                    return {"url": url, "email": email_list}
                return []

    # THIS IS NOT WORKING 100%.. -------------------------------------------------------------------------------------->
    def find_phone(self, url: str):
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {url}\n")
        response = self.get(name='find_phone', url=url)
        if response:
            if response.status_code == 200:
                html = sub(r'[()-]', '', response.text)
                phone_list = findall(r'[0-9]{2}.[0-9]{8,9}', html)
                print(phone_list)
                if len(phone_list) > 0:
                    tmplst = deque()
                    for number in phone_list:
                        if number is not '':
                            try:
                                tmplst.append(format_number(parse(str(number), 'BR'), PhoneNumberFormat.NATIONAL))
                            except NumberParseException:
                                continue
                    phone_list = tmplst
                    return phone_list
                return []

    def find_phones_in_list(self, url: str):
        crawled_url_list = self.find_urls(url)
        with Pool() as p:
            phone_pool = p.map(self.find_phone, crawled_url_list)
            p.close()
            p.join()
        return phone_pool
    # ----------------------------------------------------------------------------------------------------------------/>

    def find_emails_in_list(self, url: str):
        crawled_url_list = self.find_urls(url)
        with Pool() as p:
            email_pool = p.map(self.find_emails, crawled_url_list)
            p.close()
            p.join()

        # Uniqueness
        emails = set()
        for email_list in email_pool:
            if type(email_list) == list:
                for email in email_list:
                    if email is not None:
                        emails.add(email)
            else:
                if email_list is not None:
                    emails.add(email_list)
        return emails


if __name__ == '__main__':
    crawler = Crawler()
    results = crawler.find_emails_in_list('https://aracati.ce.gov.br/')
    # results = crawler.find_emails_in_list('http://www.pmcg.mg.gov.br/')
    # results = crawler.find_emails('http://www.aruana.go.gov.br/')
    print(results)
