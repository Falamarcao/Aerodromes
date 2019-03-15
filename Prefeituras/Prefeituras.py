# from multiprocessing import Pool, current_process
from Crawler.website import Website


class Prefeituras(Website):

    def __init__(self):
        pass

    def email(self, url: str):
        r = Website(url)
        r.email()
        return r.email


if __name__ == '__main__':
    prefeituras = Prefeituras()
    results = prefeituras.email('http://www.louveira.sp.gov.br/')
    print(results)
