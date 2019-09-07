from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests
import re


class VoucherNotAvailable(Exception):
    pass


class Voucher(ABC):

    def get_voucher(self):
        self.response = requests.get(self.URL)
        if self.response.status_code == 200:
            return self.voucher()
        else:
            raise VoucherNotAvailable()

    @abstractmethod
    def voucher(self):
        pass


class LaFuenteVoucher(Voucher):

    def __init__(self):
        self.URL = "http://lafuenteunlp.com.ar/web/"

    def voucher(self):
        return self.voucher_section().text.strip()

    def voucher_section(self):
        return self.soup().find('h2')

    def soup(self):
        return BeautifulSoup(self.html(), 'html.parser')

    def html(self):
        return self.response.content


class FranjaMoradaVoucher(Voucher):

    def __init__(self):
        self.URL = "https://www.facebook.com/pg/\
            FranjaMoradaInformaticaUNLP/posts/"

    def voucher(self):
        return re.findall("\d+", self.voucher_section())[0]

    def voucher_section(self):
        return self.html().split("voucher")[2]

    def html(self):
        return self.response.text.lower()
