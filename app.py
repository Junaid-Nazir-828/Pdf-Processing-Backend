import os
from flask import Flask, request, jsonify
from utils import generate_random_string
from process import get_text_from_image
from convert import pdf_to_images_without_poppler

app = Flask(__name__)

@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        temp_pdf_path = f"temp_{generate_random_string()}.pdf"
        pdf_file.save(temp_pdf_path)
        
        output_folder, image_paths = pdf_to_images_without_poppler(temp_pdf_path)
        
        extracted_texts = []
        for image_path in image_paths:
            text = get_text_from_image(image_path)
            extracted_texts.append({
                'page': image_path.split('_')[-1].split('.')[0],
                'text': text
            })
        
        # Cleanup
        # os.remove(temp_pdf_path)
        # for image_path in image_paths:
        #     os.remove(image_path)
        #     if os.path.exists(f"{image_path}_optimized.jpg"):
        #         os.remove(f"{image_path}_optimized.jpg")
        # os.rmdir(output_folder)
        
        return jsonify({
            'status': 'success',
            'extracted_texts': extracted_texts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)