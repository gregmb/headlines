from appkeys import weather_key, currency_key
import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import requests


app = Flask(__name__)

weather_url = 'http://api.openweathermap.org/data/2.5/weather'
currency_url = 'https://openexchangerates.org//api/latest.json'

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}


DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_frm': 'GBP',
            'currency_to': 'USD'}


@app.route("/")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get("publication")
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    # get customized currency data based on user input or default
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_frm']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate = get_rate(currency_from, currency_to)
    return(render_template("home.html", articles=articles,
                           weather=weather,
                           currency_from=currency_from,
                           currency_to=currency_to,
                           rate=rate))


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return(feed['entries'])


def get_weather(city):
    cityid = city_id(city)
    params = {'appid': weather_key, 'id': cityid,
              'units': 'imperial'}
    data = requests.get(weather_url, params=params)
    parsed = data.json()
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'], 'country': parsed['sys']['country']
                   }
    return(weather)


def get_rate(frm, to):
    params = {'app_id': currency_key}
    all_currency = requests.get(currency_url, params=params)
    parsed = all_currency.json()['rates']
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return(to_rate/frm_rate)


def city_id(input):
    # This function is to transform the city, country input into
    # the city id used by openWeather API.
    with open('city.list.json') as f:
        cityCodes = json.load(f)
    input += ', '
    name, country = input.split(',')[:2]
    name, country = name.strip().capitalize(), country.strip().upper()
    if country == 'UK':
        country = 'GB'
    codes = [(x['id'], x['country']) for x in cityCodes if x['name'] == name]
    if country:
        city_id = [x for (x, y) in codes if y == country]
    else:
        city_id = codes[0]
    # Just using first city returned in the case of multiple for a
    # single country (US). Will return later to try parsing per state.
    return(city_id[0])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
