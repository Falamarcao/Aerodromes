from requests_html import HTMLSession as Session
from multiprocessing import Pool, current_process
from bs4 import BeautifulSoup
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
        self.headers: dict = {"User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                                              "Chrome/62.0.3202.94 Safari/537.36",
                              "Accept": "application/json"}

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
            print(f" {e} happened on {name} with param list:\n{params}\n")
            return False

        if response.status_code == 200 or 500:
            return response
        else:
            print("-" * 100)
            print(f"Response code: {response.status_code} on {name} with param list:\n{params}")
            print("-" * 100, "\n")
            return {}

    # extract values
    def get_icao(self,icao=None):
        if self.response.status_code == 200:
            try:
                return self.bs.find("strong", {"title": "Indicador de Localidade (ICAO Code)"}).text
            except(TypeError, KeyError):
                return icao
        return icao

    def get_value(self, tag: str, title: str):
        if self.response.status_code == 200:
            try:
                return self.bs.find(tag, {"title": }).text
            except(TypeError, KeyError):
                return None
        return None

    @property
    def get_status(self):
        if self.response.status_code == 200:
            try:
                return self.bs.find("span", {"title": "Nome do Aeródromo"}).text
            except(TypeError, KeyError):
                return None
        return "O aeródromo não foi encontrado."

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
                   "Status": self.get_status}
        self.results = self.results.append(results)

    @property
    def read_icao_file(self) -> list:
        icao_list: list = []
        icao_filenames = [e for e in listdir() if e[-5:] == ".icao"]
        for file_name in icao_filenames:
            with open(file_name, 'r', newline='\n', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    if line is not None:
                        icao_list.append(line)
                file.close()
        return icao_list

    def search_by_list_of_icao(self, icao_list=None):
        if icao_list is None:
            icao_list = self.read_icao_file
        with Pool() as p:
            print('Parallel processing has started...')
            p.map(self.search_by_icao, icao_list)
            p.close()
            p.join()
            print('Parallel processing has finished...')

    def to_csv(self):
        columns: str = ""
        code = hashlib.sha1()
        code.update(str(time.time()))
        hash_ = hash.hexdigest()[:10]

        # extracting columns for CSV file
        n = 1
        n_columns = len(self.results[0].keys())
        for key in self.results[0].keys():
            if n < n_columns:
                columns += f"{key},"
            elif n == n_columns:
                columns += key
                break
            n += 1


        with open(f"output_{hash_}.csv", 'w', encoding='utf-8') as output_file:
            output_file.write(columns)
            for dict_ in self.results:
                line = ""
                n = 1
                for value in dict_.values():
                    if n < n_columns:
                        line += f"{value},"
                    elif n == n_columns:
                        line += value
                    n += 1
                output_file.writeline(line)
            output_file.close()
            del n


if __name__ == '__main__':
    aisweb = AISWeb()
    aisweb.search_by_list_of_icao()
    aisweb.to_csv()
