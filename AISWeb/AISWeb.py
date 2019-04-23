from requests_html import HTMLSession as Session
from multiprocessing import Pool, current_process
from datetime import datetime, timezone
from lxml.html import fromstring
from bs4 import BeautifulSoup
from csv import DictWriter
from hashlib import sha1
from os import listdir
from re import compile
from time import time
import json


class AISWeb(object):
    def __init__(self):
        self.Session = Session()
        self.base_url: str = "https://www.aisweb.decea.gov.br/"
        self.url: str = ""
        self.headers: dict = {"Accept": "text/html,application/xhtml+xml,application/xml;"
                                        "q=0.9,image/webp,image/apng,*/*;"
                                        "q=0.8,application/signed-exchange;v=b3",
                              "User-Agent": "Prometo usar somente em horários de baixo nivel de acesso S2"}
        self.response = None
        self.response_exception = None
        self.bs = None
        self.tempnotam_elements: list = []
        self.results: list = []
        self.hash = self.hash_code()

    def get(self, name: str, url: str, params: dict = None):
        """
        function to do http get requests
        :param name: transaction name for log control
        :param url: from where are asking data
        :param params: filters and mandatory parameters
        :return: Json or False when status_code isn't 200.
        """
        try:
            response = self.Session.get(url, params=params, headers=self.headers)
        except Exception as e:
            self.response_exception = e
            print("-" * 100)
            print(f"|HTTP GET| {e} happened on {name} with params:\n{params}\n")
            print("-" * 100, "\n")
            return False

        if response.status_code == 200:
            return response
        else:
            print("-" * 100)
            print(f"|HTTP GET| Response code: {response.status_code} on {name} with params:\n{params}")
            print("-" * 100, "\n")
            return {}

    def post(self, name: str, url: str, data: dict = None, params: dict = None):
        """
        function to do http post requests
        :param name: transaction name for log control
        :param url: from where are asking data
        :param data: web form data
        :param params: filters and mandatory parameters
        :return: Json or False when status_code isn't 200.
        """
        try:
            response = self.Session.post(url, data=data, params=params, headers=self.headers)
        except Exception as e:
            self.response_exception = e
            print("-" * 100)
            print(f"|HTTP POST| {e} happened on {name} with data: {data} and params:\n{params}\n")
            print("-" * 100, "\n")
            return False

        if response.status_code == 200:
            return response
        else:
            print("-" * 100)
            print(f"|HTTP POST| Response code: {response.status_code} on {name} with data: {data} and params:{params}")
            print("-" * 100, "\n")
            return {}

    # extract values
    def get_icao(self, icao: str = None):
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

    def get_status(self, icao: str):
        page = fromstring(self.response.content)
        try:
            status = page.xpath('/html/body/div/div/div/div[1]/div/div/strong/text()')[0] + \
                    page.xpath('/html/body/div/div/div/div[1]/div/div/text()')[1]
            return status.strip()
        except IndexError:
            element = page.xpath('/html/body/div/div/section/div/div[1]/div/div/text()')
            if element and (element[1].strip() == "O aeródromo não foi encontrado."):
                # search for details
                params: dict = {"i": "busca"}
                data: dict = {"q": icao}
                response = self.post(name="alert", url="https://www.aisweb.decea.gov.br/", params=params, data=data)
                status = ''.join(fromstring(response.content).xpath('/html/body/div/div/section[1]/div/div/div[2]'
                                                                    '/div/div/div[2]/div/div/strong/text()'))
                status = status.strip()
                del response, data, params
                if len(status) > 0:
                    return status.strip()
                return element[1].strip()[:-1]
            return "OK"

    @staticmethod
    def scrap_to_list(element):
        element = str(element).split('<')
        vartmp = ""
        for x in range(1, len(element)-1):
            line = element[x].split('>')[1]
            if len(line) > 1:
                line = '|' + line + '|'
            vartmp += line
        # Organizing the data structure (str to list)
        vartmp = [lst.split('|') for lst in vartmp.split('\n')]
        output = []
        for lst in vartmp:
            if len(lst) > 1:
                for s in lst:
                    if s not in ['', ' ']:
                        output.append(s.strip())
        return output

    @property
    def get_temp(self):
        elements = self.bs.find('h4', text=compile(r"AIP \("))
        if elements is not None:
            elements = elements.find_all_previous("div", {"class": "notam"})
            self.tempnotam_elements = elements
            output = []
            for element in elements:
                tmplst = self.scrap_to_list(element)
                while True:
                    duracao = ""
                    divulgacao = ""
                    if "Duração:" in tmplst:
                        i = tmplst.index("Duração:")
                        duracao = tmplst.pop(i+1)
                        del tmplst[i]
                    if "Divulgação:" in tmplst:
                        i = tmplst.index("Divulgação:")
                        divulgacao = tmplst.pop(i+1)
                        del tmplst[i]
                    if duracao or divulgacao:
                        tmplst.append({"Duração": duracao, "Divulgação": divulgacao})
                    if not ("Duração:" in tmplst) and not ("Divulgação:" in tmplst):
                        break
                output.append(tmplst)
            return output
        return ""

    @property
    def get_aip(self):
        elements = self.bs.find('h4', text=compile(r"NOTAM \("))
        if elements is not None:
            elements = elements.find_all_previous("div", {"class": "notam"})
            output = []
            for element in elements:
                if element not in self.tempnotam_elements:
                    output.append(self.scrap_to_list(element))
            return output
        return ""

    @property
    def get_notam(self):
        elements = self.bs.find('h4', text=compile(r"NOTAM \("))
        if elements is not None:
            elements = elements.find_all_next("div", {"class": "notam"})
            output = []
            for element in elements:
                output.append(self.scrap_to_list(element))
            return output
        return ""

    def search_by_icao(self, icao: str):
        process_name = current_process().name
        print(f"\nCurrent Process Name: {process_name}\tICAO: {icao}\n")
        self.url = self.base_url + "?i=aerodromos&codigo=" + icao[0:4]  # [0:4] to avoid bugs, in past appeared '*'
        self.response = self.get("icao", self.url)
        if self.response:
            self.bs = BeautifulSoup(self.response.content, features='html.parser')
            results = {"timestamp": datetime.now(timezone.utc).astimezone().isoformat(), "ICAO": self.get_icao(icao),
                       "CIAD": self.get_value("strong", "Código Identificador de Aeródromos"),
                       "Aeródromo": self.get_value("span", "Nome do Aeródromo"),
                       "Cidade": self.get_value("span", "cidade"),
                       "UF": self.get_value("span", "Estado"),
                       "Status": self.get_status(icao),
                       "TEMP": self.get_temp,
                       "AIP": self.get_aip,
                       "NOTAM": self.get_notam,
                       "Debug": {"response_status_code": self.response.status_code}}
            return results
        return {"ICAO": icao, "DEBUG": {"Exception": self.response_exception}}

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
        with Pool() as p:
            self.results = p.map(self.search_by_icao, icao_list)
            p.close()
            p.join()

    @staticmethod
    def hash_code():
        code = sha1()
        code.update(str(time()).encode('utf-8'))
        return code.hexdigest()[:10]

    def to_csv(self):
        keys = self.results[0].keys()
        with open(f'AISWeb\\output_aisweb_{self.hash}.csv', 'w', newline='') as output_file:
            dict_writer = DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.results)
            print(f'Recorded at file: output_aisweb_{self.hash}.csv')

    def to_json(self):
        with open(f'AISWeb\\output_aisweb_{self.hash}.json', 'w') as file:
            json.dump({"timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                       "data": self.results}, file)
            print(f'Recorded at file: output_aisweb_{self.hash}.json')


if __name__ == '__main__':
    aisweb = AISWeb()
    aisweb.search_by_list_of_icao()
    aisweb.to_csv()
    aisweb.to_json()
