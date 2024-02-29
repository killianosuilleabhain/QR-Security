from flask import Flask, render_template, request, send_file
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://kos:k0s@cluster0.g6zcayw.mongodb.net/database'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr')
def generate_qr():
    data = request.args.get('data')
    filename = request.args.get('filename') 

    # Access the 'qr_codes' collection in MongoDB
    qr_codes_collection = mongo.db.qr_codes

    # Check if the QR code already exists in the collection
    qr_code = qr_codes_collection.find_one({'data': data, 'filename': filename})

    if qr_code:
        # If it exists, increment the usage counter
        qr_codes_collection.update_one({'_id': qr_code['_id']}, {'$inc': {'uses': 1}})
    else:
        # If it doesn't exist, create a new record
        new_qr_code = {
            'data': data,
            'filename': filename,
            'uses': 1
        }
        qr_codes_collection.insert_one(new_qr_code)

    # Generate QR code as before
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Secure the filename to prevent possible security issues
    secure_filename_str = secure_filename(filename)

    # Save QR code with the specified filename
    temp_filename = f'{secure_filename_str}_qr.png'
    img.save(temp_filename)

    # Return the QR code image
    return send_file(temp_filename, mimetype='image/png', as_attachment=True, download_name=f'{secure_filename_str}_qrcode.png')

@app.route('/track_qr_code_usage')
def track_qr_code_usage():
    # Access the 'qr_codes' collection in MongoDB
    qr_codes_collection = mongo.db.qr_codes

    # Retrieve all documents from the collection
    qr_code_list = list(qr_codes_collection.find())

    return render_template('usage.html', qr_code_list=qr_code_list)

if __name__ == '__main__':
    app.run(debug=True)
