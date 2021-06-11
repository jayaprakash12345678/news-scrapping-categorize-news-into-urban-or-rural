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

f = open("Telegraph-Scraped-News.csv",'w', encoding='utf-8')
headers =["newswebsite", "link", "title", "scraped_date", "published_date", "content"]
csvwriter = csv.writer(f)
csvwriter.writerow(headers)
f.close()


def headlines(containers,i):
    myclient = pymongo.MongoClient("mongodb+srv://naveen:123@scrapedclusters.hpwgr.mongodb.net/userdata?retryWrites=true&w=majority")
    mydb = myclient["userdata"]
    mycol = mydb["Telegraph News"]
    for container in containers:
        datum = {}
        newswebsite="Telegraph-News"
        if i==1:
            link=container.div.find('a').get('href')
            link= "https://www.telegraphindia.com/" + link
            title = container.find("a", {"class": "muted-link ellipsis_data_3"}).getText()
            content= container.find("div", {"class": "uk-text-69 uk-margin-small-top noto-regular uk-height-limit-section"}).getText()
        else:
            link=container.find('a').get('href')
            link= "https://www.telegraphindia.com/" + link
            title = container.find("div",{"class": "article"}).div.getText()
            content = container.find("div", {"class": "uk-text-69 uk-margin-small-top noto-regular uk-height-limit-xxsmall"}).getText()
        scraped_date=datetime.now(timezone.utc).astimezone(tz).isoformat()                                
        published_date=datetime.now(timezone.utc).astimezone(tz).isoformat()
        print("newswebsite""  "":" ,newswebsite)
        print("link""  "":" ,link)
        print("title""  "":" ,title.strip())
        print("scraped_date""  "":" ,scraped_date)
        print("published_date""  "":", published_date)
        print("content""  "":" , content.strip())
        print()
        datum['newswebsite'] = newswebsite
        datum['link'] = link
        datum['title'] = title.strip()
        datum['scraped_date'] = scraped_date
        datum['published_date'] = published_date
        datum['content'] = content.strip()
        mycol.insert_one(datum)
        with open('Telegraph-Scraped-News.csv', 'a+', encoding='utf-8') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow([newswebsite,link,title,scraped_date,published_date,content.strip()])
    return None

def  get_trending_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers=soup.find("div", {"class": "row mt-3 uk-grid-divider"})
    containers = containers.findAll("div", {"class": "col"})
    headlines(containers,0)
    return None

def  get_chronological_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("div", {"class": "col-3"})
    headlines(containers,1)
    return None
    
def output():
    SRC = KNOWN_NEWS_SOURCES["Telegraph"]
    get_chronological_headlines(SRC["pages"].format(1))
    get_trending_headlines(SRC["home"].format(1))
    return None

if __name__ == "__main__":
    output()