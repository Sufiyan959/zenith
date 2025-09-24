from flask import Flask, render_template, request,jsonify
import os
import joblib
import pandas as pd
import requests
from dotenv import load_dotenv

# ----------------- Flask Initialization -----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
load_dotenv()
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# ----------------- Paths -----------------
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
yield_model_path = os.path.join(BASE_DIR, "models", "ML_models", "yield_predictor.pkl")
crop_model_path = os.path.join(BASE_DIR, "models", "ML_models", "Crop_recommendation.pkl")
fert_model_path = os.path.join(BASE_DIR, "models", "ML_models", "fertilizer.pkl")

# ----------------- Load Models -----------------
try:
    yield_model = joblib.load(yield_model_path)
except Exception as e:
    print(f"Error loading yield model: {e}")
    yield_model = None

try:
    crop_model = joblib.load(crop_model_path)
except Exception as e:
    print(f"Error loading crop recommendation model: {e}")
    crop_model = None

try:
    fert_model = joblib.load(fert_model_path)
except Exception as e:
    print(f"Error loading fertilizer model: {e}")
    fert_model = None

# ----------------- Routes -----------------

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# ----------------- Yield Prediction -----------------
@app.route("/yield-predict", methods=["GET", "POST"])
def yield_predict():
    if request.method == "POST":
        try:
            # Get form data
            State = request.form['State']
            District = request.form['District']
            Crop = request.form['Crop']
            Crop_Year = int(request.form['Crop_Year'])
            Season = request.form['Season']
            Area = float(request.form['Area'])
            Production = float(request.form['Production'])

            # Arrange into dataframe row
            input_data = pd.DataFrame([{
                "State": State,
                "District": District,
                "Crop": Crop,
                "Crop_Year": Crop_Year,
                "Season": Season,
                "Area": Area,
                "Production": Production
            }])

            # Make prediction
            if yield_model:
                prediction = yield_model.predict(input_data)[0]
                result_text = f"Predicted Yield: {prediction:.2f} tonnes/hectare"
            else:
                result_text = "Yield prediction model not loaded."

        except Exception as e:
            result_text = f"Error in yield prediction: {str(e)}"

        return render_template("yield-predict.html", prediction_text=result_text)
    else:
        return render_template("yield-predict.html")


# ----------------- Crop Recommendation -----------------
@app.route("/crop-recommend", methods=["GET", "POST"])
def crop_recommend():
    if request.method == "POST":
        try:
            N = float(request.form['N'])
            P = float(request.form['P'])
            K = float(request.form['K'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])

            input_data = pd.DataFrame([{
                "Nitrogen": N,
                "Phosphorous": P,
                "Potassium": K,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall
            }])

            if crop_model:
                crop_pred = crop_model.predict(input_data)[0]
                result_text = f"Recommended Crop: {crops[crop_pred]}"
            else:
                result_text = "Crop recommendation model not loaded."

        except Exception as e:
            result_text = f"Error in crop recommendation: {str(e)}"

        return render_template("crop-recommend.html", prediction_text=result_text)
    else:
        return render_template("crop-recommend.html")

@app.route('/community-forum')
def community_forum():
    # Later you can integrate a real forum or database
    posts = [
        {"user": "Farmer A", "topic": "Best fertilizer for wheat?", "replies": 5},
        {"user": "Farmer B", "topic": "How to save crops from pests?", "replies": 3},
        {"user": "Farmer C", "topic": "Rainwater harvesting methods", "replies": 7},
    ]
    return render_template('community_forum.html', posts=posts)
@app.route('/weather')
def weather_page():
    # Render the current weather page
    return render_template('weather.html')


@app.route('/weather-data', methods=['POST'])
def weather_data():
    try:
        data = request.get_json()
        city = data.get('city')
        if not city:
            return jsonify({'error': 'City name is required'}), 400

        if not WEATHER_API_KEY:
            return jsonify({'error': 'Weather API key not configured on server'}), 500

        # Fetch current weather from OpenWeatherMap
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
        response = requests.get(url, timeout=10)
        weather_data = response.json()

        if response.status_code != 200:
            return jsonify({'error': weather_data.get('message', 'Failed to fetch weather data')}), response.status_code

        # Extract only the needed fields for your HTML
        result = {
            "name": weather_data.get("name"),
            "main": {
                "temp": weather_data.get("main", {}).get("temp"),
                "humidity": weather_data.get("main", {}).get("humidity"),
                "pressure": weather_data.get("main", {}).get("pressure")
            },
            "wind": {
                "speed": weather_data.get("wind", {}).get("speed"),
                "deg": weather_data.get("wind", {}).get("deg")
            },
            "weather": weather_data.get("weather", [{}])[0],
            "sys": {
                "sunrise": weather_data.get("sys", {}).get("sunrise"),
                "sunset": weather_data.get("sys", {}).get("sunset")
            },
            "rain": weather_data.get("rain")
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # here you can implement sending reset link logic
        return "Password reset instructions sent to " + email
    
    return render_template('forgot_password.html')

# ----------------- Fertilizer Recommendation -----------------
# ----------------- Fertilizer Recommendation -----------------
@app.route("/fertilizer-recommend", methods=["GET", "POST"])
def fertilizer_recommend():
    result_text = None  # default value

    if request.method == "POST":
        try:
            # Numeric features
            Temperature = float(request.form['temperature'])
            Humidity = float(request.form['humidity'])
            Moisture = float(request.form['moisture'])
            Nitrogen = float(request.form['N'])
            Potassium = float(request.form['K'])
            Phosphorous = float(request.form['P'])

            # Categorical features
            Soil_Type = request.form['soil']  # from dropdown
            Crop_Type = request.form['crop']  # from dropdown

            # Encode categorical features
            soil_mapping = {soil: idx for idx, soil in enumerate(soil_types)}
            crop_mapping = {crop: idx for idx, crop in enumerate(Crop_types)}

            Soil_Type_encoded = soil_mapping.get(Soil_Type, 0)
            Crop_Type_encoded = crop_mapping.get(Crop_Type, 0)

            # Combine features into dataframe
            input_data = pd.DataFrame([{
                "Temperature": Temperature,
                "Humidity": Humidity,
                "Moisture": Moisture,
                "Nitrogen": Nitrogen,
                "Potassium": Potassium,
                "Phosphorous": Phosphorous,
                "Soil_Type": Soil_Type_encoded,
                "Crop_Type": Crop_Type_encoded
            }])

            if fert_model:
                fert_pred_idx = fert_model.predict(input_data)[0]
                result_text = f"Recommended Fertilizer: {fertilizer_classes[fert_pred_idx]}"
            else:
                result_text = "Fertilizer recommendation model not loaded."

        except Exception as e:
            result_text = f"Error in fertilizer recommendation: {str(e)}"

    # Render template with dropdown lists and prediction
    return render_template(
        "fertilizer-recommend.html",
        soil_types=soil_types,
        Crop_types=Crop_types,
        prediction_text=result_text
    )
@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/crop-disease')
def crop_disease():
    return render_template('crop-disease.html')

@app.route('/disease-prediction-result')
def disease_prediction_result():
    return render_template('disease-prediction-result.html')



crops = ['apple', 'banana', 'blackgram', 'chickpea', 'coconut', 'coffee', 'cotton', 'grapes', 
         'jute', 'kidneybeans', 'lentil', 'maize', 'mango', 'mothbeans', 'mungbean', 'muskmelon', 
         'orange', 'papaya', 'pigeonpeas', 'pomegranate', 'rice', 'watermelon']

soil_types = ['Black', 'Clayey', 'Loamy', 'Red', 'Sandy']
Crop_types = ['Barley', 'Cotton', 'Ground Nuts', 'Maize', 'Millets', 'Oil seeds', 'Paddy', 
              'Pulses', 'Sugarcane', 'Tobacco', 'Wheat']
fertilizer_classes = ['10-26-26', '14-35-14', '17-17-17', '20-20', '28-28', 'DAP', 'Urea']

# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
