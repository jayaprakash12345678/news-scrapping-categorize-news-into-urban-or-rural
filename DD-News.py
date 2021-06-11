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

f = open("DD-News-Scraped-News.csv",'w', encoding='utf-8')
headers =["newswebsite", "link", "category", "title", "scraped_date", "published_date", "content"]
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
    if(isWordPresent(link,"technology")):
        return 'technology'
    if(isWordPresent(link,"national")):
        return 'nationalnews'
    return 'others'


def headlines(containers,i):
    myclient = pymongo.MongoClient("mongodb+srv://naveen:123@scrapedclusters.hpwgr.mongodb.net/userdata?retryWrites=true&w=majority")
    mydb = myclient["userdata"]
    mycol = mydb["DD News"]
    for container in containers:
        datum={}
        newswebsite="DD-News"
        link=container.find('a').get('href')
        link="ddnews.gov.in" + link
        scraped_date=datetime.now(timezone.utc).astimezone(tz).isoformat()
        if i==1:
            time= container.find("p", {"class": "archive-date"}).getText()
            title = container.find("p", {"class": "archive-title"}).getText()
        else:
            time= container.find("p", {"class": "date"}).getText()
            title= container.find('a').getText()
        content="NA"
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
        with open('DD-News-Scraped-News.csv', 'a+', encoding='utf-8') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow([newswebsite,link,category,title,scraped_date,published_date,content.strip()])
    return None

def  get_trending_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("div", {"class": "item_list_cnt"})
    headlines(containers,0)
    return None

def  get_chronological_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("span", {"class": "field-content"})
    headlines(containers,1)
    return None
    
def output():
    SRC = KNOWN_NEWS_SOURCES["DD News"]
    get_chronological_headlines(SRC["pages"].format(1))
    get_trending_headlines(SRC["home"].format(1))
    return None

if __name__ == "__main__":
    print("ready to execute output() function:")
    output()