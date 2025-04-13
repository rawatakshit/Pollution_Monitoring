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



# --- main.py ---
import time
import numpy as np
import pandas as pd
from aqi_processing import preprocess_aqi_data, create_aqi_heatmap, predict_aqi, plot_aqi_predictions
from ph_processing import preprocess_ph_data, create_ph_heatmap, predict_ph, plot_ph_predictions


def get_simulated_data(num_samples=10):
    """
    Generates simulated AQI and pH data.
    """
    center_lat = 37.7749
    center_lon = -122.4194
    lat_range = 0.1
    lon_range = 0.1
    aqi_min = 0
    aqi_max = 200
    ph_min = 6.0
    ph_max = 8.5
    
    data = {
        'latitude': np.random.uniform(center_lat - lat_range, center_lat + lat_range, num_samples),
        'longitude': np.random.uniform(center_lon - lon_range, center_lon + lon_range, num_samples),
        'aqi': np.random.randint(aqi_min, aqi_max, num_samples).astype(float),
        'ph': np.random.uniform(ph_min, ph_max, num_samples).astype(float),
        'timestamp': [time.time() + i * 600 for i in range(num_samples)]
    }
    return pd.DataFrame(data)



def main():
    """
    Main function to run the GCS data processing and visualization.
    """
    # 1. Get the  data (simulated in this example).
    data = get_simulated_data(num_samples=20)

    # 2. Preprocess the data.
    aqi_data = preprocess_aqi_data(data.copy())  # Pass a copy to each
    ph_data = preprocess_ph_data(data.copy())    # function to avoid modifying original

    # 3. Create  heatmaps.
    create_aqi_heatmap(aqi_data, filename="aqi_heatmap.html")
    create_ph_heatmap(ph_data, filename="ph_heatmap.html")

    # 4. Predict future  levels.
    future_aqi_predictions = predict_aqi(aqi_data.copy())
    future_ph_predictions = predict_ph(ph_data.copy())

    # 5. Print and plot the predictions.
    print("\nFuture AQI Predictions:")
    print(future_aqi_predictions)
    plot_aqi_predictions(future_aqi_predictions)

    print("\nFuture pH Predictions:")
    print(future_ph_predictions)
    plot_ph_predictions(future_ph_predictions)



if __name__ == "__main__":
    main()
