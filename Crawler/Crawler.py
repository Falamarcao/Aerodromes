from datetime import datetime, timezone
from multiprocessing import Pool
from typing import Dict, List
from website import Website
from Page.Page import Page


class Crawl(Website):

    def __init__(self, url: str):
        Website.__init__(self, url)

    @property
    def emails_on_website(self):
        return self._email_addresses

    @staticmethod
    def emails_on_page(link):
        page = Page(url=link)
        page.email_addresses = page.response
        return page.email_addresses

    @emails_on_website.setter
    def emails_on_website(self, url_list: list = None):

        if url_list is None:
            self.children_urls = None
            self.url_list = self.children_urls
        else:
            self.url_list = url_list

        with Pool() as p:
            contacts_pool = p.map(self.emails_on_page, self.url_list)
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


if __name__ == '__main__':
    crawl = Crawl('http://www.louveira.sp.gov.br/')
    crawl.emails_on_website = None
    print(crawl.emails_on_website)
