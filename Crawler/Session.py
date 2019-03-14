from requests_html import HTMLSession as Sess


class Session(object):
    def __init__(self):
        self.Session = Sess()
        self.headers: dict = {"User-Agent": "Chrome/62.0.3202.94 Safari/537.36"}

    def get(self, name: str, url: str, params: dict = None):
        """
        function to handle all HTTP GET methods from that class
        :param name: transaction name for log control
        :param url: from where are asking data
        :param params: filters and mandatory parameters when these exists
        :return: Json or False when status_code isn't 200.
        """
        try:
            response = self.Session.get(url, params=params, headers=self.headers)
        except Exception as e:
            print("-" * 100)
            print(f" {e} happened on {name}, URL: {url}\n")
            print("-" * 100, "\n")
            return None
        if response.status_code == 200:
            return response
        else:
            print("-" * 100)
            print(f"Response code: {response.status_code} on {name}, URL: {url}\n")
            print("-" * 100, "\n")
            return None
