from bs4 import BeautifulSoup
import urllib.request


class VoucherScrap():

    def __init__(self):
        self.URL = "http://lafuenteunlp.com.ar/web/"
        self.soup = BeautifulSoup(self.get_html(), 'html.parser')

    def get_html(self):
        request = urllib.request.Request(self.URL)
        html = urllib.request.urlopen(request).read()
        return html

    def get_voucher(self):
        voucher = self.soup.find_all('h2')[0].text.strip()
        return voucher
