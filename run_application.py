import subprocess
import time

# Start Kafka consumer
consumer_process = subprocess.Popen(["python", "consumer.py"])

# Start Streamlit app
streamlit_process = subprocess.Popen(["streamlit", "run", "frontend/Home.py"])

# Wait for a little while (e.g., give Kafka consumer time to start)
try:
    while True:
        time.sleep(1)  # Keeps the script running
except KeyboardInterrupt:
    print("Stopping processes...")

# Terminate both processes when the script is interrupted
consumer_process.terminate()
streamlit_process.terminate()
