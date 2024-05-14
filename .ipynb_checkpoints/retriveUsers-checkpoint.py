import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from firebase import firebase

# Function to retrieve all owner names and emails from Firebase
def retrieve_owner_data():
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

    result = firebase_db.get("/OwnersData/", None)
    if result:
        owner_data = {data['nameofOwner']['firstname'] + ' ' + data['nameofOwner']['lastname']: data['email'] for data in result.values()}
        return owner_data
    else:
        return {}

# Function to send email
def send_email(sender_name, receiver_name, receiver_email, purpose):
    # Gmail configuration
    gmail_user = 'edi4project.22@gmail.com'  # Enter your Gmail email here
    gmail_password = 'ywtb oqld mlgi vmhu'     # Enter your Gmail password here

    # Email content
    subject = f"Meeting Request from {sender_name}"
    body = f"Dear {receiver_name},\n\n{sender_name} wants to meet you for the following purpose:\n\n{purpose}\n\n" \
           f"Click the button below to grant access or click the Reject button to deny access:\n\n"
    
    # Generate URL dynamically based on sender and receiver names
    grant_access_url = f"http://127.0.0.1:5500/grants.html?sender={sender_name}&receiver={receiver_name}"
    reject_url = f"http://127.0.0.1:5501/rejectGrants.html?sender={sender_name}&receiver={receiver_name}"  # URL for Reject button
    
    html_body = f"<p>Dear {receiver_name},</p>" \
                f"<p>{sender_name} wants to meet you for the following purpose:</p>" \
                f"<p>{purpose}</p>" \
               f"<p><a href='{grant_access_url}'><button class='grant-button'>Grant Access</button></a></p>" \
               f"<p><a href='{reject_url}'><button class='reject-button'>Reject</button></a></p>"

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['From'] = gmail_user
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach body
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # Send email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, receiver_email, msg.as_string())
        server.close()
        st.success("Email sent successfully.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Main function to run the Streamlit app
def main():
    st.title("Send Request")
    st.markdown("---")

    # Retrieve owner names and emails from Firebase
    owner_data = retrieve_owner_data()
    owner_names = list(owner_data.keys())

    if owner_names:
        # Form fields
        sender_name = st.text_input("Sender's Name")
        receiver_name = st.selectbox("Receiver's Name", owner_names)
        receiver_email = owner_data.get(receiver_name, "")
        purpose = st.text_area("Purpose")

        # Button to send request
        if st.button("Send Request"):
            # Handle request sending here
            if sender_name and receiver_name and receiver_email and purpose:
                send_email(sender_name, receiver_name, receiver_email, purpose)
            else:
                st.error("Please fill in all fields.")
    else:
        st.write("No owner data found.")

    # Custom CSS for button styling
    st.markdown("""
        <style>
            .grant-button, .reject-button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                cursor: pointer; /* Add cursor pointer */
                transition: background-color 0.3s ease; /* Add transition effect */
            }
            .grant-button:hover, .reject-button:hover {
                background-color: #45a049; /* Change button color on hover */
            }
            .grant-button:active, .reject-button:active {
                background-color: #367d39; /* Change button color on click */
            }
            .reject-button {
                background-color: #f44336; /* Change reject button color */
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
