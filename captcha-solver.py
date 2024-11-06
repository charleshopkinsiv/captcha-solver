from flask import Flask, request, jsonify
from flasgger import Swagger
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import requests
import io

# Run the following command to run the http server with 4 workers
# gunicorn -w 4 captcha-solver:app

app = Flask(__name__)

@app.route('/recaptch-v2', methods=['POST'])
def recaptchav2():
    """
    Upload six images
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: search
        in: query
        type: string
        required: true
        description: The item to search for
      - name: image1
        in: formData
        type: file
        required: true
        description: The first image to upload
      - name: image2
        in: formData
        type: file
        required: true
        description: The second image to upload
      - name: image3
        in: formData
        type: file
        required: true
        description: The third image to upload
      - name: image4
        in: formData
        type: file
        required: true
        description: The fourth image to upload
      - name: image5
        in: formData
        type: file
        required: true
        description: The fifth image to upload
      - name: image6
        in: formData
        type: file
        required: true
        description: The sixth image to upload
    responses:
      200:
        description: Images successfully uploaded
        schema:
          type: object
          properties:
            message:
              type: string
              example: Images successfully uploaded
            success:
              type: array
              items:
                type: string
              description: Whether the item succeeded or not
    """

    # Get search string
    search = request.args.get('search')

    processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

    for i in range(1, 7):
        image_file = request.files.get(f'image{i}')
        if not image_file:
            return jsonify({"error": f"Image {i} is missing"}), 400
        filename = secure_filename(image_file.filename)

        image = Image.open(io.BytesIO(image_file.read()))
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        boolean = False
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            if processor.target_labels[label] == search:
                boolean = True
                break

        image_files.append(boolean)

    return jsonify({
        "message": "Images successfully uploaded",
        "success": image_files
    })


if __name__ == '__main__':
    app.run(debug=True)

