from phonenumbers import format_number, parse, PhoneNumberFormat
from phonenumbers.phonenumberutil import NumberParseException
from re import findall, sub


class Phone(object):

    def __init__(self):
        self._phone_numbers_list = set()

    @property
    def numbers(self):
        return self._phone_numbers_list

    @numbers.setter
    def numbers(self, page):
        # ((?![9]{10,11}) exclude test phone number as (99) 99999-9999
        # there is not area code starting with 0
        phone_list = findall(r'(?![9]{10,11})[1-9][0-9][1-9][0-9]{7,8}', sub(r'[()\-\s]', '', page))

        tmp = set()
        for number in phone_list:
            try:
                number = format_number(parse(str(number), 'BR'), PhoneNumberFormat.NATIONAL)
                if '(' in number:  # adding only numbers parsed by google's module
                    tmp.add(number)
            except NumberParseException:
                continue
        self._phone_numbers_list = tmp
