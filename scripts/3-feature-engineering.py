import numpy as np
import pandas as pd
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

results_df = pd.read_csv('./csvs/results_from_mongo.csv')
results_df.drop(columns=['Unnamed: 0'],inplace=True)
results_df

# only keep 2021 for the api
api_df = results_df[results_df['Season']==2021]
api_df.reset_index(drop=True, inplace=True)
api_df.to_csv(f'2021_races_drivers.csv')
api_df.to_csv(f'./flask-api/2021_races_drivers.csv')

# Feature Engineering - Driver Experience
print('Feature Engineering - Driver Experience')
results_df['DriverExperience'] = 0
drivers = results_df['Driver'].unique()
for driver in drivers:
    df_driver = pd.DataFrame(results_df[results_df['Driver']==driver]).tail(60) # Arbitrary number, just look at the last x races
    df_driver.loc[:,'DriverExperience'] = 1
    
    results_df.loc[results_df['Driver']==driver, "DriverExperience"] = df_driver['DriverExperience'].cumsum()
    results_df['DriverExperience'].fillna(value=0,inplace=True)

print('Feature Engineering - Constructor Experience')
# Feature Engineering - Constructor Experience
results_df['ConstructorExperience'] = 0
constructors = results_df['Constructor'].unique()
for constructor in constructors:
    
    df_constructor = pd.DataFrame(results_df[results_df['Constructor']==constructor]).tail(60) # Arbitrary number, just look at the last x races per driver
    df_constructor.loc[:,'ConstructorExperience'] = 1
    
    results_df.loc[results_df['Constructor']==constructor, "ConstructorExperience"] = df_constructor['ConstructorExperience'].cumsum()
    results_df['ConstructorExperience'].fillna(value=0,inplace=True)

print('Feature Engineering - Driver Recent Wins')
# Feature Engineering - Driver Recent Wins
results_df['DriverRecentWins'] = 0
drivers = results_df['Driver'].unique()

results_df.loc[results_df['Position']==1, "DriverRecentWins"] = 1
for driver in drivers:
    mask_first_place_drivers = (results_df['Driver']==driver) & (results_df['Position']==1)
    df_driver = results_df[mask_first_place_drivers]
    results_df.loc[results_df['Driver']==driver, "DriverRecentWins"] = results_df[results_df['Driver']==driver]['DriverRecentWins'].rolling(60).sum() # 60 races, about 3 years rolling
    results_df.loc[mask_first_place_drivers, "DriverRecentWins"] = results_df[mask_first_place_drivers]['DriverRecentWins'] - 1  # but don't count this race's win
    results_df['DriverRecentWins'].fillna(value=0,inplace=True)

print('Feature Engineering - Driver Recent DNFs')
# Feature Engineering - Driver Recent DNFs
results_df['DriverRecentDNFs'] = 0
drivers = results_df['Driver'].unique()

results_df.loc[(~results_df['Status'].str.contains('Finished|\+')), "DriverRecentDNFs"] = 1
for driver in drivers:
    mask_not_finish_place_drivers = (results_df['Driver']==driver) & (~results_df['Status'].str.contains('Finished|\+'))
    df_driver = results_df[mask_not_finish_place_drivers]
    results_df.loc[results_df['Driver']==driver, "DriverRecentDNFs"] = results_df[results_df['Driver']==driver]['DriverRecentDNFs'].rolling(60).sum() # 60 races, about 3 years rolling
    results_df.loc[mask_not_finish_place_drivers, "DriverRecentDNFs"] = results_df[mask_not_finish_place_drivers]['DriverRecentDNFs'] - 1  # but don't count this race
    results_df['DriverRecentDNFs'].fillna(value=0,inplace=True)

print('Feature Engineering - Fix Recent Form Points')
# Feature Engineering - Fix Recent Form Points
# Add new RFPoints column - ALL finishers score points - max points First place and one less for each lesser place (using LogSpace)
seasons = results_df['Season'].unique()
results_df['RFPoints'] = 0
for season in seasons:
    rounds = results_df[results_df['Season']==season]['Round'].unique()
    for round in rounds:
        mask = (results_df['Season']==season) & (results_df['Round']==round)
        finisher_mask = ((results_df['Status'].str.contains('Finished|\+'))) # Count only if finished the race
        finished_count = results_df.loc[(mask) & finisher_mask, "RFPoints"].count()
        point_list = np.round(np.logspace(1,4,40, base=4),4) # use list of LogSpaced numbers
        point_list[::-1].sort()
        
        results_df.loc[(mask) & finisher_mask, "RFPoints"] = point_list[:finished_count].tolist()

print('Feature Engineering - Driver Recent Form')
# Feature Engineering - Driver Recent Form
results_df['DriverRecentForm'] = 0
# for all drivers, calculate the rolling X DriverRecentForm and add to a new column in 
# original data frame, this represents the 'recent form', then for NA's just impute to zero
drivers = results_df['Driver'].unique()
for driver in drivers:
    df_driver = results_df[results_df['Driver']==driver]
    results_df.loc[results_df['Driver']==driver, "DriverRecentForm"] = df_driver['RFPoints'].rolling(30).sum() - df_driver['RFPoints'] # calcluate recent form points but don't include this race's points
    results_df['DriverRecentForm'].fillna(value=0,inplace=True)

print('Feature Engineering - Constructor Recent Form')
# Feature Engineering - Constructor Recent Form
results_df['ConstructorRecentForm'] = 0
# for all constructors, calculate the rolling X RFPoints and add to a new column in 
# original data frame, this represents the 'recent form', then for NA's just impute to zero
constructors = results_df['Constructor'].unique()
for constructor in constructors:
    df_constructor = results_df[results_df['Constructor']==constructor]
    results_df.loc[results_df['Constructor']==constructor, "ConstructorRecentForm"] = df_constructor['RFPoints'].rolling(30).sum() - df_constructor['RFPoints'] # calcluate recent form points but don't include this race's points
    results_df['ConstructorRecentForm'].fillna(value=0,inplace=True)

print('Feature Engineering - Driver Age')
# Feature Engineering - Driver Age
def calculate_age(born, race):
    date_born = datetime.strptime(born,'%Y-%m-%d')
    date_race = datetime.strptime(race,'%Y-%m-%d')
    return date_race.year - date_born.year - ((date_race.month, date_race.day) < (date_born.month, date_born.day))

results_df['Age'] = results_df.apply(lambda x: calculate_age(x['DOB'], x['Race Date']), axis=1) 

print('Feature Engineering - Home Circuit')
# Feature Engineering - Home Circuit
def is_race_in_home_country(driver_nationality, race_country):
    nationality_country_map = {
        'American': ['USA'],
        'American-Italian': ['USA','Italy'],
        'Argentine': ['Argentina'],
        'Argentine-Italian': ['Argentina','Italy'],
        'Australian': ['Australia'],
        'Austrian': ['Austria'],
        'Belgian': ['Belgium'],
        'Brazilian': ['Brazil'],
        'British': ['UK'],
        'Canadian': ['Canada'],
        'Chilean': ['Brazil'],
        'Colombian': ['Brazil'],
        'Czech': ['Austria','Germany'],
        'Danish': ['Germany'],
        'Dutch': ['Netherlands'],
        'East German': ['Germany'],
        'Finnish': ['Germany','Austria'],
        'French': ['France'],
        'German': ['Germany'],
        'Hungarian': ['Hungary'],
        'Indian': ['India'],
        'Indonesian': ['Singapore','Malaysia'],
        'Irish': ['UK'],
        'Italian': ['Italy'],
        'Japanese': ['Japan','Korea'],
        'Liechtensteiner': ['Switzerland','Austria'],
        'Malaysian': ['Malaysia','Singapore'],
        'Mexican': ['Mexico'],
        'Monegasque': ['Monaco'],
        'New Zealander': ['Australia'],
        'Polish': ['Germany'],
        'Portuguese': ['Portugal'],
        'Rhodesian': ['South Africa'],
        'Russian': ['Russia'],
        'South African': ['South Africa'],
        'Spanish': ['Spain','Morocco'],
        'Swedish': ['Sweden'],
        'Swiss': ['Switzerland'],
        'Thai': ['Malaysia'],
        'Uruguayan': ['Argentina'],
        'Venezuelan': ['Brazil']
    }
    
    countries = ['None']
    
    try:
      countries = nationality_country_map[driver_nationality]
    except:
      print("An exception occurred, This driver has no race held in his home country.")
    return race_country in countries

results_df['IsHomeCountry'] = results_df.apply(lambda x: is_race_in_home_country(x['Nationality'], x['Country']), axis=1) 

print('Feature Engineering - Dummify categorical features')
# Feature Engineering - Dummify categorical features
results_df = pd.get_dummies(results_df, columns = ['Weather', 'Nationality', 'Race Name'],drop_first=True)

for col in results_df.columns:
    if 'Nationality' in col and results_df[col].sum() < 300:
        results_df.drop(col, axis = 1, inplace = True)
        
    elif 'Race Name' in col and results_df[col].sum() < 130:
        results_df.drop(col, axis = 1, inplace = True)
        
    else:
        pass

print('Feature Engineering - Drop Columns which are not needed/required for modelling')
# Feature Engineering - Drop Columns which are not needed/required for modelling
results_df.drop(['Race Date', 'Race Time', 'Status', 'DOB', 'Constructor', 'Constructor Nat', 'Circuit Name',
                 'Race Url', 'Lat', 'Long', 'Locality', 'Country','Laps','Points',
                 'RFPoints'], axis=1, inplace=True)
results_df.shape

print('Feature Engineering - convert Season to numeric')
# Feature Engineering - convert Season to numeric
results_df['Season'] = pd.to_numeric(results_df['Season'])
results_df.columns

results_df.to_csv('./csvs/feature_engineering.csv')
