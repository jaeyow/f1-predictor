try:
    import unzip_requirements
except ImportError:
    pass
  
from flask import Flask, jsonify, make_response, request
from sklearn.ensemble import BaggingRegressor
from sklearn.tree import DecisionTreeRegressor
import numpy as np
import pandas as pd
from numpy import genfromtxt

import pickle

model = pickle.load(open('f1-model.pkl','rb'))
app = Flask(__name__)

@app.route("/")
def hello_from_root():
  return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
  return jsonify(message='Hello from path!')

@app.route('/predict')
def predict():
    season = int(request.args.get('season'))
    round = int(request.args.get('round'))
    if (season == 2021 and (round > 0 and round <= 21)):
      X_test = pd.read_csv(f'./csvs/{season}_{round}.csv')
      X_test.drop(columns=['Unnamed: 0'],inplace=True)  
      prediction = model.predict(X_test)
      return jsonify(prediction.tolist())
    else:
      return make_response(jsonify(error='season and round are required arguments, or are invalid values'), 404)

@app.errorhandler(404)
def resource_not_found(e):
  return make_response(jsonify(error='Not found!'), 404)
