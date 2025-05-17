from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)

# Allowed extensions for photo uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Upload folder configuration
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your pre-trained model
MODEL_PATH = os.environ.get('MODEL_PATH', 'models/model_best.h5')  # Environment variable for model path
model = load_model(MODEL_PATH)

# Class names for prediction
class_names = [
    "Apple Scab",
    "Black Rot",
    "Cedar Apple Rust",
    "Apple Healthy",
    "Blueberry Healthy",
    "Cherry Powdery Mildew",
    "Cherry Healthy",
    "Corn Cercospora Leaf Spot",
    "Corn Common Rust",
    "Corn Northern Leaf Blight",
    "Corn Healthy",
    "Grape Black Rot",
    "Grape Esca",
    "Grape Leaf Blight",
    "Grape Healthy",
    "Orange Huanglongbing",
    "Peach Bacterial Spot",
    "Peach Healthy",
    "Pepper Bacterial Spot",
    "Pepper Healthy",
    "Potato Early Blight",
    "Potato Late Blight",
    "Potato Healthy",
    "Raspberry Healthy",
    "Soybean Healthy",
    "Squash Powdery Mildew",
    "Strawberry Leaf Scorch",
    "Strawberry Healthy",
    "Tomato Bacterial Spot",
    "Tomato Early Blight",
    "Tomato Late Blight",
    "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot",
    "Tomato Spider Mites",
    "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus",
    "Tomato Mosaic Virus",
    "Tomato Healthy"
]

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Predict disease function
def predict_disease(image_path):
    img = image.load_img(image_path, target_size=(128, 128))  # Adjust the size if needed
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize the image

    prediction = model.predict(img_array)
    return prediction

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/how_it_works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/common_diseases')
def common_diseases():
    diseases = [
        {"name": "Apple Scab", "image": "images/disease_apple_scab.jpg", "description": "Affects leaves, fruit, and stems, leading to reduced yields if left untreated."},
        {"name": "Black Rot", "image": "images/disease_black_rot.jpg", "description": "Can spread quickly during wet conditions, causing significant crop damage."},
        {"name": "Cedar Apple Rust", "image": "images/disease_cedar_apple_rust.jpg", "description": "Alternates between apples and juniper trees, leading to severe defoliation."},
        {"name": "Powdery Mildew (Cherry)", "image": "images/disease_powdery_mildew.jpg", "description": "Reduces photosynthesis, weakening the tree and lowering fruit quality."},
        {"name": "Cercospora Leaf Spot (Corn)", "image": "images/disease_cercospora_leaf_spot.jpg", "description": "Causes yield loss due to leaf blight and poor grain development."},
        {"name": "Common Rust (Corn)", "image": "images/disease_common_rust.jpg", "description": "Reduces photosynthetic efficiency, leading to yield decline."},
        {"name": "Northern Leaf Blight (Corn)", "image": "images/disease_northern_leaf_blight.jpg", "description": "Causes large leaf lesions, affecting photosynthesis and grain fill."},
        {"name": "Black Rot (Grape)", "image": "images/disease_black_rot_grape.jpg", "description": "Leads to premature defoliation and fruit rotting, reducing harvest quality."},
        {"name": "Esca (Grape)", "image": "images/disease_esca_grape.jpg", "description": "Affects wood and leaves, causing black streaks and dieback."},
        {"name": "Huanglongbing (Orange)", "image": "images/disease_huanglongbing.jpeg", "description": "A bacterial disease that causes fruit to become bitter and drop prematurely."},
        {"name": "Bacterial Spot (Peach)", "image": "images/disease_bacterial_spot_peach.jpg", "description": "Causes leaf spots, defoliation, and reduced fruit yield."},
        {"name": "Early Blight (Potato)", "image": "images/disease_early_blight_potato.jpg", "description": "Leads to dark spots on leaves, affecting plant growth and tuber development."},
        {"name": "Late Blight (Potato)", "image": "images/disease_late_blight_potato.jpg", "description": "Results in lesions and rapid decay of leaves and tubers, especially under wet conditions."},
        {"name": "Bacterial Spot (Pepper)", "image": "images/disease_bacterial_spot_pepper.jpg", "description": "Causes spots on leaves, fruits, and stems, leading to poor fruit quality."},
        {"name": "Powdery Mildew (Squash)", "image": "images/disease_powdery_mildew_squash.jpg", "description": "White powdery coating on leaves, affecting plant growth and yield."},
        {"name": "Septoria Leaf Spot (Tomato)", "image": "images/disease_septoria_leaf_spot_tomato.jpg", "description": "Causes dark, circular spots on tomato leaves, reducing photosynthesis and yield."},
        {"name": "Spider Mites (Tomato)", "image": "images/disease_spider_mites_tomato.jpg", "description": "Tiny pests that cause stippling and leaf yellowing, leading to weak plants."},
        {"name": "Target Spot (Tomato)", "image": "images/disease_target_spot_tomato.jpg", "description": "Results in round spots with concentric rings on leaves and stems."},
        {"name": "Yellow Leaf Curl Virus (Tomato)", "image": "images/disease_yellow_leaf_curl_tomato.jpg", "description": "Virus causing leaf curl, stunted growth, and poor fruit production."},
        {"name": "Mosaic Virus (Tomato)", "image": "images/disease_mosaic_virus_tomato.jpg", "description": "Causes yellow and green mottling on leaves and affects tomato growth."},
    ]
    return render_template('common_diseases.html', diseases=diseases)

@app.route('/search', methods=['POST'])
def search():
    diseases = [
        {"name": "Apple Scab", "image": "images/disease_apple_scab.jpg", "description": "Affects leaves, fruit, and stems, leading to reduced yields if left untreated."},
        {"name": "Black Rot", "image": "images/disease_black_rot.jpg", "description": "Can spread quickly during wet conditions, causing significant crop damage."},
        {"name": "Cedar Apple Rust", "image": "images/disease_cedar_apple_rust.jpg", "description": "Alternates between apples and juniper trees, leading to severe defoliation."},
        {"name": "Powdery Mildew (Cherry)", "image": "images/disease_powdery_mildew.jpg", "description": "Reduces photosynthesis, weakening the tree and lowering fruit quality."},
        {"name": "Cercospora Leaf Spot (Corn)", "image": "images/disease_cercospora_leaf_spot.jpg", "description": "Causes yield loss due to leaf blight and poor grain development."},
        {"name": "Common Rust (Corn)", "image": "images/disease_common_rust.jpg", "description": "Reduces photosynthetic efficiency, leading to yield decline."},
        {"name": "Northern Leaf Blight (Corn)", "image": "images/disease_northern_leaf_blight.jpg", "description": "Causes large leaf lesions, affecting photosynthesis and grain fill."},
        {"name": "Black Rot (Grape)", "image": "images/disease_black_rot_grape.jpg", "description": "Leads to premature defoliation and fruit rotting, reducing harvest quality."},
        {"name": "Esca (Grape)", "image": "images/disease_esca_grape.jpg", "description": "Affects wood and leaves, causing black streaks and dieback."},
        {"name": "Huanglongbing (Orange)", "image": "images/disease_huanglongbing.jpg", "description": "A bacterial disease that causes fruit to become bitter and drop prematurely."},
        {"name": "Bacterial Spot (Peach)", "image": "images/disease_bacterial_spot_peach.jpg", "description": "Causes leaf spots, defoliation, and reduced fruit yield."},
        {"name": "Early Blight (Potato)", "image": "images/disease_early_blight_potato.jpg", "description": "Leads to dark spots on leaves, affecting plant growth and tuber development."},
        {"name": "Late Blight (Potato)", "image": "images/disease_late_blight_potato.jpg", "description": "Results in lesions and rapid decay of leaves and tubers, especially under wet conditions."},
        {"name": "Bacterial Spot (Pepper)", "image": "images/disease_bacterial_spot_pepper.jpg", "description": "Causes spots on leaves, fruits, and stems, leading to poor fruit quality."},
        {"name": "Powdery Mildew (Squash)", "image": "images/disease_powdery_mildew_squash.jpg", "description": "White powdery coating on leaves, affecting plant growth and yield."},
        {"name": "Septoria Leaf Spot (Tomato)", "image": "images/disease_septoria_leaf_spot_tomato.jpg", "description": "Causes dark, circular spots on tomato leaves, reducing photosynthesis and yield."},
        {"name": "Spider Mites (Tomato)", "image": "images/disease_spider_mites_tomato.jpg", "description": "Tiny pests that cause stippling and leaf yellowing, leading to weak plants."},
        {"name": "Target Spot (Tomato)", "image": "images/disease_target_spot_tomato.jpg", "description": "Results in round spots with concentric rings on leaves and stems."},
        {"name": "Yellow Leaf Curl Virus (Tomato)", "image": "images/disease_yellow_leaf_curl_tomato.jpg", "description": "Virus causing leaf curl, stunted growth, and poor fruit production."},
        {"name": "Mosaic Virus (Tomato)", "image": "images/disease_mosaic_virus_tomato.jpg", "description": "Causes yellow and green mottling on leaves and affects tomato growth."},
        {"name": "Healthy Apple", "image": "images/apple_healthy.jpg", "description": "A healthy apple tree with no visible disease symptoms."},
        {"name": "Healthy Peach", "image": "images/peach_healthy.jpg", "description": "A healthy peach tree with vibrant green leaves and healthy fruit."},
        {"name": "Healthy Corn", "image": "images/corn_healthy.jpg", "description": "A healthy corn plant with no signs of disease or damage."},
        {"name": "Healthy Grape", "image": "images/grape_healthy.jpg", "description": "A healthy grapevine free from disease and producing good quality fruit."},
        {"name": "Healthy Tomato", "image": "images/tomato_healthy.jpg", "description": "A healthy tomato plant, thriving with no signs of pest or disease damage."}
    ]
    query = request.json.get('query', '').lower()
    filtered = [d for d in diseases if query in d['name'].lower()]
    return jsonify(filtered)


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    disease_precautions = {
        "Apple Scab": {
            "Description": "Apple scab is caused by the fungus Venturia inaequalis. It creates olive-green to black spots on leaves, fruits, and stems, leading to early defoliation and poor-quality fruit. The disease thrives in cool, wet weather and can cause significant yield loss if untreated.",
            "Precautions": [
                "Prune and dispose of infected leaves and twigs to minimize fungal spread.",
                "Use fungicides containing captan or mancozeb before bud break.",
                "Ensure good air circulation by properly spacing trees and keeping the orchard clean of debris.",
                "Select resistant varieties like Enterprise and Liberty."
            ]
        },
        "Black Rot": {
            "Description": "Black rot is caused by the fungus Botryosphaeria obtusa and primarily affects apples. Symptoms include leaf spots, fruit rot, and branch cankers. Wet and humid conditions exacerbate the disease, leading to rapid spread.",
            "Precautions": [
                "Remove and destroy all infected plant parts, including mummified fruits and fallen leaves.",
                "Apply fungicides such as thiophanate-methyl or copper-based sprays during wet seasons.",
                "Avoid wounding trees, as it provides entry points for the fungus.",
                "Maintain proper orchard hygiene and reduce humidity by pruning dense canopies."
            ]
        },
        "Cedar Apple Rust": {
            "Description": "Cedar apple rust is a fungal disease caused by Gymnosporangium juniperi-virginianae. It requires both apple and cedar (juniper) trees to complete its lifecycle. On apples, it causes yellow spots on leaves and fruit deformities, while on cedars, it forms galls.",
            "Precautions": [
                "Remove nearby cedar or juniper trees if feasible, or prune galls from cedars in winter.",
                "Apply fungicides, such as myclobutanil or propiconazole, in early spring.",
                "Grow resistant apple cultivars like Freedom or Redfree.",
                "Avoid planting apples near cedar trees to break the lifecycle of the fungus."
            ]
        },
        "Apple Healthy": {
            "Description": "Healthy apple trees are free of any fungal or bacterial infections and exhibit normal growth with vibrant green leaves and quality fruit production.",
            "Precautions": [
                "Ensure proper irrigation and nutrients for optimal tree health.",
                "Prune dead or diseased branches to maintain airflow and sunlight penetration.",
                "Monitor for pest activity and address it promptly."
            ]
        },
        "Blueberry Healthy": {
            "Description": "Healthy blueberry plants have vibrant green leaves, abundant berries, and a robust root system, without signs of disease or pest infestation.",
            "Precautions": [
                "Ensure well-drained acidic soil for optimal blueberry growth.",
                "Mulch around the base of the plants to retain moisture and prevent weed growth.",
                "Monitor for pests and apply organic insecticides if needed."
            ]
        },
        "Cherry Powdery Mildew": {
            "Description": "Powdery mildew on cherry trees is caused by the fungus Podosphaera clandestina. It forms a white, powdery layer on leaves, buds, and fruits, weakening the tree and reducing fruit quality.",
            "Precautions": [
                "Apply sulfur-based fungicides or potassium bicarbonate at the first sign of infection.",
                "Ensure good air circulation and prune to increase sunlight exposure.",
                "Remove and destroy infected leaves and twigs.",
                "Avoid excessive nitrogen fertilizers, as they promote lush growth susceptible to infection."
            ]
        },
        "Cherry Healthy": {
            "Description": "Healthy cherry trees have strong, healthy branches and vibrant leaves, with no signs of fungal or bacterial infections.",
            "Precautions": [
                "Prune regularly to remove dead or diseased branches.",
                "Ensure adequate water, nutrients, and sun exposure for optimal health."
            ]
        },
        "Corn Cercospora Leaf Spot": {
            "Description": "Caused by Cercospora zeae-maydis, this disease creates brown to gray leaf spots on corn, leading to premature death and reduced grain yields. It thrives in humid and wet conditions.",
            "Precautions": [
                "Practice crop rotation with non-host crops like soybeans.",
                "Plant resistant hybrids that tolerate Cercospora infections.",
                "Apply strobilurin or triazole-based fungicides at the VT stage of corn growth.",
                "Ensure good field drainage and reduce crop residue after harvest."
            ]
        },
        "Corn Common Rust": {
            "Description": "Common rust, caused by Puccinia sorghi, is a fungal disease that forms rust-colored pustules on leaves. Severe infections can reduce photosynthesis and weaken plants.",
            "Precautions": [
                "Grow rust-resistant corn varieties.",
                "Monitor fields regularly and apply fungicides at the first sign of infection.",
                "Avoid overcrowded planting, which reduces air circulation.",
                "Remove and destroy infected plant debris post-harvest."
            ]
        },
        "Corn Northern Leaf Blight": {
            "Description": "Northern leaf blight, caused by the fungus Exserohilum turcicum, results in large, elongated lesions on corn leaves. This disease thrives in cool, moist environments.",
            "Precautions": [
                "Use resistant corn hybrids and practice crop rotation.",
                "Apply fungicides at the first sign of infection.",
                "Remove infected plant debris after harvest to reduce disease spread."
            ]
        },
        "Corn Healthy": {
            "Description": "Healthy corn plants show strong growth, with tall, vibrant leaves and robust ears of corn. No signs of disease or pest infestation are present.",
            "Precautions": [
                "Provide adequate water and nutrients during the growing season.",
                "Ensure proper spacing to reduce overcrowding and improve airflow."
            ]
        },
        "Grape Black Rot": {
            "Description": "Black rot, caused by the fungus Guignardia bidwellii, leads to black lesions on grape leaves and fruit, causing severe crop losses. The disease spreads rapidly under warm, humid conditions.",
            "Precautions": [
                "Remove and destroy infected fruit and leaves immediately.",
                "Spray fungicides like myclobutanil during bloom and fruit development stages.",
                "Prune dense foliage to enhance airflow and sunlight penetration.",
                "Use trellising systems to keep vines off the ground."
            ]
        },
        "Grape Esca": {
            "Description": "Esca, caused by fungal pathogens such as Phaeoacremonium and Phaeomoniella, leads to premature grapevine death, characterized by leaf curling and wilting.",
            "Precautions": [
                "Prune infected vines and remove diseased wood.",
                "Improve vine vigor through proper irrigation and nutrient management.",
                "Plant resistant grape varieties when possible."
            ]
        },
        "Grape Leaf Blight": {
            "Description": "Leaf blight in grapevines is caused by various fungi, resulting in dark lesions on the leaves, which hinder photosynthesis and lead to reduced fruit yields.",
            "Precautions": [
                "Apply fungicides regularly during the growing season.",
                "Prune infected vines and remove debris.",
                "Ensure proper spacing to improve airflow and reduce humidity."
            ]
        },
        "Grape Healthy": {
            "Description": "Healthy grapevines are free from disease, with lush green leaves and vigorous growth, producing high-quality fruit.",
            "Precautions": [
                "Maintain proper vine spacing and pruning for optimal growth.",
                "Monitor regularly for pests and apply preventative measures."
            ]
        },
        "Orange Huanglongbing": {
            "Description": "Huanglongbing (HLB), also known as citrus greening, is caused by the bacterium Candidatus Liberibacter asiaticus. It causes yellowing leaves, misshapen fruits, and tree decline.",
            "Precautions": [
                "Remove infected trees and destroy them to prevent spread.",
                "Use insecticides to control the vectors that transmit the disease.",
                "Maintain tree health through proper irrigation and fertilization."
            ]
        },
        "Peach Bacterial Spot": {
            "Description": "Peach bacterial spot is caused by Xanthomonas arboricola and leads to dark lesions on peach leaves and fruit, reducing fruit quality and causing defoliation.",
            "Precautions": [
                "Prune and remove infected branches.",
                "Apply copper-based fungicides during the growing season.",
                "Ensure proper spacing for good air circulation around trees."
            ]
        },
        "Peach Healthy": {
            "Description": "Healthy peach trees show no signs of disease and produce high-quality fruit with no spots or discoloration.",
            "Precautions": [
                "Ensure proper irrigation and pruning to maintain healthy growth.",
                "Monitor for pests and disease regularly."
            ]
        },
        "Pepper Bacterial Spot": {
            "Description": "Bacterial spot on pepper plants is caused by Xanthomonas campestris and leads to dark lesions on leaves, stems, and fruit, reducing plant vigor.",
            "Precautions": [
                "Remove and destroy infected plant parts.",
                "Apply copper-based bactericides to control the disease.",
                "Avoid overhead irrigation to reduce humidity on the plants."
            ]
        },
        "Pepper Healthy": {
            "Description": "Healthy pepper plants grow vigorously, with vibrant leaves and quality fruits, free from bacterial or fungal infections.",
            "Precautions": [
                "Provide adequate water, nutrients, and sunlight for optimal growth.",
                "Prune to maintain good airflow and reduce disease risk."
            ]
        },
        "Potato Early Blight": {
            "Description": "Early blight on potatoes, caused by the fungus Alternaria solani, leads to circular lesions on leaves and stems, resulting in premature plant death.",
            "Precautions": [
                "Apply fungicides such as chlorothalonil or mancozeb early in the growing season.",
                "Use resistant potato varieties.",
                "Rotate crops and remove infected debris after harvest."
            ]
        },
        "Potato Late Blight": {
            "Description": "Late blight of potato is caused by the fungus Phytophthora infestans. It leads to brown spots on leaves and tubers, causing decay and yield loss. The disease thrives in wet and cool conditions.",
            "Precautions": [
                "Apply fungicides such as chlorothalonil or mancozeb during early infection stages.",
                "Plant resistant potato varieties like Elba or Sarpo Mira.",
                "Avoid overwatering and provide good drainage in the field.",
                "Remove and destroy infected plants and tubers immediately."
            ]
        },
        "Potato Healthy": {
            "Description": "Healthy potato plants have lush green leaves, strong stems, and produce quality tubers without any disease symptoms.",
            "Precautions": [
                "Ensure proper irrigation and drainage.",
                "Remove any dead or diseased plants to prevent further infection."
            ]
        },
        "Raspberry Healthy": {
            "Description": "Healthy raspberry plants exhibit vibrant leaves, strong canes, and abundant fruit production, with no disease signs.",
            "Precautions": [
                "Ensure good soil fertility and drainage.",
                "Prune regularly to maintain healthy canes."
            ]
        },
        "Soybean Healthy": {
            "Description": "Healthy soybean plants show robust growth with strong stems, vibrant leaves, and no signs of pest or disease.",
            "Precautions": [
                "Rotate crops and manage soil fertility.",
                "Monitor for pest activity and apply pesticides as needed."
            ]
        },
        "Squash Powdery Mildew": {
            "Description": "Powdery mildew is caused by fungal pathogens such as Erysiphe cichoracearum or Podosphaera xanthii. It affects the leaves, stems, and flowers of squash plants, leading to white, powdery spots that can spread and coalesce, causing leaf yellowing and plant decline. Warm, dry conditions with high humidity favor its development.",
            "Precautions": [
                "Plant resistant varieties of squash to reduce susceptibility to the disease.",
                "Ensure adequate spacing between plants to improve air circulation and reduce humidity levels.",
                "Apply preventive fungicides, such as sulfur or potassium bicarbonate, at the first sign of the disease.",
                "Remove and destroy heavily infected leaves or plants to limit the spread of fungal spores.",
                "Water plants at the base rather than overhead to keep foliage dry and less conducive to fungal growth."
            ]
        },
        "Strawberry Leaf Scorch": {
            "Description": "Leaf scorch on strawberries is caused by environmental stress or fungal infections, leading to yellowing and browning of leaves, affecting plant health and fruit production.",
            "Precautions": [
                "Ensure proper irrigation and avoid waterlogging.",
                "Maintain good air circulation around plants.",
                "Prune affected leaves to reduce stress on the plant."
            ]
        },
        "Strawberry Healthy": {
            "Description": "Healthy strawberry plants produce strong runners, vibrant green leaves, and abundant fruit without any disease or pest infestations.",
            "Precautions": [
                "Provide well-drained soil and proper fertilization.",
                "Prune dead or diseased leaves to encourage healthy growth."
            ]
        },
        "Tomato Bacterial Spot": {
            "Description": "Bacterial spot on tomatoes, caused by Xanthomonas vesicatoria, leads to lesions on leaves and fruits, which can reduce yield.",
            "Precautions": [
                "Remove infected plant parts and destroy them.",
                "Apply copper-based bactericides as a preventive measure.",
                "Ensure good airflow by proper spacing of plants."
            ]
        },
        "Tomato Early Blight": {
            "Description": "Early blight on tomatoes is caused by the fungus Alternaria solani. It results in dark lesions on leaves, leading to early defoliation and reduced yields.",
            "Precautions": [
                "Apply fungicides such as chlorothalonil or mancozeb during the growing season.",
                "Rotate crops to minimize recurrence.",
                "Prune infected leaves and dispose of them to prevent further spread."
            ]
        },
        "Tomato Late Blight": {
            "Description": "Late blight, caused by Phytophthora infestans, causes water-soaked lesions and rapid decay in tomato leaves, stems, and fruit.",
            "Precautions": [
                "Apply fungicides at the first sign of infection.",
                "Remove infected plant material to limit spread.",
                "Water at the base of the plant to keep foliage dry."
            ]
        },
        "Tomato Leaf Mold": {
            "Description": "Leaf mold on tomatoes, caused by the fungus Passalora fulva, results in fuzzy, yellow spots on leaves.",
            "Precautions": [
                "Maintain proper airflow and spacing between plants.",
                "Prune infected leaves and stems.",
                "Apply fungicides like chlorothalonil during the growing season."
            ]
        },
        "Tomato Septoria Leaf Spot": {
            "Description": "Septoria leaf spot is caused by the fungus Septoria lycopersici. It causes small, round lesions on tomato leaves, reducing photosynthesis and yield.",
            "Precautions": [
                "Use resistant tomato varieties.",
                "Apply fungicides regularly during the growing season.",
                "Remove and destroy infected leaves."
            ]
        },
        "Tomato Spider Mites": {
            "Description": "Spider mites cause yellowing and speckling of tomato leaves. They are tiny pests that thrive in hot, dry conditions.",
            "Precautions": [
                "Use miticides or insecticidal soap to control spider mites.",
                "Ensure proper irrigation and humidity to reduce mite pressure.",
                "Remove and destroy heavily infested leaves."
            ]
        },
        "Tomato Target Spot": {
            "Description": "Target spot on tomatoes is caused by Corynespora cassiicola. It leads to concentric ring-like lesions on leaves.",
            "Precautions": [
                "Apply fungicides at the first sign of infection.",
                "Prune infected areas and remove them."
            ]
        }
    }


    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template(
                'detect.html',
                error="No file part in the request",
                disease_name=None,
                disease_info=None,
                precautions=None,
                image_path=None
            )

        file = request.files['file']

        if file.filename == '':
            return render_template(
                'detect.html',
                error="No file selected for uploading",
                disease_name=None,
                disease_info=None,
                precautions=None,
                image_path=None
            )

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Perform prediction
            predictions = predict_disease(filepath)
            predicted_index = np.argmax(predictions, axis=1)[0]
            predicted_disease = class_names[predicted_index]

            # Get precautions
            precautions_data = disease_precautions.get(predicted_disease, {"Description": "No data available", "Precautions": []})

            return render_template(
                'detect.html',
                error=None,
                disease_name=predicted_disease,
                disease_info=precautions_data['Description'],
                precautions=precautions_data['Precautions'],
                image_path=filepath
            )

    # For GET requests or initial render
    return render_template(
        'detect.html',
        error=None,
        disease_name=None,
        disease_info=None,
        precautions=None,
        image_path=None
    )

if __name__ == '__main__':
    app.run(debug=True)
