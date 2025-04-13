# --- aqi_processing.py ---
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

def preprocess_aqi_data(df):
    """
    Preprocesses the AQI data.
    - Converts timestamps to datetime objects.
    - Feature engineering (e.g., creating time-based features).
    - Removing outliers
    Args:
        df: A pandas DataFrame with AQI and GPS data.

    Returns:
        A cleaned pandas DataFrame.
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df[(df['aqi'] >= 0) & (df['aqi'] <= 500)]
    df['hour_of_day'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df = df.fillna(df.mean())
    return df

def create_aqi_heatmap(df, filename="aqi_heatmap.html"):
    """
    Creates an AQI heatmap using Folium.

    Args:
        df: A pandas DataFrame with AQI and GPS data.
        filename: The name of the HTML file to save the heatmap to.
    """
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)
    heat_data = [[row['latitude'], row['longitude'], row['aqi']] for _, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)
    m.save(filename)
    print(f"AQI Heatmap saved to {filename}")



def predict_aqi(df):
    """
    Predicts future AQI levels using a machine learning model.

    Args:
        df: A pandas DataFrame with AQI and GPS data, including time-based features.

    Returns:
        A pandas DataFrame with the predicted AQI values and their corresponding times
    """
    df = df.copy()
    features = ['latitude', 'longitude', 'hour_of_day', 'day_of_week']
    target = 'aqi'
    X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"AQI Mean Squared Error: {mse}")
    last_time = df['datetime'].max()
    future_times = pd.to_datetime([last_time + pd.Timedelta(minutes=i*15) for i in range(1, 5)])
    future_df = pd.DataFrame({
        'datetime': future_times,
        'latitude': [df['latitude'].mean()] * len(future_times),
        'longitude': [df['longitude'].mean()] * len(future_times),
    })
    future_df['hour_of_day'] = future_df['datetime'].dt.hour
    future_df['day_of_week'] = future_df['datetime'].dt.dayofweek
    future_predictions = model.predict(future_df[features])
    future_df['predicted_aqi'] = future_predictions
    return future_df[['datetime', 'predicted_aqi']]

def plot_aqi_predictions(predictions):
    """
    Plots the predicted AQI values over time.

    Args:
        predictions: A pandas DataFrame with predicted AQI values and times
    """
    plt.figure(figsize=(10, 6))
    plt.plot(predictions['datetime'], predictions['predicted_aqi'], marker='o', linestyle='-', color='r')
    plt.title('Predicted AQI')
    plt.xlabel('Time')
    plt.ylabel('AQI')
    plt.grid(True)
    plt.show()