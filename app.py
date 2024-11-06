from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Create an images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Overlay and PDF Converter</title>
        <style>
            /* Basic reset */
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f4f4f9;
                color: #333;
            }
            .container {
                max-width: 400px;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                background-color: #fff;
                text-align: center;
            }
            h1 {
                margin-bottom: 20px;
                color: #0077cc;
            }
            label {
                display: block;
                margin: 10px 0 5px;
                font-weight: bold;
            }
            input[type="file"], input[type="text"], select, button {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                background-color: #0077cc;
                color: white;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #005fa3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Image Overlay & PDF Converter</h1>
            <form method="post" enctype="multipart/form-data" action="/process">
                <label for="image">Choose an image:</label>
                <input type="file" name="image" required>

                <label for="text">Enter overlay text:</label>
                <input type="text" name="text" placeholder="Enter text for overlay" required>

                <label for="output_type">Select output type:</label>
                <select name="output_type" required>
                    <option value="image">Image</option>
                    <option value="pdf">PDF</option>
                </select>
                
                <button type="submit">Process</button>
            </form>
        </div>
    </body>
    </html>
    '''


@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return 'No image uploaded!', 400
    
    image_file = request.files['image']
    overlay_text = request.form.get('text', '')  # Get overlay text from form
    output_format = request.form.get('output_type', 'image')  # Get output type from form

    # Load image
    image = Image.open(image_file).convert("RGBA")  # Convert to RGBA for transparency support

    # Create a drawing context
    draw = ImageDraw.Draw(image)
    # Load a larger font size for better visibility
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Calculate text size and position for bottom center
    text_bbox = draw.textbbox((0, 0), overlay_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x_position = (image.width - text_width) / 2  # Center horizontally
    y_position = image.height - text_height - 20  # Position at bottom with 20px padding

    # Define text color and background rectangle
    text_color = "white"  # White text for contrast
    background_color = (0, 0, 0, 128)  # Semi-transparent black rectangle

    # Draw rectangle behind text for readability
    draw.rectangle(
        [x_position - 10, y_position - 5, x_position + text_width + 10, y_position + text_height + 5],
        fill=background_color
    )

    # Draw the overlay text on the image
    draw.text((x_position, y_position), overlay_text, fill=text_color, font=font)

    # Handle output format
    if output_format == 'pdf':
        pdf_path = os.path.join("images", f"{os.path.splitext(image_file.filename)[0]}.pdf")
        
        # Create a PDF canvas with image dimensions
        c = canvas.Canvas(pdf_path, pagesize=(image.width, image.height))
        temp_image_path = os.path.join("images", "temp_image.png")
        image.save(temp_image_path)  # Save the image as PNG temporarily
        c.drawImage(temp_image_path, 0, 0, width=image.width, height=image.height)  # Add image to PDF
        c.save()
        os.remove(temp_image_path)  # Remove the temporary image
        return send_file(pdf_path, as_attachment=True, download_name=f"{os.path.splitext(image_file.filename)[0]}.pdf")
    else:
        image_path = os.path.join("images", f"{os.path.splitext(image_file.filename)[0]}.png")
        image.save(image_path)  # Save the image in PNG format by default
        return send_file(image_path, as_attachment=True, download_name=image_file.filename)

if __name__ == '__main__':
    app.run(debug=True)
