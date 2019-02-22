from requests_html import Session
from pandas import DataFrame
from bs4 import BeautifulSoup

class AISWEB(object):
    def __init__(self):
        self.Session = Session()
        self.base_url: str = "https://www.aisweb.aer.mil.br/?i=aerodromos&codigo="
        self.url: str = ""
        self.response = None
        self.bs = None
        self.results = None
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
            self.response = self.Session.get(url, params=params, headers=self.headers)
        except Exception as e:
            print(f" {e} happened on {name} with param list:\n{params}\n")
            return False

        if self.response.status_code == 200:
            return self.response.content
        else:
            print("-" * 100)
            print(f"Response code: {self.response.status_code} on {name} with param list:\n{params}")
            print("-" * 100, "\n")
            return {}

    # extract values
    def get_ciad(self):
        if self.response != {}:
            return self.bs.find("strong", {"title": "Código Identificador de Aeródromos"})
        return None

    def get_icao(self):
        if self.response != {}:
            return self.bs.find("strong", {"title": "Indicador de Localidade (ICAO Code)"})
        return None

    def get_status(self):
        if self.response != {}:
            return self.bs.find("span", {"title": "Nome do Aeródromo"})
        return None

    def get_name(self):
        if self.response != {}:
            return self.bs.find("span", {"title": "Nome do Aeródromo"})
        return None

    def get_city(self):
        if self.response != {}:
            return self.bs.find("span", {"title": "cidade"})
        return None

    def get_state(self):
        if self.response != {}:
            return self.bs.find("span", {"title": "Estado"})
        return None

    # search
    def search_by_icao(self, icao: str):
        self.url = self.base_url + icao
        self.response = self.get("icao", self.url)
        self.bs = BeautifulSoup(self.response)
        del self.response
        self.results = DataFrame({"Status": self.get_status,
                                  "Aeródromo": self.get_name(),
                                  "Cidade": self.get_city(),
                                  "UF": self.get_state})
        return self.results
