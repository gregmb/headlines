from appkeys import weather_key, currency_key
import datetime
import feedparser
from flask import Flask
from flask import make_response
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
             'iol': 'http://www.iol.co.za/cmlink/1.640'
}


DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'}


def get_value_with_fallback(key):

    """Return value whether key was user defined,
    stored in cookie, or default
    """
    
    if request.args.get(key):
        return request.args.get(key)
    elif request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


@app.route("/")
def home():
    """Return web page."""
    # get customized headlines, based on user input or default
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)
    # get customized weather based on user input or default
    city = get_value_with_fallback('city')
    weather = get_weather(city)
    # get customized currency data based on user input or default
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rate(currency_from, currency_to)
    response = make_response(render_template(
        'home.html',
        articles=articles,
        weather=weather,
        currency_from=currency_from,
        currency_to=currency_to,
        rate=rate,
        currencies=sorted(currencies)
    ))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie('publication', publication, expires=expires)
    response.set_cookie('city', city, expires=expires)
    response.set_cookie('currency_from', currency_from, expires=expires)
    response.set_cookie('currency_to', currency_to, expires=expires)
    return response


def get_news(query):
    """Return articles for selected newsfeed."""
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(city):
    """Return weather data for given city."""
    cityid = city_id(city)
    params = {
        'appid': weather_key,
        'id': cityid,
        'units': 'imperial'
    }
    rawdata = requests.get(weather_url, params=params)
    parseddata = rawdata.json()
    weather = None
    if parseddata.get('weather'):
        weather = {
            'description': parseddata['weather'][0]['description'],
            'temperature': parseddata['main']['temp'],
            'city': parseddata['name'],
            'country': parseddata['sys']['country']
        }
    return weather


def get_rate(frm, to):
    """Return exchange rate for selected currencies."""
    params = {'app_id': currency_key}
    all_currency = requests.get(currency_url, params=params)
    parseddata = all_currency.json().get('rates')
    frm_rate = parseddata.get(frm.upper())
    to_rate = parseddata.get(to.upper())
    return (to_rate/frm_rate, parseddata.keys())


def city_id(rawcity):
    """Returns city id used by openWeather API from user input."""
    with open('city.list.json', encoding='utf-8') as f:
        citycodes = json.load(f)
    rawcity += ', '
    name, country = rawcity.split(',')[:2]
    name, country = name.strip().capitalize(), country.strip().upper()
    if country == 'UK':
        country = 'GB'
    if name in 'New york city':
        name = 'Manhattan'        
    codes = [(x['id'], x['country']) for x in citycodes if x['name'] == name]
    if country:
        city_id = [x for (x, y) in codes if y == country]
    else:
        city_id = codes[0]
    # Just using first city returned in the case of multiple for a
    # single country (US). Will return later to try parsing per state.
    return city_id[0]


if __name__ == '__main__':
    app.run(port=5000, debug=True)
