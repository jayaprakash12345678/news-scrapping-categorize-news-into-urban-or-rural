import os
from sys import path
from sources import KNOWN_NEWS_SOURCES
import pymongo
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pytz
tz = pytz.timezone('Asia/Kolkata')
from datetime import datetime,timezone
from dateutil.tz import *

import csv
from csv import writer

f = open("The-Hindu-Scraped-News.csv",'w', encoding='utf-8')
headers =["newswebsite", "link", "title", "category", "scraped_date", "published_date", "content"]
csvwriter = csv.writer(f)
csvwriter.writerow(headers)
f.close()


def isWordPresent(sentence, word):  
    s = sentence.split("/") 
    for i in s: 
        if (i == word): 
            return True
    return False


def category_scrapednews(link):
    if(isWordPresent(link,"sports")):
        return 'sports'
    if(isWordPresent(link,"international")):
        return 'internationalnews'
    if(isWordPresent(link,"business")):
        return 'business'
    if(isWordPresent(link,"national")):
        return 'nationalnews'
    return 'others'

def headlines(containers,i):
    myclient = pymongo.MongoClient("mongodb+srv://naveen:123@scrapedclusters.hpwgr.mongodb.net/userdata?retryWrites=true&w=majority")
    mydb = myclient["userdata"]
    mycol = mydb["The Hindu News"]
    for container in containers:
        datum = {}
        newswebsite="The-Hindu"
        link=container.find(['h3','h2'])
        link=link.find('a').get('href')
        scraped_date=datetime.now(timezone.utc).astimezone(tz).isoformat()
        title=container.find("span", {"class": "story-card-heading"})
        title=title.find("a", {"class": "section-name"}).getText()
        time= container.find(['h3','h2'])
        time= time.find('a').get('title')
        content = container.find(['h3','h2']).getText() 
        if time is None:
            published_date=datetime.now(timezone.utc).astimezone(tz).isoformat()
        else:
            published_date = time.strip()
        category = category_scrapednews(link)
        print("newswebsite""  "":" ,newswebsite)
        print("link""  "":" ,link)
        print("category"" "":" ,category)
        print("title""  "":" ,title.strip())
        print("scraped_date""  "":" ,scraped_date)
        print("published_date""  "":", published_date)
        print("content""  "":" , content.strip())
        print()
        datum['newswebsite'] = newswebsite
        datum['link'] = link
        datum['category'] = category
        datum['title'] = title
        datum['scraped_date'] = scraped_date
        datum['published_date'] = published_date
        datum['content'] = content.strip()
        mycol.insert_one(datum)
        with open('The-Hindu-Scraped-News.csv', 'a+', encoding='utf-8') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow([newswebsite,link,category,title,scraped_date,published_date,content.strip()])
    return None

def  get_trending_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("div", {"class": "story-card-news"})
    headlines(containers,0)
    return None

def  get_chronological_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("div", {"class": "story-card-news"})
    headlines(containers,1)
    return None
    
def output():
    SRC = KNOWN_NEWS_SOURCES["The Hindu"]
    get_chronological_headlines(SRC["pages"].format(1))
    get_trending_headlines(SRC["home"].format(1))
    return None

if __name__ == "__main__":
    output()