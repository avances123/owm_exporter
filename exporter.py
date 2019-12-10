#!/usr/bin/env python
import logging
import requests
import re
import time
import options

from prometheus_client import start_http_server, Gauge
import pyowm


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)



class OWMExporter:
    def __init__(self, options):
        self.owm = pyowm.OWM( options['owm_api_key'])
        self.gauge = Gauge("temperature", "", ['city'])

    def report_metrics(self, city):
        w = self.owm.weather_at_place(city).get_weather()
        temp = w.get_temperature('celsius')['temp']
        self.gauge.labels(city).set(temp)        

if __name__ == "__main__":
  options = options.get()
  exporter = OWMExporter(options)
  start_http_server(int(options['endpoint_port']))
  while True:
    for city in options['cities'].split(','):
      exporter.report_metrics(city)
    time.sleep(int(options['scrape_interval']))