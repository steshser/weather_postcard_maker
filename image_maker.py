import re
import cv2 as cv
import numpy as np
import datetime
from weather_maker import WeatherMaker
from database_updater import Weather

URL = 'https://weather.com/ru-RU/weather/tenday/l/' \
      '34f2aafc84cff75ae0b014754856ea5e7f8ddf618cf9735549dfb5e016c28e10'
TODAY = datetime.date.today()
SUN_IMAGE = 'weather_img/sun.jpg'
RAIN_IMAGE = 'weather_img/rain.jpg'
SNOW_IMAGE = 'weather_img/snow.jpg'
CLOUD_IMAGE = 'weather_img/cloud.jpg'
BACKGROUND_IMAGE = 'background.jpg'


class ImageMaker(WeatherMaker):

    def __init__(self, url, date, value=0, value_min=255, edge=300):
        super().__init__(url)
        self.value = value
        self.value_min = value_min
        self.edge = edge
        self.date = date
        self.b = 0
        self.g = 0
        self.r = 0
        self.weather_img = None
        self.postcard = cv.imread(BACKGROUND_IMAGE)

    def postcard_color_and_weather_img(self):
        weather = Weather.get(Weather.date == self.date).weather
        sun_pattern = r'[Сс]ол'
        rain_pattern = r'[Дд]ож'
        snow_pattern = r'[Сс]не'
        cloud_pattern = r'[Оо]бл'
        # Солнечно - от желтого к белому
        if re.search(sun_pattern, weather):
            self.b = 0
            self.g = 255
            self.r = 255
            self.weather_img = cv.imread(SUN_IMAGE)
        # Дождь - от синего к белому
        elif re.search(rain_pattern, weather):
            self.b = 255
            self.g = 0
            self.r = 0
            self.weather_img = cv.imread(RAIN_IMAGE)
        # Снег - от голубого к белому
        elif re.search(snow_pattern, weather):
            self.b = 255
            self.g = 205
            self.r = 0
            self.weather_img = cv.imread(SNOW_IMAGE)
        # Облачно - от серого к белому
        elif re.search(cloud_pattern, weather):
            self.b = 154
            self.g = 154
            self.r = 154
            self.weather_img = cv.imread(CLOUD_IMAGE)
        else:
            print('Такая погода не учтена')
        return self.b, self.g, self.r, self.weather_img

    def make_gradient_postcard(self):
        # write colored rectangle
        cv.rectangle(self.postcard, (0, 0), (self.postcard.shape[1], self.postcard.shape[0]), (self.b, self.g, self.r),
                     -1)
        # create gradient
        gradient = self.create_gradient(self.postcard.shape[1], self.postcard.shape[0])
        # merge image with gradient
        self.postcard = cv.addWeighted(self.postcard, 0.5, gradient, 0.5, 0)
        temperature_for_postcard = Weather.get(Weather.date == self.date).temperature
        weather_for_postcard = Weather.get(Weather.date == self.date).weather
        cv.putText(self.postcard, temperature_for_postcard, (100, 100),
                   cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
        cv.putText(self.postcard, weather_for_postcard, (100, 200),
                   cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1)
        # I want to put logo on top-left corner, So I create a ROI
        rows_weather_img, cols_weather_img, channels_weather_img = self.weather_img.shape
        rows_postcard, cols_postcard, channels_postcard = self.postcard.shape
        roi = self.postcard[0:rows_weather_img, (cols_postcard - cols_weather_img):cols_postcard]
        # Now create a mask of logo and create its inverse mask also
        weather_img_gray = cv.cvtColor(self.weather_img, cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(weather_img_gray, 10, 255, cv.THRESH_BINARY)
        mask_inv = cv.bitwise_not(mask)
        # Now black-out the area of logo in ROI
        postcard_bg = cv.bitwise_and(roi, roi, mask=mask_inv)
        # Take only region of logo from logo image.
        weather_img_fg = cv.bitwise_and(self.weather_img, self.weather_img, mask=mask)
        # Put logo in ROI and modify the main image
        dst = cv.add(postcard_bg, weather_img_fg)
        self.postcard[0:rows_weather_img, (cols_postcard - cols_weather_img):cols_postcard] = dst
        postcard_name = 'postcard_{}.png'.format(str(self.date))
        cv.imwrite(postcard_name, self.postcard)

    def create_gradient(self, width, height):
        # Create blank image
        gradient = np.zeros((height, width, 3), np.uint8)
        # go through all lines of pixels horizontally
        for x in range(0, width):
            # if value is smaller than value_min make all pixels value_min
            if self.value >= self.value_min:
                gradient[0:height, x] = (self.value_min, self.value_min, self.value_min)
            # make all lines of pixels = value
            else:
                gradient[0:height, x] = (self.value, self.value, self.value)
                # decrease value so that it reaches 0 by x = edge
                self.value = self.value + (255 / self.edge)
        return gradient

    def run(self):
        self.postcard_color_and_weather_img()
        self.make_gradient_postcard()

