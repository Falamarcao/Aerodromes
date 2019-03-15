from multiprocessing import current_process
from Crawler.Page.email import Email
from Crawler.Page.phone import Phone
from urllib.parse import urlsplit


class Page(object):

    def __init__(self, url: str):
        self.url = urlsplit(url)
        self._email_list = None
        self._phone_list = None
        self._elements_list = None

    @property
    def email_addresses(self):
        return self._email_list

    @email_addresses.setter
    def email_addresses(self, response):
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {response.url}\n")
        email = Email()
        email = email.address_list(response)
        if len(email.address_list) > 0:
            self._email_list = {"url_path": self.url.path, "email": email.address_list}
        self._email_list = None

    @property
    def phone_numbers(self):
        return self._phone_list

    @phone_numbers.setter
    def phone_numbers(self, response):
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {response.url}\n")
        phone = Phone()
        phone = phone.number_list(response)
        if len(phone.number_list) > 0:
            self._phone_list = {"url_path": self.url.path, "phone": phone.number_list}
        self._phone_list = None

    # @property
    # def elements(self):
    #     return self.elements_list
    #
    # @elements.setter
    # def elements(self, *args: dict):
    #     for dict_ in args:
    #         if len(dict_) > 0:
    #             tmp = {"url_path": self.url.path}
    #             self._elements_list.append(tmp.update(dict_))
