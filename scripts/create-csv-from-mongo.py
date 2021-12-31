import requests
import json
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('MONGO_DB_USER')
password = os.getenv('MONGO_DB_PW')
conn_str = f'mongodb+srv://{username}:{password}@cluster0.pagvf.mongodb.net/f1Oracle?retryWrites=true&w=majority'
connect = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

def get_categorical_weather(weather):
    weather = weather.replace(',',' ')
    weather = weather.replace('.',' ')
    weather = weather.replace(';',' ')
    weather = weather.replace("'",' ')
    weather = weather.replace('/',' ')
    weather = weather.replace('\xa0','.')
    weather_dict = {
        'weather_hot': ['hot'],
        'weather_warm': ['soleggiato', 'clear', 'warm', 'sunny', 'fine', 'mild', 'sereno'],
        'weather_cold': ['cold', 'fresh', 'chilly', 'cool'],
        'weather_dry': ['dry', 'asciutto'],
        'weather_wet': ['showers', 'wet', 'rain', 'pioggia', 'damp', 'thunderstorms', 'rainy', 'drizzly'],
        'weather_cloudy': ['overcast', 'nuvoloso', 'clouds', 'cloudy', 'grey', 'coperto']}
    
    categorical_weather = ''
    for key in weather_dict:
        categorical_weather = key if any(i in weather_dict[key] for i in weather.lower().split()) else 'No weather'
        if categorical_weather != 'No weather':
            break
        else:
            categorical_weather = 'weather_warm' # a few are formatted wierd, so impute to warm 
    return categorical_weather

def create_results_dataframe_from_db_collection():
    db = connect.f1Oracle
    collection = db.results
    races_results = list(collection.find({})) # MongoDB query about ~30 seconds

    for_da_result = {'Season':[],'Round':[],'Race Name':[],'Race Date':[],'Race Time':[],'Position':[],
                     'Points':[],'Grid':[],'Laps':[],'Status':[],'Driver':[],'DOB':[],
                     'Nationality':[],'Constructor':[],'Constructor Nat':[],'Circuit Name':[],'Race Url':[],
                     'Lat':[],'Long':[],'Locality':[],'Country':[],'Weather':[]}
        
    for race in races_results:
        for results in race['Results']:
            for_da_result['Season'].append(f"{race['season']}")
            for_da_result['Round'].append(int(race['round']))
            for_da_result['Race Name'].append(f"{race['raceName']}")
            for_da_result['Race Date'].append(f"{race['date']}")
            for_da_result['Race Time'].append(f"{race['time']}" if 'time' in results else '10:10:00Z')
            for_da_result['Position'].append(int(results['position']))
            for_da_result['Points'].append(float(results['points']))
            for_da_result['Grid'].append(int(results['grid']))
            for_da_result['Laps'].append(int(results['laps']))
            for_da_result['Status'].append(f"{results['status']}")
            for_da_result['Driver'].append(f"{results['Driver']['givenName']} {results['Driver']['familyName']}")
            for_da_result['DOB'].append(f"{results['Driver']['dateOfBirth']}")
            for_da_result['Nationality'].append(f"{results['Driver']['nationality']}")
            for_da_result['Constructor'].append(f"{results['Constructor']['name']}")
            for_da_result['Constructor Nat'].append(f"{results['Constructor']['nationality']}")
            for_da_result['Circuit Name'].append(f"{race['Circuit']['circuitName']}")
            for_da_result['Race Url'].append(f"{race['url']}")
            for_da_result['Lat'].append(f"{race['Circuit']['Location']['lat']}")
            for_da_result['Long'].append(f"{race['Circuit']['Location']['long']}")
            for_da_result['Locality'].append(f"{race['Circuit']['Location']['locality']}")
            for_da_result['Country'].append(f"{race['Circuit']['Location']['country']}")
            for_da_result['Weather'].append(f"{get_categorical_weather(race['weather'])}")
                
    return pd.DataFrame(for_da_result)

print('Creating csv results from MongoDb...')
inter_df = create_results_dataframe_from_db_collection()
inter_df.to_csv('./csvs/results_from_mongo.csv')
print('Creating csv results from MongoDb, DONE...')
