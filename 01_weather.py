# -*- coding: utf-8 -*-

# В очередной спешке, проверив приложение с прогнозом погоды, вы выбежали
# навстречу ревью вашего кода, которое ожидало вас в офисе.
# И тут же день стал хуже - вместо обещанной облачности вас встретил ливень.

# Вы промокли, настроение было испорчено, и на ревью вы уже пришли не в духе.
# В итоге такого сокрушительного дня вы решили написать свою программу для прогноза погоды
# из источника, которому вы доверяете.

# Для этого вам нужно:

# Создать модуль-движок с классом WeatherMaker, необходимым для получения и формирования предсказаний.
# В нём должен быть метод, получающий прогноз с выбранного вами сайта (парсинг + re) за некоторый диапазон дат,
# а затем, получив данные, сформировать их в словарь {погода: Облачная, температура: 10, дата:datetime...}

# Добавить класс ImageMaker.
# Снабдить его методом рисования открытки
# (использовать OpenCV, в качестве заготовки брать lesson_016/python_snippets/external_data/probe.jpg):
#   С текстом, состоящим из полученных данных (пригодится cv2.putText)
#   С изображением, соответствующим типу погоды
# (хранятся в lesson_016/python_snippets/external_data/weather_img ,но можно нарисовать/добавить свои)
#   В качестве фона добавить градиент цвета, отражающего тип погоды
# Солнечно - от желтого к белому
# Дождь - от синего к белому
# Снег - от голубого к белому
# Облачно - от серого к белому

# Добавить класс DatabaseUpdater с методами:
#   Получающим данные из базы данных за указанный диапазон дат.
#   Сохраняющим прогнозы в базу данных (использовать peewee)

# Сделать программу с консольным интерфейсом, постаравшись все выполняемые действия вынести в отдельные функции.
# Среди действий, доступных пользователю, должны быть:
#   Добавление прогнозов за диапазон дат в базу данных
#   Получение прогнозов за диапазон дат из базы
#   Создание открыток из полученных прогнозов
#   Выведение полученных прогнозов на консоль
# При старте консольная утилита должна загружать прогнозы за прошедшую неделю.

# Рекомендации:
# Можно создать отдельный модуль для инициализирования базы данных.
# Как далее использовать эту базу данных в движке:
# Передавать DatabaseUpdater url-путь
# https://peewee.readthedocs.io/en/latest/peewee/playhouse.html#db-url
# Приконнектится по полученному url-пути к базе данных
# Инициализировать её через DatabaseProxy()
# https://peewee.readthedocs.io/en/latest/peewee/database.html#dynamically-defining-a-database

import argparse
import datetime
import weather_maker
import image_maker
import database_updater

URL = 'https://weather.com/ru-RU/weather/tenday/l/' \
      '34f2aafc84cff75ae0b014754856ea5e7f8ddf618cf9735549dfb5e016c28e10'
TODAY = datetime.date.today()
parser = argparse.ArgumentParser(description='Прогноз подгоды. \n'
                                             'Выберите действие: \n'
                                             '1. Добавление прогнозов за диапазон дат в базу данных \n '
                                             '2. Получение прогнозов за диапазон дат из базы \n'
                                             '3. Создание открыток из полученных прогнозов \n'
                                             '4. Выведение полученных прогнозов на консоль')
parser.add_argument('action', type=int, help='Действие пользователя')
parser.add_argument('start_date', type=str, help='Дата начала прогноза в формате dd.mm.yyyy')
parser.add_argument('end_date', type=str, help='Дата окончания прогноза в формате dd.mm.yyyy')
args = parser.parse_args()

if __name__ == '__main__':
    delta = int(str(datetime.datetime.strptime(args.end_date, '%d.%m.%Y') -
                    datetime.datetime.strptime(args.start_date, '%d.%m.%Y')).split(' ')[0])
    next_date = (datetime.datetime.strptime(args.start_date, '%d.%m.%Y') + datetime.timedelta(days=1)).strftime(
        '%d.%m.%Y')
    dates_list = []
    for _ in range(delta + 1):
        dates_list.append(args.start_date)
        args.start_date = (
                    datetime.datetime.strptime(args.start_date, '%d.%m.%Y') + datetime.timedelta(days=1)).strftime(
            '%d.%m.%Y')
    for date in dates_list:
        if args.action == 1:
            update_database = database_updater.DatabaseUpdater(URL, date)
            update_database.write_to_database()
        elif args.action == 2:
            make_weather = weather_maker.WeatherMaker(URL)
            make_weather.parsing_weathercom_site()
        elif args.action == 3:
            make_postcards = image_maker.ImageMaker(URL, date)
            make_postcards.run()
        elif args.action == 4:
            update_database = database_updater.DatabaseUpdater(URL, date)
            update_database.get_data()

# зачет!
