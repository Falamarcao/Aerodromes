# from multiprocessing import Pool, current_process
from Crawler.website import Website
from Crawler.Page import Page

class Prefeituras(Website, Page):

    def __init__(self):
        pass

    def email(self, url: str):
        r = self.Page(url)
        r.email_addresses()
        return r.email_addresses


if __name__ == '__main__':
    prefeituras = Prefeituras()
    results = prefeituras.email('http://www.louveira.sp.gov.br/')
    print(results)
