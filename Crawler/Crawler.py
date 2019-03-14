from typing import Dict, List

from multiprocessing import Pool, current_process
from datetime import datetime, timezone
from urllib.parse import urlsplit


class Crawler(object):

    def __init__(self):
        pass

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

# TODO: GET contact name or info around phone number


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
