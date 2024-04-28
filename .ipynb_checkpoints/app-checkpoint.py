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
    display_detected_text()

    # Footer
    st.markdown("---")
    st.sidebar.markdown(
        """
        📣 **Note:** This is a demo app for real-time object detection using Streamlit.
        """
    )

if __name__ == "__main__":
    main()
