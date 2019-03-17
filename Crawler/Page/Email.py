from re import findall, IGNORECASE


class Email(object):

    def __init__(self):
        self._email_addresses_list: list = []

    @property
    def addresses(self):
        return self._email_addresses_list

    @addresses.setter
    def addresses(self, page):
        self._email_addresses_list = findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", page, IGNORECASE)


# if __name__ == '__main__':
#     # from requests import get
#     # email = Email()
#     # email.address_list = get('http://www.louveira.sp.gov.br/').text
#     # print(email.address_list)
