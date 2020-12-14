from bs4 import BeautifulSoup
import requests
import transliterate
import re
import sqlite3
import uuid


def change_letter(ch, ca1, ca2):
    end_result = ''
    for x in ch:
        if x != ca1:
            end_result += x
        else:
            end_result += ca2
    return end_result


class AvitoParser:
    db = sqlite3.connect('data.db', check_same_thread=False)
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS mydata (
    identifier TEXT UNIQUE NOT NULL,
    geo TEXT,
    request TEXT,
    url TEXT,
    num_ads TEXT)""")
    db.commit()

    def __init__(self, region='Нижний Тагил', request='куртка'):
        self.session = requests.session()

        self.site = 'https://www.avito.ru/'
        self.region = str(region.lower())
        self.request_word = str(request)
        self.request = '/?q=' + self.request_word
        self.url = self.site + self.transliter_region() + self.request

        self.session.headers = {'User-Agent': 'Mozilla/5.0'}
        self.params = {'radius': 0, 'user': 0}
        self.r = self.session.get(self.url, params=self.params)

        self.print_id = ''

    def get_info(self):  # Сборщик данных
        if self.r.status_code == 200:
            html_dock = BeautifulSoup(self.r.text, features='html.parser')
            ads_title = html_dock.find_all('h1', {'class': 'page-title-text-WxwN3 page-title-inline-2v2CW'})
            num_ads = html_dock.find_all('span', {'class': 'page-title-count-1oJOc'})
            print(self.url)
            for title, num in zip(ads_title, num_ads):
                return (self.url, title.text + ' ' + num.text), self.write_app_data(num.text)

    def transliter_region(self):  # Переводчик региона в нужный формат
        self.region = change_letter(self.region, " ", "_")
        if re.search(r'[^a-zA-Z \-]', self.region):
            self.region = change_letter(self.region, "й", "y")
            self.region = change_letter(self.region, "я", "ya")
            end_word = transliterate.translit(self.region, reversed=True)
            return end_word
        else:
            return self.region

    def write_app_data(self, num_text=None):  # Запись новых связок в базу
        num_text = num_text
        self.sql.execute(f"SELECT url FROM mydata WHERE url = '{self.url}'")
        new_id = str(uuid.uuid4())
        if self.sql.fetchone() is None:
            self.sql.execute(f"INSERT OR REPLACE INTO mydata VALUES (?, ?, ?, ?, ?)",
                             (new_id, self.transliter_region(), self.request_word, self.url, num_text))
            self.db.commit()
            self.print_id = str(new_id)
            self.print_base()
            print(f"Зарегистрированно! ID = {self.print_id}")
            return f"Зарегистрированно! ID = {self.print_id}"
        else:
            for value in self.sql.execute(f"SELECT * FROM mydata WHERE url = '{self.url}'"):
                self.print_id = str(value[0])
                self.print_base()
                print(f"Такая запись уже имеется! ID = {self.print_id}")
                return f"Такая запись уже имеется! ID = {self.print_id}"

    def print_base(self):
        for value in self.sql.execute(f"SELECT * FROM mydata"):
            print(value)

    def stat_request(self, stat_id=None):
        stat_id = stat_id
        for identifier, geo, request, url, num_ads in self.sql.execute(f"SELECT * FROM mydata"):
            if identifier == stat_id:
                print(f"Количество объявлений в связке '{geo} + {request}' = {num_ads}")
                return f"Количество объявлений в связке '{geo} + {request}' = {num_ads}"
