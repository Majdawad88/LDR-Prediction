#git clone https://github.com/Majdawad88/LDR-Prediction.git
import serial
import time
import numpy as np
from sklearn.linear_model import LinearRegression

# 1. Setup Serial and Data Storage
try:
    ser = serial.Serial('COM16', 9600, timeout=1)
    time.sleep(2) # Wait for Arduino to reset
    print("Connected to Arduino!", flush=True)
except:
    print("Error: Could not connect to COM port.", flush=True)
    exit()

history_y = []       # Stores live LDR readings
history_x = []       # Stores time indexes
last_prediction = None
error_margin = 20    # How close the prediction needs to be to count as "Correct"

print(f"{'Time':<10} | {'Live':<10} | {'Predicted':<10} | {'Result'}", flush=True)
print("-" * 50, flush=True)

while True:
    line = ser.readline().decode('utf-8').strip()

    if line:
        try:
            current_val = float(line)
            current_time = len(history_y)

            # --- STEP 1: COMPARE LAST PREDICTION TO CURRENT REALITY ---
            result = "N/A"
            if last_prediction is not None:
                diff = abs(current_val - last_prediction)
                if diff <= error_margin:
                    result = "MATCH"
                else:
                    result = "FAIL"

            # --- STEP 2: SHOW DATA ---
            pred_display = f"{last_prediction:.2f}" if last_prediction is not None else "Wait..."
            print(f"{current_time:<10} | {current_val:<10.2f} | {pred_display:<10} | {result}", flush=True)

            # --- STEP 3: UPDATE MEMORY & RETRAIN ---
            history_y.append(current_val)
            history_x.append(current_time)

            # Only train if we have enough data (last 15 points)
            if len(history_y) > 15:
                # Use a sliding window of the last 15 points
                X_train = np.array(history_x[-15:]).reshape(-1, 1)
                y_train = np.array(history_y[-15:])

                model = LinearRegression()
                model.fit(X_train, y_train)

                # --- STEP 4: PREDICT THE NEXT VALUE ---
                # We predict for (current_time + 1) to compare it in the next loop
                next_time = [[current_time + 1]]
                last_prediction = model.predict(next_time)[0]

        except ValueError:
            continue

    time.sleep(0.1) # Small delay to match Arduino speed

