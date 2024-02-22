from flask import Flask, render_template, send_file, request
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr')
def generate_qr():
    data = request.args.get('data')
    filename = request.args.get('filename')

    # Generate QR code
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
    # Google This function typically removes spaces, replaces certain characters with underscores, and ensures that the filename is safe for storage on various file systems.
    secure_filename_str = secure_filename(filename)

    # Save QR code with filename
    temp_filename = f'{secure_filename_str}_qr.png'
    img.save(temp_filename)

    # Return the QR code image
    return send_file(temp_filename, mimetype='image/png', as_attachment=True, download_name=f'{secure_filename_str}_qrcode.png')

if __name__ == '__main__':
    app.run(debug=True)

#TO RUN
# python main.py