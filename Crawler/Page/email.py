from re import findall, IGNORECASE


class Email(object):

    def __init__(self):
        self._email_list: list = []

    @property
    def address_list(self):
        return self._email_list

    @address_list.setter
    def address_list(self, response):
        self._email_list = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, IGNORECASE)
