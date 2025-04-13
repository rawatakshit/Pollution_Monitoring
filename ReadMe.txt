Pollution Monitoring Project

Overview
This project aims to monitor pollution levels using Unmanned Ground Vehicles (UGVs), Unmanned Aerial Vehicles (UAVs), and pH monitoring systems. The collected data is processed to generate insights and predictions regarding air quality and water pH levels.

File Descriptions

1. UGV.py
* Purpose: This script controls the Unmanned Ground Vehicle (UGV) for collecting environmental data.
* Key Functions:
   * Initializes the UGV hardware components (sensors, GPS, camera).
   * Implements path planning algorithms (A* and RRT*) for navigation.
   * Collects air quality data using the PMS7003 AQI sensor.
   * Sends collected data to the central processing unit for further analysis.

2. UAV.py
* Purpose: This script manages the operations of the Unmanned Aerial Vehicle (UAV).
* Key Functions:
   * Initializes UAV components, including the PixHawk PX4 flight controller.
   * Implements autonomous flight capabilities and navigation.
   * Collects aerial environmental data and images for pollution mapping.
   * Interfaces with the ground control station to transmit data in real-time.

3. Ph.cpp
* Purpose: This C++ program is responsible for monitoring pH levels in water bodies.
* Key Functions:
   * Initializes the pH sensor and manages data collection.
   * Controls solenoid valves for pH balancing using acid and base solutions.
   * Sends alerts or notifications if pH levels deviate from acceptable ranges.
   * Communicates with the main system to provide real-time pH data.

4. aqi_processing.py
* Purpose: This Python script processes the air quality index (AQI) data collected from the UGV and UAV.
* Key Functions:
   * Cleans and preprocesses the raw AQI data for analysis.
   * Generates heatmaps using Folium to visualize pollution levels.
   * Implements machine learning models (e.g., Random Forest) to predict future AQI levels.
   * Outputs processed data and visualizations for reporting.

5. ph_processing.py
* Purpose: This Python script processes the pH data collected from the pH monitoring system.
* Key Functions:
   * Cleans and preprocesses the pH data for analysis.
   * Analyzes trends in pH levels over time and identifies anomalies.
   * Generates reports or visualizations to communicate pH data findings.
   * Interfaces with the main system to provide insights on water quality.

6. main.py
* Purpose: This is the main entry point of the project, focusing on managing AQI and pH data.
* Key Functions:
   * Initializes data processing for AQI and pH monitoring.
   * Calls processing scripts (aqi_processing.py and ph_processing.py) to analyze collected data.
   * Generates reports and visualizations for end-users and stakeholders.
   * Manages the integration of AQI and pH data for comprehensive environmental monitoring.
