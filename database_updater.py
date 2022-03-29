import peewee
import datetime
from weather_maker import WeatherMaker

URL = 'https://weather.com/ru-RU/weather/tenday/l/' \
      '34f2aafc84cff75ae0b014754856ea5e7f8ddf618cf9735549dfb5e016c28e10'
TODAY = datetime.date.today()
DATABASE_NAME = 'weather.db'


class DatabaseUpdater(WeatherMaker):

    def __init__(self, url, input_date):
        super().__init__(url)
        self.date = input_date

    def write_to_database(self):
        date_weather_dict = self.parsing_weathercom_site()
        for self.date in date_weather_dict.keys():
            data = Weather.insert(date=self.date, temperature=date_weather_dict[self.date]['Температура'],
                                  weather=date_weather_dict[self.date]['Погода']
                                  ).on_conflict_replace()
            data.execute()

    def get_data(self):
        weather_data = Weather.get(Weather.date == self.date)
        print(f'Дата: {weather_data.date} Температура: {weather_data.temperature} Погода: {weather_data.weather}')


class BaseTable(peewee.Model):
    class Meta:
        database = peewee.SqliteDatabase(DATABASE_NAME)


class Weather(BaseTable):
    date = peewee.DateTimeField(unique=True)
    temperature = peewee.CharField()
    weather = peewee.CharField()
