import os
from sys import path
from sources import KNOWN_NEWS_SOURCES
import pymongo
import requests
from bs4 import BeautifulSoup
import pytz
tz = pytz.timezone('Asia/Kolkata')
from datetime import datetime,timezone
from dateutil.tz import *

import csv
from csv import writer

f = open("Deccan-Chronicle-Scraped-News.csv",'w', encoding='utf-8')
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
    if(isWordPresent(link,"entertainment")):
        return 'entertainment'
    if(isWordPresent(link,"world")):
        return 'worldnews'
    if(isWordPresent(link,"business")):
        return 'business'
    if(isWordPresent(link,"politics")):
        return 'politics'
    if(isWordPresent(link,"technology")):
        return 'technology'
    if(isWordPresent(link,"nation")):
        return 'nationalnews'
    return 'others'

def headlines(containers,i):
    myclient = pymongo.MongoClient("mongodb+srv://naveen:123@scrapedclusters.hpwgr.mongodb.net/userdata?retryWrites=true&w=majority")
    mydb = myclient["userdata"]
    mycol = mydb["newsrecord"]
    for container in containers:
        newswebsite="Deccan-Chronical"
        scraped_date=datetime.now(timezone.utc).astimezone(tz).isoformat()
        title=container.find(['h3', 'h2']).contents[0].strip()
        time= container.find("span", {"class": "SunChDt2"})
        if i==1:
            link=container.div.find('a').get('href')
            link= "https://www.deccanchronicle.com" + link
            content= container.find("div", {"class": "OpinionStrapList"}).getText()
        else:
            link=container.find('a').get('href')
            link= "https://www.deccanchronicle.com" + link
            content = "NA"
        if time is None:
            published_date=datetime.now(timezone.utc).astimezone(tz).isoformat()
        else:
            published_date = time.contents[0].strip()
            published_date = datetime.strptime(published_date,"%d %b %Y %I:%M %p").astimezone(tz).isoformat()
        category = category_scrapednews(link) 
        print("newswebsite""  "":" ,newswebsite)
        print("link""  "":" ,link)
        print("category"" "":" ,category)
        print("title""  "":" ,title)
        print("scraped_date""  "":" ,scraped_date)
        print("published_date""  "":", published_date)
        print("content""  "":" , content.strip())
        print()
        with open('Deccan-Chronicle-Scraped-News.csv', 'a+', encoding='utf-8') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow([newswebsite,link,category,title,scraped_date,published_date,content.strip()])
    return None

def  get_trending_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("div", {"class": "col-sm-12 col-xs-12 tstry-feed-sml-a"})
    headlines(containers,0)
    return None

def  get_chronological_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.findAll("div", {"class": "col-sm-12 SunChNewListing"})
    headlines(containers,1)
    return None
    
def output():
    SRC = KNOWN_NEWS_SOURCES["Deccan Chronicle"]
    get_chronological_headlines(SRC["pages"].format(1))
    get_trending_headlines(SRC["home"].format(1))
    return None

if __name__ == "__main__":
    output()