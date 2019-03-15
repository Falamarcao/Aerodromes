from multiprocessing import current_process
from Page.Email import Email
from Page.Phone import Phone
from website import Website
from urllib.parse import urlsplit


class Page(Website, Email, Phone):

    def __init__(self, url: str):
        Website.__init__(self, url)
        self.url_path = urlsplit(self.url).path
        Email.__init__(self)
        Phone.__init__(self)

    @property
    def email_addresses(self):
        return self._email_list

    @email_addresses.setter
    def email_addresses(self, response):
        if response is None:
            response = self.response
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {response.url}\n")
        email = Email()
        email.address_list = response.text
        if len(email.address_list) > 0:
            self._email_list = {"url_path": self.url_path, "email": email.address_list}
        else:
            self._email_list = None

    @property
    def phone_numbers(self):
        return self._phone_numbers_list

    @phone_numbers.setter
    def phone_numbers(self, response):
        if response is None:
            response = self.response
        print(f"\nCurrent Process Name: {current_process().name}\tURL: {response.url}\n")
        phone = Phone()
        phone.number_list = response.text
        if len(phone.number_list) > 0:
            self._phone_numbers_list = {"url_path": self.url_path, "phone": phone.number_list}
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
