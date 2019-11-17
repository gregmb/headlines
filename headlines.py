import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import requests


app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}


DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK'}


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
    return(render_template("home.html", articles=articles,
                           weather=weather))


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return(feed['entries'])


def get_weather(city):
    api_url = 'http://api.openweathermap.org/data/2.5/weather'
    cityid = city_id(city)
    params = {'appid': 'ec152d53a4c74873d56523adabb25269', 'id': cityid,
              'units': 'imperial'}
    data = requests.get(api_url, params=params)
    parsed = data.json()
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed["weather"][0]["description"],
                   'temperature': parsed["main"]["temp"],
                   'city': parsed["name"]
                   }
    return(weather)


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
