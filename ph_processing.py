#ph
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap


def preprocess_ph_data(df):
    """
    Preprocesses the  pH data.
    - Converts timestamps to datetime objects.
    - Feature engineering.
    - Removing outliers
    Args:
        df: A pandas DataFrame with  pH and GPS data.

    Returns:
        A cleaned pandas DataFrame.
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df[(df['ph'] >= 0) & (df['ph'] <= 14)]
    df['hour_of_day'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df = df.fillna(df.mean())
    return df



def create_ph_heatmap(df, filename="ph_heatmap.html"):
    """
    Creates a  pH heatmap using Folium.

    Args:
        df: A pandas DataFrame with  pH and GPS data.
        filename: The name of the HTML file to save the heatmap to.
    """
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)
    heat_data = [[row['latitude'], row['longitude'], row['ph']] for _, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)
    m.save(filename)
    print(f"pH Heatmap saved to {filename}")



def predict_ph(df):
    """
    Predicts future  pH levels using a machine learning model.

    Args:
        df: A pandas DataFrame with  pH and GPS data, including time-based features.

    Returns:
        A pandas DataFrame with the predicted  pH values and their corresponding times
    """
    df = df.copy()
    features = ['latitude', 'longitude', 'hour_of_day', 'day_of_week']
    target = 'ph'
    X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"pH Mean Squared Error: {mse}")
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
    future_df['predicted_ph'] = future_predictions
    return future_df[['datetime', 'predicted_ph']]

def plot_ph_predictions(predictions):
    """
    Plots the predicted  pH values over time.

    Args:
        predictions: A pandas DataFrame with predicted  pH values and times.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(predictions['datetime'], predictions['predicted_ph'], marker='o', linestyle='-', color='r')
    plt.title('Predicted pH')
    plt.xlabel('Time')
    plt.ylabel('pH')
    plt.grid(True)
    plt.show()
