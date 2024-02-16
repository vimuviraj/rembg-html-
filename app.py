from flask import Flask, request, render_template, send_file, redirect, url_for
from rembg import remove
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__)

# Set up directories
os.makedirs('original', exist_ok=True)
os.makedirs('masked', exist_ok=True)

def process_image(file):
    # Save the uploaded image inside the "original" folder
    original_image_path = os.path.join('original', file.filename)
    file.save(original_image_path)

    # Remove the background from the uploaded image
    with open(original_image_path, 'rb') as f:
        input_data = f.read()
        foreground_img = Image.open(BytesIO(remove(input_data, alpha_matting=True)))

    # Generate a unique filename for the masked image
    filename = f'masked_{file.filename}.png'  # Use .png format to preserve transparency

    # Save the final composite image in the "masked" folder as PNG
    composite_image_path = os.path.join('masked', filename)
    foreground_img.save(composite_image_path, format='PNG')

    # Return the filename of the masked image
    return filename



@app.route('/')
def home():
    return render_template('index.html', error=None)


@app.route('/process_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No file part', 400

    file = request.files['image']

    if file.filename == '':
        return 'No selected file', 400

    if file:
        try:
            # Process the image and get the filename of the masked image
            masked_filename = process_image(file)

            # Redirect the user to view the background-removed image
            return redirect(url_for('result', filename=masked_filename))
        except Exception as e:
            # Handle processing errors
            return render_template('index.html', error=str(e))

    return 'Error processing the image', 500


@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', result_filename=filename)


@app.route('/download/<filename>')
def download_masked_image(filename):
    # Define the path to the background-removed image 
    masked_image_path = os.path.join('masked', filename)

    # Check if the file exists
    if os.path.exists(masked_image_path):
        # Serve the image for download using Flask's send_file method
        return send_file(masked_image_path, as_attachment=True, mimetype='image/jpeg', download_name=f'masked_{filename}')
    else:
        # Return a 404 error if the file does not exist
        return 'Image not found', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



