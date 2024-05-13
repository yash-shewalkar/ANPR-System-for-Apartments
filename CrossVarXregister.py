import streamlit as st
import subprocess
import threading
import time
import pandas as pd
import re
from firebase import firebase

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
    df = pd.read_csv(csv_file)
    while True:
        try:
            last_saved_text = read_last_saved_text(filename)
            if last_saved_text:
                text_container.success(f"Detected Text: {last_saved_text}")
                # Check if the detected text is present in the CSV file
                is_present = check_number_plate_in_csv(last_saved_text, csv_file)
                if is_present:
                       # Fetch owner's name from the CSV file based on the detected text
                    owner_name = df.loc[df['number plate'].apply(preprocess_text) == preprocess_text(last_saved_text), 'Owner Name'].iloc[0]
                    text_container.success(f"The number plate '{last_saved_text}' has registered owner : '{owner_name}'")
                else:
                    text_container.warning(f"The number plate '{last_saved_text}' is unregistered!")
            else:
                text_container.warning("No text detected yet.")
        except Exception as e:
            text_container.error(f"Error: {str(e)}")

        # Sleep for a short duration to avoid high CPU usage
        time.sleep(1)

# Function to display registration form
def display_registration_form():
    st.title("Flat Owners Registration")
    st.markdown("---")

    # Input fields for registration form
    fname = st.text_input("First Name",key = 1)
    lname = st.text_input("Last Name")
    wing = st.selectbox("Wing", ["A", "B", "C"])
    flat_no = st.number_input("Flat No.")
    mobile = st.number_input("Mobile Number")
    car_number = st.text_input("Car Number Plate")
    email = st.text_input("Email")
    owner_id = st.number_input("Owner ID")

    # Firebase configuration
    firebase_config = {
          "apiKey": "AIzaSyChkpiDuK_Jbcmxj8Rh53Od0QwBd8BxFGI",
          "authDomain": "smartchowkidhar.firebaseapp.com",
          "databaseURL": "https://smartchowkidhar-default-rtdb.firebaseio.com",
          "projectId": "smartchowkidhar",
          "storageBucket": "smartchowkidhar.appspot.com",
          "messagingSenderId": "947490286483",
          "appId": "1:947490286483:web:70be023aff67182a559666",
          "measurementId": "G-C9H5FY5DP8"
    }

    firebase_db = firebase.FirebaseApplication(firebase_config["databaseURL"], None)

    # Buttons for registration actions
    if st.button("Add"):
        # Perform registration action here (store data in Firebase)
        data = {
            "ownerID": owner_id,
            "nameofOwner": {"firstname": fname, "lastname": lname},
            "wingName": wing,
            "flatNum": flat_no,
            "mobile": mobile,
            "carNumberPlate": car_number,
            "email": email
        }
        result = firebase_db.post("/SmartChowkidhar/", data)
        st.success("Data added successfully.")
    if st.button("Update"):
        # Perform update action here
        data = {
            "ownerID": owner_id,
            "nameofOwner": {"firstname": fname, "lastname": lname},
            "wingName": wing,
            "flatNum": flat_no,
            "mobile": mobile,
            "carNumberPlate": car_number,
            "email": email
        }
        result = firebase_db.put("/SmartChowkidhar/", int(owner_id), data)
        st.success("Data updated successfully.")
    if st.button("Delete"):
        # Perform delete action here
        result = firebase_db.delete("/SmartChowkidhar/", int(owner_id))
        st.success("Data deleted successfully.")
    if st.button("Retrieve"):
        # Perform retrieve action here
        result = firebase_db.get("/SmartChowkidhar/", int(owner_id))
        if result:
            fname = result["nameofOwner"]["firstname"]
            lname = result["nameofOwner"]["lastname"]
            wing = result["wingName"]
            flat_no = result["flatNum"]
            mobile = result["mobile"]
            car_number = result["carNumberPlate"]
            email = result["email"]
            
            st.success("Data retrieved successfully.")
        else:
            st.error("Owner doesn't exist.")

def display_messages():
    st.title("Messages")
    st.markdown("---")

    # Your message display logic here
    st.write("Welcome to the messages page!")
    st.write("This is where you can see your messages.")
    

def main():
    # Set page title and favicon
    st.set_page_config(page_title="Smart Chowkidhar", page_icon="🚀")

    # Navigation bar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Detection", "Registration", "Messages"])

    # Handle navigation
    if page == "Detection":
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
          
        )
    elif page == "Registration":
        # Display registration form
        display_registration_form()

    elif page == "Messages":
        # Handle messages page
        display_messages()

if __name__ == "__main__":
    main()
