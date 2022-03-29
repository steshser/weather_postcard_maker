import re
import requests
import datetime
from bs4 import BeautifulSoup

URL = 'https://weather.com/ru-RU/weather/tenday/l/' \
      '34f2aafc84cff75ae0b014754856ea5e7f8ddf618cf9735549dfb5e016c28e10'
TODAY = datetime.date.today()


class WeatherMaker:

    def __init__(self, url):
        self.url = url
        self.today = TODAY
        self.headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/53.0.2785.116 Safari/537.36 OPR/40.0.2308.81',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate, lzma, sdch',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
        }
        self.date_weather_dict = {}
        self.list_of_dates = []
        self.list_of_temperature = []
        self.list_of_weather = []

    def parsing_weathercom_site(self):
        days_list = []
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            html_doc = BeautifulSoup(response.text, features='html.parser')
            self.list_of_dates = html_doc.find_all('h2', {'class': 'DetailsSummary--daypartName--2FBp2'})
            self.list_of_temperature = html_doc.find_all('span', {'data-testid': 'TemperatureValue'})
            self.list_of_weather = html_doc.find_all('span', {'class': 'DetailsSummary--extendedData--365A_'})

            for date, temperature, weather in zip(self.list_of_dates, self.list_of_temperature, self.list_of_weather):
                if re.match(r'[Сс]егодня', date.text):
                    self.date_weather_dict[self.today.strftime("%d.%m.%Y")] = {
                        'Температура': temperature.text[:-1], 'Погода': weather.text
                    }
                else:
                    day = int(date.text[-2:])
                    days_list.append(day)
                    if len(days_list) != 1:
                        for i in range(len(days_list)-1):
                            if days_list[i+1] < days_list[i]:
                                month = int(self.today.month+1)
                            else:
                                continue
                    else:
                        month = self.today.month
                    date = datetime.datetime(year=self.today.year, month=month, day=day)
                    self.date_weather_dict[date.strftime("%d.%m.%Y")] = {
                        'Температура': temperature.text[:-1], 'Погода': weather.text
                    }
        return self.date_weather_dict


