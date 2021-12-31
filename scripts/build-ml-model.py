import numpy as np
import pandas as pd
from timeit import default_timer as timer
from sklearn.metrics import precision_score
from sklearn.ensemble import BaggingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import MinMaxScaler
import pickle

import warnings
warnings.filterwarnings('ignore')

def regression_test_score(model, print_output=False):
    # --- Test ---
    score = 0
    races = model_df[(model_df['Season'] == 2021)]['Round'].unique()
    for race in races:
        test = model_df[(model_df['Season'] == 2021) & (model_df['Round'] == race)]
        X_test = test.drop(['Position','Driver'], axis = 1)
        y_test = test['Position']
        X_test = pd.DataFrame(scaler.transform(X_test), columns = X_test.columns)
        X_test.to_csv(f'{2021}_{race}.csv')

        # make predictions
        prediction_df = pd.DataFrame(model.predict(X_test), columns = ['prediction'])
        merged_df = pd.concat([prediction_df, test[['Driver','Position']].reset_index(drop=True)], axis=1)
        merged_df.rename(columns = {'Position': 'actual_pos'}, inplace = True)
        
        # shuffle data to remove original order that will influence selection
        # of race winner when there are drivers with identical win probablilities
        merged_df = merged_df.sample(frac=1).reset_index(drop=True) 
        merged_df.sort_values(by='prediction', ascending=False, inplace=True)
        merged_df['predicted_pos'] = merged_df['prediction'].map(lambda x: 0)
        merged_df.iloc[0, merged_df.columns.get_loc('predicted_pos')] = 1
        merged_df.reset_index(drop=True, inplace=True)
        if (print_output == True):
            print(merged_df)

        # --- Score --- 
        score += precision_score(merged_df['actual_pos'], merged_df['predicted_pos'], zero_division=0)
        
    return score / len(races)

def bagging_regressor_pickle(X_train, y_train):
    # now use the winning paramters to build the model
    model = BaggingRegressor(random_state=0, base_estimator=DecisionTreeRegressor(),
         n_estimators=200, max_samples=10, max_features=50, bootstrap=True, bootstrap_features=True)
    model.fit(X_train, y_train)
    pickle.dump(model, open('./model/f1-model.pkl', 'wb'))
    pickle.dump(model, open('./flask-api/f1-model.pkl', 'wb'))
    print(model.n_features_in_)

scoring_raw ={'model':[], 'params': [], 'score': [], 'train_time': [], 'test_time': []}

results_df = pd.read_csv('./csvs/feature_engineering.csv')
results_df.drop(columns=['Unnamed: 0'],inplace=True)
results_df

print(f'ML Model Building - prepare for ML model training')
# ML Model Building - prepare for ML model training
np.set_printoptions(precision=4)
model_df = results_df.copy()
model_df['Position'] = model_df['Position'].map(lambda x: 1 if x == 1 else 0)

train = model_df[(model_df['Season'] > 1950) & (model_df['Season'] < 2021)]
X_train = train.drop(['Position','Driver'], axis = 1)
y_train = train['Position']

scaler = MinMaxScaler()
X_train = pd.DataFrame(scaler.fit_transform(X_train, y_train), columns = X_train.columns)

model_df.columns
    
# ML Model Building - Model Training
print(f'Start Bagging Regressor model training...')
start = timer()
bagging_regressor_pickle(X_train, y_train)
end = timer()
print(f'bagging_regressor_pickle() took {end - start} s, DONE')