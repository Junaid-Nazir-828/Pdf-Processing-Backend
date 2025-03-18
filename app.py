from flask import Flask, request, jsonify
from utils import generate_random_string
from background import process_pdf_in_background
import threading
import traceback

# Import our MongoDB service
from mongodb_service import MongoDBService

app = Flask(__name__)
mongo_service = MongoDBService()


@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Get analysis_id from form data
        analysis_id = request.form.get('analysis_id')
        if not analysis_id:
            return jsonify({'error': 'No analysis ID provided'}), 400
        
        # Save the PDF
        temp_pdf_path = f"temp_{generate_random_string()}.pdf"
        pdf_file.save(temp_pdf_path)
        
        # Start background processing thread
        thread = threading.Thread(
            target=process_pdf_in_background,
            args=(temp_pdf_path, analysis_id)
        )
        thread.daemon = True  # Allow the main program to exit even if thread is running
        thread.start()
        
        # Return immediately
        return jsonify({
            'status': 'processing',
            'message': 'PDF processing started in background',
            'analysis_id': analysis_id
        })
    
    except Exception as e:
        # Log the full error with traceback
        print(f"Error initiating PDF processing: {e}")
        traceback.print_exc()
        
        # Update database with error status
        # try:
        #     if 'analysis_id' in locals():
        #         mongo_service.update_analysis_status(analysis_id, "FAILED", error_message=str(e))
        # except Exception as db_error:
        #     print(f"Error updating database: {db_error}")
            
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok'})

@app.teardown_appcontext
def teardown_db(exception=None):
    """Close MongoDB connection when app context ends"""
    mongo_service.close_connection()

if __name__ == '__main__':
    app.run(debug=True)
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)