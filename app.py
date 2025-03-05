from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from twilio.rest import Client
import random

app = Flask(__name__)

# Twilio credentials (replace with your own)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load crime dataset (example dataset)
crime_data = pd.read_csv('crime_data.csv')  # Replace with your dataset

# Train a simple ML model for crime prediction
def train_crime_prediction_model():
    X = crime_data[['latitude', 'longitude']]
    y = crime_data['crime_type']  # Replace with actual crime labels
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model

crime_model = train_crime_prediction_model()

# In-memory storage for favorite contacts (replace with a database in production)
favorite_contacts = []

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to add favorite contacts
@app.route('/add_contact', methods=['POST'])
def add_contact():
    data = request.json
    favorite_contacts.append(data)
    return jsonify({'status': 'Contact added', 'contacts': favorite_contacts})

# Route to send SOS alert (SMS + Voice Call)
@app.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    latitude = data['latitude']
    longitude = data['longitude']
    message = f"EMERGENCY! I need help! My location: https://maps.google.com/?q={latitude},{longitude}"

    # Send SMS to all favorite contacts
    for contact in favorite_contacts:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=contact['phone']
        )

        # Make a voice call to the contact
        call = client.calls.create(
            url='http://demo.twilio.com/docs/voice.xml',  # TwiML for voice call
            to=contact['phone'],
            from_=TWILIO_PHONE_NUMBER
        )

    return jsonify({'status': 'SOS sent', 'location': {'latitude': latitude, 'longitude': longitude}})

# Route to simulate a fake call
@app.route('/fake_call', methods=['POST'])
def fake_call():
    fake_number = f"+91-{random.randint(9000000000, 9999999999)}"
    return jsonify({'fake_number': fake_number})

# Route to predict crime in an area
@app.route('/predict_crime', methods=['POST'])
def predict_crime():
    data = request.json
    latitude = data['latitude']
    longitude = data['longitude']
    prediction = crime_model.predict([[latitude, longitude]])[0]
    return jsonify({'crime_prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)