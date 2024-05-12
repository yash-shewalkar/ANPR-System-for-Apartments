import streamlit as st
import subprocess
import threading
import time
import pandas as pd
import re

# Function to run the Python script with the provided arguments
def run_script(model, source):
    st.text("Running detection...")
    subprocess.run(['python', 'v2.py', f'model={model}', f'source={source}'])
    st.text("Detection completed.")

# Function to read the last saved text from a file
def read_last_saved_text(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()  # Get the last line and remove whitespace
                return last_line
            else:
                return "File is empty"
    except FileNotFoundError:
        return "File not found"

# Function to preprocess text (remove non-alphanumeric characters, convert to uppercase, and remove white spaces)
def preprocess_text(text):
    return re.sub(r'\W+', '', text).upper().replace(" ", "")

# Function to check if a number plate text is present in a CSV file
def check_number_plate_in_csv(number_plate_text, csv_file):
    try:
        df = pd.read_csv(csv_file)
        number_plate_text_processed = preprocess_text(number_plate_text)
        df['number plate'] = df['number plate'].apply(preprocess_text)
        return number_plate_text_processed in df['number plate'].values
    except FileNotFoundError:
        st.error("CSV file not found.")
        return False

# Function to display detected text
def display_detected_text(filename, csv_file):
    st.header("Detected Text")
    text_container = st.empty()  # Create an empty container for text

    while True:
        try:
            last_saved_text = read_last_saved_text(filename)
            if last_saved_text:
                text_container.success(f"Detected Text: {last_saved_text}")
                # Check if the detected text is present in the CSV file
                is_present = check_number_plate_in_csv(last_saved_text, csv_file)
                if is_present:
                    text_container.success(f"The number plate '{last_saved_text}' is present in the CSV file.")
                else:
                    text_container.warning(f"The number plate '{last_saved_text}' is not present in the CSV file.")
            else:
                text_container.warning("No text detected yet.")
        except Exception as e:
            text_container.error(f"Error: {str(e)}")

        # Sleep for a short duration to avoid high CPU usage
        time.sleep(1)

def main():
    # Set page title and favicon
    st.set_page_config(page_title="Object Detection", page_icon="🚀")

    # Header
    st.title("Real-Time Object Detection")
    st.markdown("---")

    # Sidebar
    st.sidebar.title("Detection Settings")
    model = st.sidebar.text_input("Model", "best.pt")
    source = st.sidebar.text_input("Source", "0")

    # Run button
    if st.sidebar.button("Run Detection"):
        # Start the detection script in a separate thread
        threading.Thread(target=run_script, args=(model, source), daemon=True).start()

    # Display detected text
    display_detected_text("recognized_number.txt", "owners.csv")

    # Footer
    st.markdown("---")
    st.sidebar.markdown(
        """
        📣 **Note:** This is a demo app for real-time object detection using Streamlit.
        """
    )

if __name__ == "__main__":
    main()
