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
