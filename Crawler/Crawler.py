# from multiprocessing import Pool, current_process
from Crawler.website import Website


class Crawler(object):

    def __init__(self):
        pass

    @staticmethod
    def crawl(url: str):
        r = Website(url)
        r.email()
        return r.email


if __name__ == '__main__':
    crawler = Crawler()
    results = crawler.crawl('http://www.louveira.sp.gov.br/')
    print(results)
