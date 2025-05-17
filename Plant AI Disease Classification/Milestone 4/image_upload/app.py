from flask import Flask, request, render_template, jsonify, url_for
import os
import tensorflow as tf
import numpy as np
import cv2
from werkzeug.utils import secure_filename
import logging

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/upload/'
MODEL_PATH = 'C:/Users/DELL/Desktop/infosysSpringBoard2/image_upload/models/sashanksModel20epochhhha.h5'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the model
model = tf.keras.models.load_model(MODEL_PATH)

# Class names (Ensure it matches the model's output order)
CLASS_NAMES = [
    "Bacterial Blight (CBB)", "Brown Streak Disease (CBSD)", "Green Mottle (CGM)", "Healthy",
    "Mosaic Disease (CMD)", "Rice_BrownSpot", "Rice_Healthy", "Rice_Hispa", "Rice_LeafBlast",
    "apple_apple scab", "apple_healthy", "bacterial spot", "black rot", "cedar apple rust",
    "cherry (including sour)_healthy", "cherry (including sour)_powdery mildew", "corn (maize)",
    "corn (maize)_cercospora leaf spot gray leaf spot", "corn (maize)_common rust", "corn (maize)_healthy",
    "corn (maize)_northern leaf blight", "early blight", "grape", "grape_black rot",
    "grape_esca (black measles)", "grape_healthy", "grape_leaf blight (isariopsis leaf spot)",
    "healthy", "healthy_healthy", "late blight", "orange", "orange_haunglongbing (citrus greening)",
    "peach", "peach_bacterial spot", "peach_healthy", "pepper, bell", "squash_powdery mildew",
    "strawberry_healthy", "strawberry_leaf scorch", "tomato_bacterial spot", "tomato_early blight",
    "tomato_healthy", "tomato_late blight", "tomato_leaf mold", "tomato_septoria leaf spot",
    "tomato_spider mites two-spotted spider mite", "tomato_target spot", "tomato_tomato mosaic virus",
    "tomato_tomato yellow leaf curl virus"
]

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Helper function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Image preprocessing function
def preprocess_image(image):
    image = tf.image.resize(image, [128, 128])  # Ensure size matches model input
    image = image / 255.0  # Normalize the image
    return np.expand_dims(image, axis=0)  # Add batch dimension

# Segment leaf function
def segment_leaf(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    return cv2.bitwise_and(image, image, mask=mask)

# Combine preprocessing and prediction
def preprocess_and_predict(image_path):
    image = cv2.imread(image_path)
    if image is None:
        logging.error(f"Error reading image: {image_path}")
        return None, None, "Error: Unable to read image."

    segmented_image = segment_leaf(image)
    processed_image = preprocess_image(segmented_image)

    try:
        prediction = model.predict(processed_image)
        logging.debug(f"Prediction: {prediction}")
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return None, None, f"Error during prediction: {str(e)}"
    
    # Ensure prediction is valid
    if prediction is None or np.isnan(prediction).any():
        logging.error(f"Invalid prediction result: {prediction}")
        return None, None, "Error: Invalid prediction result."

    # Find predicted class index and confidence
    predicted_class_index = np.argmax(prediction, axis=1)[0]
    confidence = np.max(prediction, axis=1)[0] * 100  # Confidence as percentage

    if np.isnan(confidence):
        logging.error(f"Invalid confidence score: {confidence}")
        return None, None, "Error: Invalid confidence score."

    return predicted_class_index, confidence, None

# Function to classify severity
def classify_severity(confidence_score):
    if confidence_score >= 70:
        return 'Mild', 'green'  # Green for Mild
    elif 50 <= confidence_score < 70:
        return 'Moderate', 'orange'  # Orange for Moderate
    else:
        return 'Severe', 'red'  # Red for Severe

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            predicted_class_index, confidence, error = preprocess_and_predict(file_path)

            if error:
                return jsonify({'error': error})

            predicted_class = CLASS_NAMES[predicted_class_index]

            # Classify the severity based on confidence
            severity, color = classify_severity(confidence)

            # Send back JSON response with prediction, confidence, severity, and image URL
            return jsonify({
                'predicted_class': predicted_class,
                'confidence': f"{confidence:.2f}%",
                'severity': severity,
                'color': color,
                'image_url': url_for('static', filename='upload/' + filename)
            })

    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get the confidence from the front-end (could come from model prediction)
    data = request.get_json()
    confidence_score = data.get('confidence', 0)

    # Classify severity based on confidence score
    severity, color = classify_severity(confidence_score)

    response = {
        'severity': severity,
        'color': color,
        'confidence_score': confidence_score,
        'message': f'Disease is classified as {severity} with a confidence score of {confidence_score}%.'
    }

    return jsonify(response)

@app.route('/disease_diversity', methods=['POST'])
def disease_diversity():
    data = request.get_json()
    confidence_score = data.get('confidence', 0)
    
    # Classify disease severity and diversity based on confidence score
    severity, color = classify_severity(confidence_score)
    diversity_score = confidence_score  # Example: Use confidence score as diversity score

    response = {
        'severity': severity,
        'color': color,
        'diversity_score': diversity_score,
        'message': f'Disease diversity is classified as {severity} with a diversity score of {diversity_score}%.'
    }

    return jsonify(response)

@app.route('/buy-products')
def buy_products():
    return render_template('buy-products.html')

@app.route('/Contact_Us')
def contact_us():
    return render_template('Contact_Us.html')

@app.route('/Why_PlantAI')
def why_plantai():
    return render_template('Why_PlantAI.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/PlantDiseases')
def plant_diseases():
    return render_template('PlantDiseases.html')
@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/result/<filename>')  # For handling the result
def result(filename):
    return render_template('upload_success.html', filename=filename)

if __name__ == "__main__":
    app.run(debug=True)