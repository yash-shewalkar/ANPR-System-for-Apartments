import streamlit as st
import subprocess
import threading
import time

# Function to run the Python script with the provided arguments
def run_script(model, source):
    st.text("Running detection...")
    subprocess.run(['python', 'v2.py', f'model={model}', f'source={source}'])
    st.text("Detection completed.")

def display_detected_text():
    st.header("Detected Text")
    text_container = st.empty()  # Create an empty container for text

    while True:
        try:
            # Read the last line from the text file
            with open("recognized_number.txt", "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()  # Get the last line and remove whitespace
                    if last_line:
                        text_container.success(f"Detected Text: {last_line}")
                    else:
                        text_container.warning("No text detected yet.")
                else:
                    text_container.warning("No text detected yet.")
        except FileNotFoundError:
            text_container.error("Error: Text file not found.")

        # Sleep for a short duration to avoid high CPU usage
        time.sleep(1)

def object_detection():
    st.title("Object Detection")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Object Detection", "Dashboard"))

    if page == "Object Detection":
        st.markdown("---")
        st.subheader("Object Detection Page")
        st.write("Put your object detection content here.")
    elif page == "Dashboard":
        st.markdown("---")
        st.subheader("Dashboard Page")
        st.write("Welcome to the Dashboard!")

def dashboard():
    st.title("Dashboard")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Object Detection", "Dashboard"))

    if page == "Object Detection":
        st.markdown("---")
        st.subheader("Object Detection Page")
        st.write("Put your object detection content here.")
    elif page == "Dashboard":
        st.markdown("---")
        st.subheader("Dashboard Page")
        st.write("Welcome to the Dashboard!")
        
        # Cards for Entries, Exits, and Guests
        st.markdown("---")
        st.subheader("Dashboard Cards")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Entries")
            st.write("100")  # Replace with actual entry count
        with col2:
            st.write("Exits")
            st.write("80")  # Replace with actual exit count
        with col3:
            st.write("Guests")
            st.write("20")  # Replace with actual guest count

def main():
    page = st.sidebar.selectbox("Go to", ("Object Detection", "Dashboard"))

    if page == "Object Detection":
        object_detection()
    elif page == "Dashboard":
        dashboard()

if __name__ == "__main__":
    main()
