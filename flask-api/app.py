try:
    import unzip_requirements
except ImportError:
    pass
  
from flask import Flask, jsonify, make_response, request
import numpy as np
import pandas as pd
from timeit import default_timer as timer
import json

import pickle

model = pickle.load(open('f1-model.pkl','rb'))
app = Flask(__name__)

@app.route('/predict')
def predict():
    season = int(request.args.get('season'))
    round = int(request.args.get('round'))
    
    if (season == 2021 and (round > 0 and round <= 21)):
      # work with csv files for now
      X_test = pd.read_csv(f'./csvs/{season}_{round}.csv')
      X_test.drop(columns=['Unnamed: 0'],inplace=True)
      drivers_csv_df = pd.read_csv(f'./2021_races_drivers.csv')
      drivers = drivers_csv_df[(drivers_csv_df['Season'] == 2021) & (drivers_csv_df['Round'] == round)]
      start = timer()
      prediction_df = pd.DataFrame(model.predict(X_test), columns = ['Prediction'])
      merged_df = pd.concat([prediction_df, drivers[['Driver']].reset_index(drop=True)], axis=1)
      
      # shuffle, then sort
      merged_df = merged_df.sample(frac=1).reset_index(drop=True)
      merged_df.sort_values(by='Prediction', ascending=False, inplace=True)
      merged_df.reset_index(drop=True, inplace=True)
      end = timer()
      
      # arrange for api output 
      return {
        'Prediction Time': f'{end - start} s',
        'Season': season,
        'Round': round,
        'Results': [(Postions(index+1, row['Prediction'], row['Driver'])).toJSON() for index, row in merged_df.iterrows() ]
      }
    else:
      return make_response(jsonify(error='season and round are required arguments, or are invalid values'), 400)

@app.errorhandler(404)
def resource_not_found(e):
  return make_response(jsonify(error='Not found!'), 404)

class Postions:
   def __init__(self, pos, p, d):
       self.Position = pos
       self.Prediction = p 
       self.Driver = d


   def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, indent=4)

 