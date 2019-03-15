from Crawler.Page import Email, Phone


class Page(object):

    def __init__(self, url: str):
        self.url: str = url
        self.email_list = None
        self.phone_list = None

    def emails(self):
        return self.email_list

    @emails.setter
    def emails(self, email_list: set):
        if len(email_list) > 0:
            self.email_list = {"url_path": url.path, "email": email_list}
        self.email_list = None

    def phone_numbers(self):
        return self.phone_list

    @phone_numbers.setter
    def phone_numbers(self, phone_list: set):
        if len(phone_list) > 0:
            self.phone_list = {"url_path": url.path, "phone": phone_list}
        self.phone_list = None


# # RETURN
# if all((len(email_list), len(phone_list))) > 0:
#     return {"url_path": url.path, "email": email_list, "phone": phone_list}
# elif len(email_list) > 0:
#     return {"url_path": url.path, "email": email_list}
# elif len(phone_list) > 0:
#     return {"url_path": url.path, "phone": phone_list}
# return None
