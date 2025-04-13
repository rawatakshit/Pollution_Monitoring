# Code for Raspberry Pi 4B on UGV for environmental data gathering

# Import necessary libraries
import time
from picamera import PiCamera
from hcsr04sensor import HCSR04
import serial
import pynmea2  # For GPS parsing

# --- Configuration ---
CAMERA_CAPTURE_INTERVAL = 60  # seconds
DISTANCE_THRESHOLD = 50      # cm for object avoidance
AQI_READ_INTERVAL = 5        # seconds
GPS_READ_INTERVAL = 1        # second
SERIAL_PORT = '/dev/ttyS0'   # Default serial port for UART communication
BAUDRATE = 9600

# --- Initialize Components ---
try:
    camera = PiCamera()
    print("Camera initialized successfully.")
except Exception as e:
    print(f"Error initializing camera: {e}")
    camera = None

sensor = HCSR04(trigger_pin=17, echo_pin=18, temperature=20)  # Adjust pins as needed
print("HCSR04 sensor initialized (adjust pins if needed).")

try:
    aqi_serial = serial.Serial(SERIAL_PORT, BAUDRATE)
    print("PMS7003 sensor serial initialized.")
except serial.SerialException as e:
    print(f"Error initializing PMS7003 serial port {SERIAL_PORT}: {e}")
    aqi_serial = None

try:
    gps_serial = serial.Serial(SERIAL_PORT, BAUDRATE) # Assuming GPS also uses UART
    print("GPS serial initialized.")
except serial.SerialException as e:
    print(f"Error initializing GPS serial port {SERIAL_PORT}: {e}")
    gps_serial = None

# --- Global Variables ---
last_camera_capture = time.time()
last_aqi_read = time.time()
last_gps_read = time.time()
current_location = None
pollution_data = None

# --- Functions ---

def capture_image():
    """Captures an image using the Pi Camera."""
    if camera:
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"/home/pi/images/capture_{timestamp}.jpg"  # Adjust path as needed
            camera.capture(filename)
            print(f"Image captured: {filename}")
            return filename
        except Exception as e:
            print(f"Error capturing image: {e}")
    return None

def check_distance():
    """Checks the distance using the HCSR04 sensor."""
    if sensor:
        distance = sensor.distance()
        print(f"Distance: {distance:.2f} cm")
        return distance
    return None

def read_aqi():
    """Reads data from the PMS7003 AQI sensor."""
    global pollution_data
    if aqi_serial:
        try:
            if aqi_serial.in_waiting >= 32:  # PMS7003 sends 32 bytes of data
                data = aqi_serial.read(32)
                if len(data) == 32 and data[0:2] == b'\x42\x4d':
                    pm1_0 = int.from_bytes(data[2:4], 'big')
                    pm2_5 = int.from_bytes(data[4:6], 'big')
                    pm10 = int.from_bytes(data[6:8], 'big')
                    pollution_data = {"pm1_0": pm1_0, "pm2_5": pm2_5, "pm10": pm10}
                    print(f"AQI Data: PM1.0={pm1_0}, PM2.5={pm2_5}, PM10={pm10}")
                    return pollution_data
                else:
                    print("Invalid AQI data format.")
            else:
                print("Not enough data from AQI sensor.")
        except serial.SerialException as e:
            print(f"Error reading from AQI sensor: {e}")
    return None

def get_gps_location():
    """Reads and parses GPS data."""
    global current_location
    if gps_serial:
        try:
            sentence = gps_serial.readline().decode('utf-8', errors='ignore').strip()
            if sentence.startswith('$GPGGA'):
                msg = pynmea2.parse(sentence)
                if msg.latitude and msg.longitude:
                    current_location = (msg.latitude, msg.longitude)
                    print(f"GPS Location: Latitude={msg.latitude}, Longitude={msg.longitude}")
                    return current_location
            elif sentence.startswith('$GPRMC'):
                msg = pynmea2.parse(sentence)
                if msg.latitude and msg.longitude and msg.status == 'A': # 'A' indicates a valid fix
                    current_location = (msg.latitude, msg.longitude)
                    print(f"GPS Location (RMC): Latitude={msg.latitude}, Longitude={msg.longitude}")
                    return current_location
        except serial.SerialException as e:
            print(f"Error reading from GPS: {e}")
        except pynmea2.ParseError as e:
            print(f"Error parsing GPS data: {e}")
    return None

def send_data_to_gcs(image_path=None, distance=None, pollution=None, location=None):
    """
    Simulates sending data to the Ground Control Station (GCS).
    In a real application, this would involve network communication (e.g., Wi-Fi, LoRa).
    """
    print("\n--- Sending Data to GCS ---")
    if image_path:
        print(f"Image Path: {image_path}")
    if distance is not None:
        print(f"Distance: {distance:.2f} cm")
    if pollution:
        print(f"Pollution Data: {pollution}")
    if location:
        print(f"Location: Latitude={location[0]}, Longitude={location[1]}")
    print("---------------------------\n")

def avoid_obstacle():
    """Basic obstacle avoidance logic."""
    distance = check_distance()
    if distance is not None and distance < DISTANCE_THRESHOLD:
        print("Obstacle detected! Implementing avoidance maneuver (replace with actual motor control).")
        # In a real robot, you would add code here to stop or move the UGV.
        return True
    return False

def main_loop():
    """Main loop for data acquisition and processing."""
    global last_camera_capture, last_aqi_read, last_gps_read

    while True:
        if avoid_obstacle():
            time.sleep(1)  # Give time for avoidance maneuver
            continue

        current_time = time.time()

        # Capture image periodically
        if camera and current_time - last_camera_capture >= CAMERA_CAPTURE_INTERVAL:
            image_path = capture_image()
            send_data_to_gcs(image_path=image_path)
            last_camera_capture = current_time

        # Read AQI data periodically
        if aqi_serial and current_time - last_aqi_read >= AQI_READ_INTERVAL:
            pollution_data = read_aqi()
            if pollution_data and current_location:
                send_data_to_gcs(pollution=pollution_data, location=current_location)
            elif pollution_data:
                print("No GPS location available yet, cannot send combined pollution and location data.")
            last_aqi_read = current_time

        # Read GPS data periodically
        if gps_serial and current_time - last_gps_read >= GPS_READ_INTERVAL:
            current_location = get_gps_location()
            last_gps_read = current_time

        time.sleep(0.1)  # Small delay to avoid busy-waiting

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if camera:
            camera.close()
        if aqi_serial and aqi_serial.is_open:
            aqi_serial.close()
        if gps_serial and gps_serial.is_open:
            gps_serial.close()
        if sensor:
            sensor.cleanup()