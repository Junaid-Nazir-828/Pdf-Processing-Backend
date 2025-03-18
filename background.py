from utils import generate_random_string
from process import get_text_from_image
from convert import pdf_to_images_without_poppler
from mongodb_service import MongoDBService
import os
import traceback

def process_pdf_in_background(pdf_path, analysis_id, output_folder=None, image_paths=None):
    """Process PDF in a background thread"""
    try:
        mongo_service = MongoDBService()
        # Only generate images if they weren't passed in
        if not output_folder or not image_paths:
            output_folder, image_paths = pdf_to_images_without_poppler(pdf_path)
        
        extracted_texts = []
        for image_path in image_paths:
            print(f"Extracting text from {image_path}")
            text = get_text_from_image(image_path)
            page_num = image_path.split('_')[-1].split('.')[0]
            extracted_texts.append({
                'page': page_num,
                'text': text
            })
        
        # Update database with results
        success = mongo_service.update_analysis_results(analysis_id, extracted_texts)
        
        if not success:
            print("Failed to update analysis results")
            mongo_service.update_analysis_status(analysis_id, "FAILED", 
                                               error_message="Failed to update analysis results")
            return
        print("Analysis results updated successfully")
        # Update status to completed
        mongo_service.update_analysis_status(analysis_id, "COMPLETED")
        
        # Cleanup
        # os.remove(pdf_path)
        # for image_path in image_paths:
        #     os.remove(image_path)
        #     if os.path.exists(f"{image_path}_optimized.jpg"):
        #         os.remove(f"{image_path}_optimized.jpg")
        # os.rmdir(output_folder)
        
    except Exception as e:
        print(f"Background processing error: {e}")
        traceback.print_exc()
        
        # Update database with error status
        try:
            mongo_service.update_analysis_status(analysis_id, "FAILED", error_message=str(e))
        except Exception as db_error:
            print(f"Error updating database: {db_error}")