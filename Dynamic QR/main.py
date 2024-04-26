from flask import Flask, render_template, request, redirect, send_file, url_for, session
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import qrcode
import shortuuid
import io
import base64

# Connect to my own MongoDB 
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb+srv://kos:k0s@cluster0.g6zcayw.mongodb.net/database'
mongo = PyMongo(app)

# MongoDB collections
url_collection = mongo.db.urls
qr_codes_collection = mongo.db.qr_codes  

# Shorten the URL to 8
def generate_short_url(url):
    return shortuuid.uuid()[:8]

# Route for Home page
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login')) 
    return render_template('index.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'StudentATU' and request.form['password'] == 'x@A[!|s167B6': 
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Url Shortneing
@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form.get('long_url')
    if long_url:
        short_url = generate_short_url(long_url)
        full_short_url = request.host_url + short_url
        # Sends URL to Mongo
        url_collection.insert_one({
            'short_url': short_url,
            'long_url': long_url,
            'clicks': 0
        })
        return render_template('index.html', short_url=full_short_url)
    else:
        return redirect('/')

# Redirect user to the original url which counts each visit
@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    url_data = url_collection.find_one({'short_url': short_url})
    if url_data:
        url_collection.update_one({'short_url': short_url}, {'$inc': {'clicks': 1}})
        return redirect(url_data['long_url'])
    return f'No URL found for {short_url}', 404

# QR code Generator
@app.route('/generate_qr', methods=['GET'])
def generate_qr():
    original_url = request.args.get('data')
    filename = request.args.get('filename', default='qrcode')

    short_url = generate_short_url(original_url)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(request.host_url + short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR by encoding it 
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    img_data = buf.read()
    data_url = base64.b64encode(img_data).decode('utf-8')

    # Save QR code details to Mongo
    qr_code_entry = {
        'original_url': original_url,
        'qr_code': data_url,  
        'filename': filename
    }
    qr_codes_collection.insert_one(qr_code_entry)

    # Save the QR image file
    return send_file(io.BytesIO(img_data), mimetype='image/png', as_attachment=True, download_name=f'{filename}_qrcode.png')

# Usage Statictics
@app.route('/track_qr_code_usage')
def track_qr_code_usage():
    qr_code_list = list(qr_codes_collection.find())
    urls = list(url_collection.find()) 
    return render_template('usage.html', qr_code_list=qr_code_list, urls=urls)

# Debugger + Entry Point
if __name__ == '__main__':
    app.run(debug=True)
