from requests_html import HTMLSession as Session
from multiprocessing import Pool, current_process
from lxml.html import fromstring
from bs4 import BeautifulSoup
from csv import DictWriter
from re import compile
from os import listdir
import hashlib
import time


class AISWeb(object):
    def __init__(self):
        self.Session = Session()
        self.base_url: str = "https://www.aisweb.aer.mil.br/?i=aerodromos&codigo="
        self.url: str = ""
        self.response = None
        self.bs = None
        self.results: list = []
        self.headers: dict = {"User-Agent": "Chrome/62.0.3202.94 Safari/537.36"}

    def get(self, name: str, url: str, params: dict = None):
        """
        function to get json data from API
        :param name: transaction name for log control
        :param url: from where are asking data
        :param params: filters and mandatory parameters
        :return: Json or False when status_code isn't 200.
        """
        try:
            response = self.Session.get(url, params=params, headers=self.headers)
        except Exception as e:
            print("-" * 100)
            print(f" {e} happened on {name} with param list:\n{params}\n")
            print("-" * 100, "\n")
            return False

        if response.status_code == 200 or 404:
            return response
        else:
            print("-" * 100)
            print(f"Response code: {response.status_code} on {name} with param list:\n{params}")
            print("-" * 100, "\n")
            return {}

    # extract values
    def get_icao(self, icao=None):
        if self.response.status_code == 200:
            try:
                return self.bs.find("strong", {"title": "Indicador de Localidade (ICAO Code)"}).text
            except AttributeError:
                pass
        return icao

    def get_value(self, tag: str, title: str):
        element = self.bs.find(tag, {"title": title})
        if element is not None:
            return element.text
        return ""

    @property
    def get_alert(self):
        page = fromstring(self.response.content)
        try:
            s = page.xpath('/html/body/div/div/div/div[1]/div/div/strong/text()')[0] + \
                page.xpath('/html/body/div/div/div/div[1]/div/div/text()')[1]
            return s.strip()
        except IndexError:
            element = page.xpath('/html/body/div/div/section/div/div[1]/div/div/text()')
            if element is not None:
                value = ""
                for i in element:
                    if element.index(i) < len(element):
                        value += i.strip() + ' '
                    else:
                        value += i.strip()
                return value
        return ""

    @property
    def get_notam(self):
        elements = self.bs.find_all("div", {"class": "notam"})
        notam_list = []
        if elements is not None:

            for element in elements:
                notam_dict = {}

                badge_info = element.find_next('span', {'class': compile('.*badge.*')})
                if badge_info is not None:
                    notam_dict.update({"badge_info": badge_info.text})

                    h5 = element.find_next('h5')
                    if h5 is not None:
                        notam_dict.update({"titulo": h5.text[len(badge_info.text)+1:]})

                    pre = element.find_next('pre')
                    if pre is not None:
                        notam_dict.update({"texto1": pre.text})

                    span = element.find_next('span', {'class': ''})
                    if badge_info is not None:
                        notam_dict.update({"texto2": span.text})

                    href = element.find_next('a').get('href')
                    if (href is not None) and ("?i=aerodromos&p=sol&id=" not in href):
                        notam_dict.update({"anexo": href})
                    notam_list.append(notam_dict)
            if len(notam_list) == 1:
                return notam_list[0]
            return notam_list
        return ""

    # search
    def search_by_icao(self, icao: str):
        process_name = current_process().name
        print(f"\nCurrent Process Name: {process_name}\tICAO: {icao}\n")
        self.url = self.base_url + icao
        self.response = self.get("icao", self.url)
        self.bs = BeautifulSoup(self.response.content, features='html.parser')
        results = {"ICAO": self.get_icao(icao),
                   "CIAD": self.get_value("strong", "Código Identificador de Aeródromos"),
                   "Aeródromo": self.get_value("span", "Nome do Aeródromo"),
                   "Cidade": self.get_value("span", "cidade"),
                   "UF": self.get_value("span", "Estado"),
                   "Alerta": self.get_alert,
                   "NOTAM": self.get_notam}
        return results

    @property
    def read_icao_file(self) -> list:
        icao_list: list = []
        icao_filenames = ['AISWeb\\ICAO\\' + i for i in listdir('AISWeb\\ICAO') if i[-5:] == ".icao"]
        if len(icao_filenames) == 0:
            print("Please insert the *.cao files into the folder and try again.")
            exit()
        for file_name in icao_filenames:
            with open(file_name, 'r', newline='\n', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    if line is not None:
                        icao_list.append(line)
                file.close()
        return icao_list

    def search_by_list_of_icao(self, icao_list: list = None):
        """
        get information from AISWeb. If a icao list is not given.
        The function will search for *.icao files
        :param icao_list:
        :return:
        """
        if icao_list is None:
            icao_list = self.read_icao_file
        with Pool(4) as p:
            self.results = p.map(self.search_by_icao, icao_list)
            p.close()
            p.join()

    def to_csv(self):
        code = hashlib.sha1()
        code.update(str(time.time()).encode('utf-8'))
        hash_ = code.hexdigest()[:10]
        keys = self.results[0].keys()
        with open(f'AISWeb\\output_aisweb_{hash_}.csv', 'w', newline='') as output_file:
            print(f'Recorded at file: output_aisweb_{hash_}.csv')
            dict_writer = DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.results)


if __name__ == '__main__':
    aisweb = AISWeb()
    aisweb.search_by_list_of_icao()
    aisweb.to_csv()

