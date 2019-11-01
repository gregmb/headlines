import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import requests
from urllib.parse import urlencode, puote_plus

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}



@app.route("/")
#@app.route("/<publication>")
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    weather = get_weather("London,UK")
    return(render_template("home.html", articles=feed['entries'],weather=weather))

def get_weather(query):
    api_url = 'http://apiopenweathermap.org/data/2.5/weather'?q={ }&appid
    params = {'appid' : 'ec152d53a4c74873d56523adabb25269', 'q' : city}}
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description":parsed["weather"][0]["description"],"temperature":parsed["main"]["temp"],"city":parsed["name"]
                  }
    return weather

if __name__ == '__main__':
    app.run(port=5000, debug=True)
