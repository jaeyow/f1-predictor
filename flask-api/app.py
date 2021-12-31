from flask import Flask, jsonify, make_response, request
import pandas as pd
import numpy as np
from timeit import default_timer as timer
import pickle

# this is our machine learning model
model = pickle.load(open('f1-model.pkl','rb'))
app = Flask(__name__)

@app.route('/predict',methods = ['POST', 'GET'])
def predict():
    season = int(request.args.get('season'))
    round = int(request.args.get('round'))
    
    # this mvp only works for all races in season 2021
    if (season == 2021 and (round > 0 and round <= 21)):
      # work with csv files for now
      X_indie_df = pd.read_csv(f'./csvs/{season}_{round}.csv')
      X_indie_df.drop(columns=['Unnamed: 0'],inplace=True)
      
      drivers_csv_df = pd.read_csv(f'./csvs/2021_races_drivers.csv')
      drivers_df = drivers_csv_df[(drivers_csv_df['Season'] == 2021) & (drivers_csv_df['Round'] == round)]
      start = timer()
      prediction_df = pd.DataFrame(model.predict(X_indie_df), columns = ['Prediction'])
      merged_df = pd.concat([prediction_df, drivers_df[['Driver']].reset_index(drop=True)], axis=1)
      
      # shuffle, then sort
      merged_df = merged_df.sample(frac=1).reset_index(drop=True)
      merged_df.sort_values(by='Prediction', ascending=False, inplace=True)
      merged_df.reset_index(drop=True, inplace=True)
      end = timer()
      
      # arrange for api output 
      return make_response({
        'Prediction Time': f'{np.round(end - start, 5)} sec',
        'Season': season,
        'Round': round,
        'Results': [(Postions(index+1, row['Prediction'], row['Driver'])).toJSON() for index, row in merged_df.iterrows() ]
      }, 200)
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
    return {
      'Position': self.Position, 
      'Prediction': self.Prediction,
      'Driver': self.Driver
    }

 