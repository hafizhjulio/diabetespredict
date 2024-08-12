from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import numpy as np  # Assuming you have numpy and your model loaded
# from your_model import model, model_accuracy  # Load your model and its accuracy

app = Flask(__name__, template_folder="templates")
app.secret_key = 'kk'  # Set your Flask secret key here

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

        # Call the PHP API for registration
        response = requests.post('http://127.0.0.1:8000/api/register', json={
            'username': username,
            'email': email,
            'password': password
        })

        # Check if registration was successful
        if response.status_code == 200:  # Assuming your PHP API returns 200 on success
            return redirect(url_for('login'))  # Redirect to login page after successful registration

        # If registration fails, you can handle it here or redirect to an error page
        return render_template('error.html')

    # If GET request, render the registration form
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process the login form data
        email = request.form['email']
        password = request.form['password']

        # Call the PHP API for login
        response = requests.post('http://127.0.0.1:8000/api/login', json={
            'email': email,
            'password': password
        })

        # Print the response details to the console
        print("Response Status Code:", response.status_code)
        print("Response JSON:", response.json())
        print("Response Text:", response.text)  # Optionally print raw response text

        # Check if login was successful
        login_data = response.json()

        if response.status_code == 200:
            # Assuming successful login data contains a token
            session['token'] = login_data['data']['token']
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')

    # If GET request, render the login form
    return render_template('login.html')

# Decorator to check if user is logged in
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


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
