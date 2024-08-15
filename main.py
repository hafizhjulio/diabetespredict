from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
import requests
import numpy as np  # Assuming you have numpy and your model loaded
# from your_model import model, model_accuracy  # Load your model and its accuracy

import pickle
import numpy as np

app = Flask(__name__, template_folder="templates")
model = pickle.load(open(r"final2.pkl","rb"))
app.secret_key = 'kk'  # Set your Flask secret key here
model_accuracy = 78  # Contoh akurasi model dalam persen
# Redirect '/' to '/home'
@app.route('/')
def index():
    return render_template('home.html')

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Process the registration form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Custom headers, especially the User-Agent to mimic Postman or a browser
        headers = {
            'User-Agent': 'PostmanRuntime/7.28.4'  # Example from Postman
        }

        max_retries = 3  # Number of retry attempts
        retry_count = 0
        wait_time = 2  # Initial wait time in seconds

        while retry_count < max_retries:
            # Call the hosted API for registration
            response = requests.post('https://barbeqshop.online/api/register', json={
                'username': username,
                'email': email,
                'password': password
            }, headers=headers)

            if response.status_code == 429:
                # If we hit the rate limit, wait and retry
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
                retry_count += 1
            else:
                break

        if response.status_code == 200:
            # Redirect to login page after successful registration
            return redirect(url_for('login'))
        elif response.status_code == 429:
            # Too many requests, inform the user to try again later
            return render_template('error.html', error="Too many requests. Please try again later.")
        else:
            # Handle other errors
            return render_template('error.html', error=f"Error: {response.status_code} - {response.text}")

    # If GET request, render the registration form
    return render_template('register.html')
# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process the login form data
        email = request.form['email']
        password = request.form['password']

        # Custom headers, especially the User-Agent to mimic Postman or a browser
        headers = {
            'User-Agent': 'PostmanRuntime/7.28.4'  # Example from Postman
        }

        max_retries = 3  # Number of retry attempts
        retry_count = 0
        wait_time = 2  # Initial wait time in seconds

        while retry_count < max_retries:
            # Call the local API for login
            response = requests.post('https://barbeqshop.online/api/login', json={
                'email': email,
                'password': password
            }, headers=headers)

            if response.status_code == 429:
                # If we hit the rate limit, wait and retry
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
                retry_count += 1
            else:
                break

        # Check if login was successful
        if response.status_code == 200:
            try:
                login_data = response.json()
                # Assuming successful login data contains a token
                session['token'] = login_data['data']['token']
                print(session['token'])
                return redirect(url_for('home'))  # Redirect to home page after successful login
            except ValueError:
                return render_template('login.html', error='Invalid response format from the server.')

        elif response.status_code == 429:
            # Too many requests, inform the user to try again later
            return render_template('login.html', error="Too many requests. Please try again later.")
        else:
            return render_template('login.html', error=f"Invalid credentials. Please try again.")

    # If GET request, render the login form
    return render_template('login.html')

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/history')
@login_required
def history():
    token = session.get('token')  # Retrieve the token from the session
    return render_template('history.html', token=token)


@app.route('/logout')
def logout():
    # Remove the token from the session
    session.pop('token', None)
    return redirect(url_for('login'))
# Route for home page
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/AboutMe', methods=['GET', 'POST'])
def aboutme():
    return render_template('AboutMe.html')

@app.route('/ContactUs', methods=['GET', 'POST'])
def contactus():
    return render_template('ContactUs.html')

@app.route('/HealthTools', methods=['GET', 'POST'])
def healthtools():
    return render_template('HealthTools.html')

@app.route('/ExpertAdv', methods=['GET', 'POST'])
def expertadv():
    return render_template('ExpertAdv.html')

@app.route('/Diet&Exer', methods=['GET', 'POST'])
def dietandexer():
    return render_template('Diet&Exer.html')

@app.route('/Test', methods=['GET', 'POST'])
@login_required
def test():
    # Retrieve the token from the session
    token = session.get('token')
    
    # Pass the token to the template
    return render_template('Form.html', token=token)

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    return render_template('summary.html')

# Route for processing data (as per your existing code)
@app.route('/process_data', methods=['POST'])
def process_data():
    # Get data from the request
    data = request.get_json().get('data')
    print(data)
    
    # Ensure the data has exactly 8 elements
    if len(data) != 8:
        return jsonify({'error': 'Invalid input data length'}), 400
    
    try:
        dt1 = int(data[0])
        dt2 = int(data[1])
        dt3 = int(data[2])
        dt4 = int(data[3])
        dt5 = int(data[4])
        dt6 = float(data[5])
        dt7 = float(data[6])
        dt8 = int(data[7])
    except ValueError as e:
        return jsonify({'error': 'Invalid input data format'}), 400
    
    dat = (dt1, dt2, dt3, dt4, dt5, dt6, dt7, dt8)
    print(dat)
    
    final = np.array([dat])
    print(final)
    
    # Make prediction
    prediction = model.predict(final)
    print(prediction)
    
    res1 = prediction[0]
    if res1 == 0:
        msg = "Jangan khawatir! Kamu tampak benar-benar sehat dan baik-baik saja"
    elif res1 == 1:
        msg = "Anda rentan terhadap gaya hidup diabetes. Tolong perhatikan kebiasaan Anda"
    else:
        msg = "Hasil prediksi tidak dikenali"
    
    # Return the prediction and model accuracy as JSON response
    return jsonify({'result': msg, 'accuracy': model_accuracy})

if __name__ == "__main__":
    app.run(debug=True)
