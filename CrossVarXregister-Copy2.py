import streamlit as st
import subprocess
import threading
import time
import pandas as pd
import re
from firebase import firebase
import datetime

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

# Function to check if a number plate text is present in the Firebase database
def check_number_plate_in_firebase(number_plate_text, firebase_db):
    try:
        # Retrieve data from Firebase
        result = firebase_db.get("/OwnersData/", None)

        if result:
            for owner_id, data in result.items():
                # Access carNumberPlate from each owner's data
                car_number_plate = data.get("carNumberPlate", "")
                # Preprocess text for comparison
                number_plate_text_processed = preprocess_text(number_plate_text)
                car_number_plate_processed = preprocess_text(car_number_plate)
                # Check if the detected number plate matches any registered number plate
                if number_plate_text_processed == car_number_plate_processed:
                    # Fetch owner's name from the data
                    owner_firstname = data.get("nameofOwner", {}).get("firstname", "")
                    owner_lastname = data.get("nameofOwner", {}).get("lastname", "")
                    return True, f"{owner_firstname} {owner_lastname}"
            return False, ""
        else:
            st.error("No data found in Firebase database.")
            return False, ""
    except Exception as e:
        st.error(f"Error while accessing Firebase database: {str(e)}")
        return False, ""

# Function to save detected entry to Firebase
def save_detected_entry_to_firebase(number_plate_text, owner_name, is_registered, firebase_db):
    try:
        # Get current date and time
        current_datetime = datetime.datetime.now()

        # Extract date and time separately
        date_str = current_datetime.strftime("%Y-%m-%d")
        time_str = current_datetime.strftime("%H:%M:%S")

        # Create data object
        data = {
            "carNumberPlate": number_plate_text,
            "ownerName": owner_name,
            "registeredStatus": "Registered" if is_registered else "Unregistered",
            "date": date_str,
            "time": time_str
        }

        # Save data to Firebase
        firebase_db.post("/EntriesData/", data)
    except Exception as e:
        st.error(f"Error while saving entry to Firebase: {str(e)}")



# Function to display detected text
def display_detected_text(filename, firebase_db):
    st.header("Detected Text")
    text_container = st.empty()  # Create an empty container for text
    last_detection = ""  # Variable to store the last detected number plate
    popup_container = None  # Container for pop-up message
    owner_name_input_key = "owner_name_input"  # Unique key for owner's name input field
    while True:
        try:
            current_detection = read_last_saved_text(filename)
            if current_detection:
                if current_detection != last_detection:  # Check if a new detection has been made
                    last_detection = current_detection
                    text_container.success(f"Detected Text: {current_detection}")
                    # Check if the detected text is present in the Firebase database
                    is_present, owner_name = check_number_plate_in_firebase(current_detection, firebase_db)
                    if is_present:
                        text_container.success(f"The number plate '{current_detection}' has registered owner: '{owner_name}'")
                        if owner_name == "Unknown":
                            owner_name_input = st.text_input("Enter owner's name:", key=owner_name_input_key)
                        else:
                            owner_name_input = None  # Clear input field
                            st.write("Access Granted!")  # Display access granted message
                    else:
                        text_container.warning(f"The number plate '{current_detection}' is unregistered!")
                        owner_name_input = st.text_input("Enter owner's name:", key=owner_name_input_key)
                        if owner_name_input:
                            # Save the detected entry with unknown owner to Firebase
                            save_detected_entry_to_firebase(current_detection, owner_name_input, False, firebase_db)
                            text_container.success(f"The number plate '{current_detection}' is saved with owner: '{owner_name_input}' as unregistered.")
                            popup_container = st.error("Access Denied!")  # Display access denied message

            else:
                text_container.warning("No text detected yet.")
        except Exception as e:
            text_container.error(f"Error: {str(e)}")

        # Sleep for a short duration to avoid high CPU usage
        time.sleep(1)

        
# Function to display registration form
def display_registration_form(firebase_db):
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
        result = firebase_db.post("/OwnersData/", data)
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
        result = firebase_db.put("/OwnersData/", int(owner_id), data)
        st.success("Data updated successfully.")
    if st.button("Delete"):
        # Perform delete action here
        result = firebase_db.delete("/OwnersData/", int(owner_id))
        st.success("Data deleted successfully.")
    if st.button("Retrieve"):
        # Perform retrieve action here
        result = firebase_db.get("/OwnersData/", int(owner_id))
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

# Function to retrieve access grants or rejected data from Firebase
def retrieve_access_grants():
    # Firebase configuration
    firebase_config = {
        "apiKey": "AIzaSyAq5Oe1j_wMJVqn0z-yEhQMvFZRlDiU8XE",
        "authDomain": "edi4project.firebaseapp.com",
        "databaseURL": "https://edi4project-default-rtdb.firebaseio.com",
        "projectId": "edi4project",
        "storageBucket": "edi4project.appspot.com",
        "messagingSenderId": "1076558734753",
        "appId": "1:1076558734753:web:a9c250ac6621587c5ed7e0",
        "measurementId": "G-3WLFN8G757"
    }

    firebase_db = firebase.FirebaseApplication(firebase_config["databaseURL"], None)

    # Retrieve access grants or rejected data from Firebase
    # Replace "/AccessGrants/" with the path to your access grants or rejected data in your Firebase database
    result = firebase_db.get("/GrantsData/", None)

    # Convert data to DataFrame
    if result:
        df = pd.DataFrame(result.values())
        return df
    else:
        return pd.DataFrame()

# Function to display access grants
def display_access_grants():
    st.title("Access Grants / Rejected Data")
   
    # Retrieve access grants or rejected data
    df = retrieve_access_grants()

    # Get the most recent entry
    most_recent_entry = df.tail(1)  # Get the last row of the DataFrame

    # Display the most recent entry as a new entry
    if not most_recent_entry.empty:
        st.write("Most Recent Entry:")
        st.write(most_recent_entry)
    else:
        st.write("No access grants or rejected data found.")

    st.markdown("---")

    # Display data in a table
    if not df.empty:
        st.write(df)
    else:
        st.write("No access grants or rejected data found.")


def display_entries_from_firebase(firebase_db):
    st.title("Detected Entries")
    st.markdown("---")

    # Retrieve data from Firebase
    result = firebase_db.get("/EntriesData/", None)

    # Convert data to DataFrame
    if result:
        df = pd.DataFrame(result.values())
        # Rename columns for better display
        df = df.rename(columns={"carNumberPlate": "Car Number Plate",
                                "ownerName": "Owner Name",
                                "registeredStatus": "Registered Status",
                                "date": "Date",
                                "time": "Time"})
        # Display DataFrame
        st.dataframe(df)
    else:
        st.write("No detected entries found.")


def display_grants_data(firebase_db):
    st.title("Granted/Rejected Entries for Unregistered cars")
    st.markdown("---")

    #retrive data from Firebase
    result = firebase_db.get("/GrantsData", None)

    # Convert to dataframe
    if result:
        df = pd.DataFrame(result.values())
        #Rename columns 
        df = df.rename(columns={"senderName":"Visitor",
                                "recieverName" : "Owner_Name",
                                "date": "Date",
                                "time": "Time",
                                "grantStatus":"Entry_Status"
                               })
        st.dataframe(df)
    else:
        st.write("No Grants data founnd!")

def main():
    # Initialize Firebase database
    firebase_config = {
        "apiKey": "AIzaSyAq5Oe1j_wMJVqn0z-yEhQMvFZRlDiU8XE",
        "authDomain": "edi4project.firebaseapp.com",
        "databaseURL": "https://edi4project-default-rtdb.firebaseio.com",
        "projectId": "edi4project",
        "storageBucket": "edi4project.appspot.com",
        "messagingSenderId": "1076558734753",
        "appId": "1:1076558734753:web:a9c250ac6621587c5ed7e0",
        "measurementId": "G-3WLFN8G757"
    }

    firebase_db = firebase.FirebaseApplication(firebase_config["databaseURL"], None)

    # Set page title and favicon
    st.set_page_config(page_title="Smart Chowkidhar", page_icon="🚀")

    # Navigation bar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Detection", "Registration","Messages"])

    # Handle navigation
    if page == "Detection":
        # Header
        st.title("Real-Time Object Detection")
        st.markdown("---")
        display_entries_from_firebase(firebase_db)
        st.markdown("---")
        display_grants_data(firebase_db)

        # Sidebar
        st.sidebar.title("Detection Settings")
        model = st.sidebar.text_input("Model", "best.pt")
        source = st.sidebar.text_input("Source", "0")

        # Run button
        if st.sidebar.button("Run Detection"):
            # Start the detection script in a separate thread
            threading.Thread(target=run_script, args=(model, source), daemon=True).start()

        # Display detected text
        display_detected_text("recognized_number.txt", firebase_db)

        # Footer
        st.markdown("---")
        st.sidebar.markdown("")
    elif page == "Registration":
        # Display registration form
        display_registration_form(firebase_db)
    elif page == "Messages":
        # Handle messages page
        display_access_grants()

if __name__ == "__main__":
    main()
