from flask import Flask, render_template, request, send_file, redirect
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import qrcode
import hashlib
import shortuuid
from datetime import datetime

app = Flask(__name__)
# Configure the Flask app to use MongoDB
app.config['MONGO_URI'] = 'mongodb+srv://kos:k0s@cluster0.g6zcayw.mongodb.net/database'
mongo = PyMongo(app)

url_collection = mongo.db.urls

# Function to generate a shortened URL using a hash function
def generate_short_url(url):
    sha1_hash = hashlib.sha1(url.encode()).hexdigest()
    return sha1_hash[:8]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form.get('long_url')
    if long_url:
        short_url = shortuuid.uuid()[:8]
        full_short_url = request.host_url + short_url #testing
        url_mapping = {
            'short_url': short_url,
            'long_url': long_url,
            'clicks': 0  # Initialize click count
        }
        url_collection.insert_one(url_mapping)
        return render_template('index.html', short_url=full_short_url)
    else:
        return redirect('/')

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    url_data = url_collection.find_one({'short_url': short_url})
    if url_data:
        # Increment click count
        url_collection.update_one({'short_url': short_url}, {'$inc': {'clicks': 1}})
        return redirect(url_data['long_url'])
    else:
        return f'No URL found for {short_url}', 404


@app.route('/generate_qr')
def generate_qr():
    original_url = request.args.get('data')
    filename = request.args.get('filename') 

    # Check if the URL already exists in the collection
    url_entry = mongo.db.shortened_urls.find_one({'original_url': original_url})

    if url_entry:
        short_url = url_entry['short_url']
    else:
        short_url = generate_short_url(original_url)
        mongo.db.shortened_urls.insert_one({
            'original_url': original_url,
            'short_url': short_url,
            'clicks': 0  # Initialize click counter
        })

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    secure_filename_str = secure_filename(filename)
    temp_filename = f'{secure_filename_str}_qr.png'
    img.save(temp_filename)

    return send_file(temp_filename, mimetype='image/png', as_attachment=True, download_name=f'{secure_filename_str}_qrcode.png')

@app.route('/track_qr_code_usage')
def track_qr_code_usage():
    qr_codes_collection = mongo.db.shortened_urls
    qr_code_list = list(qr_codes_collection.find())
    return render_template('usage.html', qr_code_list=qr_code_list)

# Route to handle short URLs and redirect to the original URL
@app.route('/<short_url>')
def redirect_to_original(short_url):
    url_entry = mongo.db.shortened_urls.find_one({'short_url': short_url})
    
    if url_entry:
        original_url = url_entry['original_url']
        # Increment the click counter
        mongo.db.shortened_urls.update_one({'short_url': short_url}, {'$inc': {'clicks': 1}})
        # Redirect to the original URL
        return redirect(original_url)
    else:
        # Handle the case when the short URL is not found
        return render_template('not_found.html', short_url=short_url)

if __name__ == '__main__':
    app.run(debug=True)
