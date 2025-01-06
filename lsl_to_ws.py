from pylsl import StreamInlet, resolve_stream, LostError
from websocket_server import WebsocketServer
import json
import threading
import time
import numpy as np
from scipy.signal import welch
import sys

# Create a WebSocket server
server = WebsocketServer(host='localhost', port=6789)

# Function to run the WebSocket server in a separate thread
def start_ws_server():
    print("Starting WebSocket server...")
    server.run_forever()

# Start the WebSocket server thread
ws_thread = threading.Thread(target=start_ws_server, daemon=True)
ws_thread.start()

# Resolve the EEG stream from MuseLSL
print("Looking for an EEG stream...")
try:
    streams = resolve_stream('type', 'EEG')
except Exception as e:
    print(f"Failed to resolve EEG stream: {e}")
    sys.exit(1)

# Connect to the LSL stream
try:
    inlet = StreamInlet(streams[0])
    print("Connected to EEG stream")
except Exception as e:
    print(f"Failed to connect to EEG stream: {e}")
    sys.exit(1)

# Sampling frequency (Muse 2 default)
fs = 256  # Hz

# Function to calculate band power using Welch's method
def calculate_band_power(signal, fs, band):
    """
    Calculate power in a specific frequency band using Welch's method.
    :param signal: Raw EEG signal (1D array)
    :param fs: Sampling frequency (e.g., 256 Hz for Muse 2)
    :param band: Frequency range as a tuple (e.g., (30, 100) for Gamma)
    :return: Power in the specified band
    """
    freqs, psd = welch(signal, fs=fs, nperseg=256)
    band_power = np.sum(psd[(freqs >= band[0]) & (freqs <= band[1])])
    return band_power

# Buffer to collect raw EEG data for processing
buffer_size = 256  # 1-second buffer
raw_buffer = []

# Cumulative sums and counts for averages
cumulative_sums = {"delta": 0, "theta": 0, "alpha": 0, "beta": 0, "gamma": 0}
cumulative_counts = 0

# Streaming loop
last_update = time.time()
update_interval = 1  # Update every 1 second

try:
    while True:
        try:
            # Pull a sample from the EEG stream
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            if sample is None:
                raise LostError("Stream lost. No new samples received.")

            raw_buffer.append(sample)

            # Ensure the buffer contains only the latest `buffer_size` samples
            if len(raw_buffer) > buffer_size:
                raw_buffer.pop(0)

            # Process data at the defined update interval
            if time.time() - last_update >= update_interval and len(raw_buffer) == buffer_size:
                # Extract raw data by channel
                raw_data = np.array(raw_buffer)  # Convert to NumPy array
                tp9 = raw_data[:, 0]  # Channel 1 (TP9)
                af7 = raw_data[:, 1]  # Channel 2 (AF7)
                af8 = raw_data[:, 2]  # Channel 3 (AF8)
                tp10 = raw_data[:, 3]  # Channel 4 (TP10)

                # Compute band powers for each channel
                delta_power = np.mean([
                    calculate_band_power(tp9, fs, band=(0.5, 4)),
                    calculate_band_power(af7, fs, band=(0.5, 4)),
                    calculate_band_power(af8, fs, band=(0.5, 4)),
                    calculate_band_power(tp10, fs, band=(0.5, 4))
                ])
                theta_power = np.mean([
                    calculate_band_power(tp9, fs, band=(4, 8)),
                    calculate_band_power(af7, fs, band=(4, 8)),
                    calculate_band_power(af8, fs, band=(4, 8)),
                    calculate_band_power(tp10, fs, band=(4, 8))
                ])
                alpha_power = np.mean([
                    calculate_band_power(tp9, fs, band=(8, 13)),
                    calculate_band_power(af7, fs, band=(8, 13)),
                    calculate_band_power(af8, fs, band=(8, 13)),
                    calculate_band_power(tp10, fs, band=(8, 13))
                ])
                beta_power = np.mean([
                    calculate_band_power(tp9, fs, band=(13, 30)),
                    calculate_band_power(af7, fs, band=(13, 30)),
                    calculate_band_power(af8, fs, band=(13, 30)),
                    calculate_band_power(tp10, fs, band=(13, 30))
                ])
                gamma_power = np.mean([
                    calculate_band_power(tp9, fs, band=(30, 100)),
                    calculate_band_power(af7, fs, band=(30, 100)),
                    calculate_band_power(af8, fs, band=(30, 100)),
                    calculate_band_power(tp10, fs, band=(30, 100))
                ])

                # Update cumulative sums and counts
                cumulative_sums["delta"] += delta_power
                cumulative_sums["theta"] += theta_power
                cumulative_sums["alpha"] += alpha_power
                cumulative_sums["beta"] += beta_power
                cumulative_sums["gamma"] += gamma_power
                cumulative_counts += 1

                # Create smoothed data dictionary
                smoothed_data = {
                    "delta": delta_power,
                    "theta": theta_power,
                    "alpha": alpha_power,
                    "beta": beta_power,
                    "gamma": gamma_power,
                }

                # Prepare JSON message
                message = json.dumps({
                    "time": time.time(),
                    "data": smoothed_data
                })

                # Send the message to all WebSocket clients
                server.send_message_to_all(message)

                # Update the last update time
                last_update = time.time()

        except LostError as e:
            print(f"Lost EEG stream connection: {e}")
            break

except Exception as e:
    print(f"Error during streaming: {e}")

finally:
    # Calculate and display averages
    if cumulative_counts > 0:
        averages = {wave: cumulative_sums[wave] / cumulative_counts for wave in cumulative_sums}
        print("Average Wave Powers:")
        for wave, avg_power in averages.items():
            print(f"{wave.capitalize()}: {avg_power:.2f}")
