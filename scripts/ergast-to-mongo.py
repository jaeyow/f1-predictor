import requests
import json
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('MONGO_DB_USER')
password = os.getenv('MONGO_DB_PW')
conn_str = 'mongodb+srv://{username}:{password}@cluster0.pagvf.mongodb.net/f1Oracle?retryWrites=true&w=majority'
print(conn_str)
connect = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

seasons = requests.get("https://ergast.com/api/f1/seasons.json?limit=100")
f1_seasons = json.loads(seasons.text)["MRData"]["SeasonTable"]["Seasons"]


def write_races_to_db():
    # Write Races to DB
    try:
        print("Connected successfully!!!")
        db = connect.f1Oracle
        collection = db.races

        print('Writing races to Mongo...')
        for season in f1_seasons:
            race_schedule = requests.get(f"http://ergast.com/api/f1/{season['season']}.json")
            races = json.loads(race_schedule.text)["MRData"]["RaceTable"]["Races"]
            for race in races:
                # add weather to the DB now to save time later when preparing the data for EDA and model creation                 
                # race['weather'] = get_race_weather_from_wikipedia(race['url'])
                # collection.insert_one(race)
                print('collection.insert_one...')
        print('Writing races to Mongo... DONE')

    except Exception as e: # work on python 3.x
        print('Failed Mongo: '+ str(e))
        
def write_drivers_to_db():
    # Write Drivers to DB
    print("Connected successfully!!!")
    db = connect.f1Oracle
    collection = db.drivers

    print('Writing drivers to Mongo...')
    cts = requests.get(f"https://ergast.com/api/f1/drivers.json?limit=1000")
    drivers = json.loads(cts.text)["MRData"]["DriverTable"]["Drivers"]
    for driver in drivers:
        collection.insert_one(driver)
    print('Writing drivers to Mongo... DONE')        

def write_circuits_to_db():
    # Write Circuits to DB
    print("Connected successfully!!!")
    db = connect.f1Oracle
    collection = db.circuits

    print('Writing circuits to Mongo...')
    cts = requests.get(f"http://ergast.com/api/f1/circuits.json?limit=100")
    circuits = json.loads(cts.text)["MRData"]["CircuitTable"]["Circuits"]
    for circuit in circuits:
        collection.insert_one(circuit)
        print('Writing circuits to Mongo... DONE')
    
def write_raceresults_to_db():
    # Write Results to DB
    try:
        print("Connected successfully!!!")
        db = connect.f1Oracle
        collection = db.results

        print('Writing results to Mongo...')
        for season in f1_seasons:
            season_results = requests.get(f"http://ergast.com/api/f1/{season['season']}/results.json?limit=1000")
            races = json.loads(season_results.text)["MRData"]["RaceTable"]["Races"]
            for race_results in races:
                race_results['weather'] = get_race_weather_from_db(race_results['season'], race_results['round'])
                collection.insert_one(race_results)
        print('Writing results to Mongo... DONE')

    except Exception as e: # work on python 3.x
        print('Failed Mongo: '+ str(e))
        
def get_race_weather_from_db(season, round):
    db = connect.f1Oracle
    collection = db.races
    races = list(collection.find({}))
    races = [race for race in races if (race['season'] == season and race['round'] == round)]
    return races[0]['weather']
        
def get_race_weather_from_wikipedia(link):
    info = 'none'
    try:
        df = pd.read_html(link)[0]
        if 'Weather' in list(df.iloc[:,0]):
            n = list(df.iloc[:,0]).index('Weather')
            info = df.iloc[n,1]
        else:
            df = pd.read_html(link)[1]
            if 'Weather' in list(df.iloc[:,0]):
                n = list(df.iloc[:,0]).index('Weather')
                info = df.iloc[n,1]
            else:
                df = pd.read_html(link)[2]
                if 'Weather' in list(df.iloc[:,0]):
                    n = list(df.iloc[:,0]).index('Weather')
                    info = df.iloc[n,1]
                else:
                    df = pd.read_html(link)[3]
                    if 'Weather' in list(df.iloc[:,0]):
                        n = list(df.iloc[:,0]).index('Weather')
                        info = df.iloc[n,1]
                    else:
                        driver = webdriver.Chrome()
                        driver.get(link)

                        # italian page
                        button = driver.find_element_by_link_text('Italiano')
                        button.click()
                        info = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[9]/td').text

    except:
        info = 'Sunny' # Default to Sunny

    return info

write_races_to_db()
# write_drivers_to_db()
# write_circuits_to_db()
# write_raceresults_to_db()