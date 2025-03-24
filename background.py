# from utils import generate_random_string
# from process import get_text_from_image
# from convert import pdf_to_images_without_poppler
# from mongodb_service import MongoDBService
# import os
# import traceback

# def process_pdf_in_background(pdf_path, analysis_id, output_folder=None, image_paths=None):
#     """Process PDF in a background thread"""
#     try:
#         mongo_service = MongoDBService()
#         # Only generate images if they weren't passed in
#         if not output_folder or not image_paths:
#             output_folder, image_paths = pdf_to_images_without_poppler(pdf_path)
        
#         extracted_texts = []
#         for image_path in image_paths:
#             print(f"Extracting text from {image_path}")
#             text = get_text_from_image(image_path)
#             page_num = image_path.split('_')[-1].split('.')[0]
#             extracted_texts.append({
#                 'page': page_num,
#                 'text': text
#             })
        
#         # Update database with results
#         success = mongo_service.update_analysis_results(analysis_id, extracted_texts)
        
#         if not success:
#             print("Failed to update analysis results")
#             mongo_service.update_analysis_status(analysis_id, "FAILED", 
#                                                error_message="Failed to update analysis results")
#             return
#         print("Analysis results updated successfully")
#         # Update status to completed
#         mongo_service.update_analysis_status(analysis_id, "COMPLETED")
        
#         # Cleanup
#         # os.remove(pdf_path)
#         # for image_path in image_paths:
#         #     os.remove(image_path)
#         #     if os.path.exists(f"{image_path}_optimized.jpg"):
#         #         os.remove(f"{image_path}_optimized.jpg")
#         # os.rmdir(output_folder)
        
#     except Exception as e:
#         print(f"Background processing error: {e}")
#         traceback.print_exc()
        
#         # Update database with error status
#         try:
#             mongo_service.update_analysis_status(analysis_id, "FAILED", error_message=str(e))
#         except Exception as db_error:
#             print(f"Error updating database: {db_error}")

from process import get_text_from_image, analyze_text_with_openai
from convert import pdf_to_images_without_poppler
from mongodb_service import MongoDBService
import traceback

def process_pdf_in_background(pdf_path, analysis_id, output_folder=None, image_paths=None):
    """Process PDF in a background thread with word limit of 4000"""
    try:
        mongo_service = MongoDBService()
        # Only generate images if they weren't passed in
        if not output_folder or not image_paths:
            output_folder, image_paths = pdf_to_images_without_poppler(pdf_path)
        
        extracted_texts = []
        total_words = 0
        combined_text = ""
        
        # Update status to processing
        mongo_service.update_analysis_status(analysis_id, "PROCESSING")
        
        for image_path in image_paths:
            print(f"Extracting text from {image_path}")
            text = get_text_from_image(image_path)
            page_num = image_path.split('_')[-1].split('.')[0]
            print(f'--- Page {page_num} ----')
            print(text)
            
            # Count words in current page
            current_page_words = len(text.split())
            total_words += current_page_words
            
            # Add the text to our collection
            extracted_texts.append({
                'page': page_num,
                'text': text,
                'word_count': current_page_words
            })
            
            combined_text += text + "\n\n"
            
            print(f"Page {page_num}: {current_page_words} words, Total: {total_words} words")
            
            # Check if we've hit our word limit
            if total_words >= 4000:
                print(f"Word limit of 4000 reached after page {page_num}")
                break
        
        # Now analyze the collected text
        f = open("prompt.txt", "r", encoding="utf8")
        analysis_prompt = f.read()
        
        # Perform analysis with OpenAI
        analysis_result = analyze_text_with_openai(combined_text, analysis_prompt)
        with open("analysis_result.txt", "w+", encoding="utf-8") as file:
            file.write(analysis_result)

        print("Analysis saved to 'analysis_result.txt'")

        # Add analysis and metadata to results
        result_data = analysis_result
        # {
        #     'extracted_text_pages': extracted_texts,
        #     'total_words': total_words,
        #     'pages_processed': len(extracted_texts),
        #     'total_pages': len(image_paths),
        #     'word_limit_reached': word_limit_reached,
        #     'analysis_result': analysis_result
        # }
        
        # Update database with results
        success = mongo_service.update_analysis_results(analysis_id, result_data)
        
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