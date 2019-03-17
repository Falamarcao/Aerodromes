from multiprocessing import current_process
from urllib.parse import urlsplit
from Page.Phone import Phone
from Page.Email import Email
from website import Website


class Page(Website, Email, Phone):

    def __init__(self, url: str):
        super().__init__(url)
        self.url_path = urlsplit(self.url).path

    @property
    def email_addresses(self):
        return self._email_addresses_list

    @email_addresses.setter
    def email_addresses(self, response):
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {response.url}\n")
        self.addresses = response.text
        if len(self.addresses) > 0:
            self._email_addresses_list = {"url_path": self.url_path, "email": self.addresses}
        else:
            self._email_addresses_list = None

    @property
    def phone_numbers(self):
        return self._phone_numbers_list

    @phone_numbers.setter
    def phone_numbers(self, response):
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {response.url}\n")
        self._phone_numbers_list = response.text
        if len(self.numbers) > 0:
            self._phone_numbers_list = {"url_path": self.url_path, "phone": self.numbers}
        else:
            self._phone_numbers_list = None

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
