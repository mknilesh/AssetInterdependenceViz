import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from datetime import datetime, timedelta


def read_data(assetName):

    df = pd.read_csv("./data/final_dataset.csv")
    dataset = df[["Date", assetName]]
    dataset["Date"] = pd.to_datetime(dataset["Date"])
    
    dataset['day'] = dataset["Date"].dt.dayofyear
    dataset['month'] = dataset["Date"].dt.month
    dataset['year'] = dataset["Date"].dt.year
    dataset['dayofweek'] = dataset["Date"].dt.dayofweek
    dataset = dataset.set_index('Date')
    features = ['month', 'day', 'dayofweek', 'year']
    target = [assetName]

    new_test = anomaly_prediction(dataset[features], dataset[target], dataset.iloc[-1].name, 365, features)
    new_test = new_test.set_index('Date')
    
    return new_test

def train_and_predict(X_train, y_train, X_test, output_df, lr = 0.01, n_estimators = 1000):
    reg = GradientBoostingRegressor(learning_rate = lr, n_estimators = n_estimators, min_samples_split = 10, min_samples_leaf = 10)
    reg.fit(X_train, y_train.values.ravel())
    output_df['prediction'] = reg.predict(X_test)
    return output_df, reg

def anomaly_prediction(X_train, y_train, current_day, num_days, features):
    date_range = pd.date_range(current_day - timedelta(days = 10), current_day + timedelta(days=num_days))
    new_test = date_range.to_frame(index = False, name = "Date")
    
    new_test['dayofweek'] = new_test.Date.dt.dayofweek
    new_test['day'] = new_test.Date.dt.dayofyear
    new_test['month'] = new_test.Date.dt.month
    new_test['year'] = new_test.Date.dt.year
    
    X_test = new_test[features]
    new_test, _ = train_and_predict(X_train, y_train, X_test, new_test)
    return new_test


if __name__ == "__main__":
    assetName = "PRI:US"
    read_data(assetName)