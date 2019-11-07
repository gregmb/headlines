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


@app.route("/")
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    weather = get_weather("London,GB")
    return(render_template("home.html", articles=feed['entries'],
                           weather=weather))


def get_weather(query):
    api_url = 'http://api.openweathermap.org/data/2.5/weather'
    city = city_id(query)
    params = {'appid': 'ec152d53a4c74873d56523adabb25269', 'q': city}
    data = requests.get(api_url, params=params)
    parsed = json.loads(data)
    weather = None
    if parsed["weather"]:
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"], "city": parsed["name"]
                   }
    return weather
                        

def city_id(input):
    with open('city.list.json') as f:
        cityCodes = json.load(f)
    name, country = input.split(',')
    code = [x['id'] for x in cityCodes if x['name']==name and x['country']==country]
    return(code[0])
   
   
if __name__ == '__main__':
    app.run(port=5000, debug=True)
