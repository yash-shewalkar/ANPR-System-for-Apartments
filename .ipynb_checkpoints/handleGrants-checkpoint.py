from flask import Flask, redirect, request
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Endpoint to handle URL clicks
@app.route('/grant-access')
def grant_access():
    sender_name = request.args.get('sender_name')
    receiver_name = request.args.get('receiver_name')

    # Update Firebase database
    doc_ref = db.collection('access_requests').document()
    doc_ref.set({
        'sender_name': sender_name,
        'receiver_name': receiver_name,
        'access_granted': True
    })

    # Redirect to confirmation page
    return redirect('/confirmation')

# Streamlit app code
if __name__ == "__main__":
    app.run(debug=True)
