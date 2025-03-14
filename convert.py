from utils import generate_random_string
import fitz
import os
from PIL import Image
import io

def optimize_image(image_path):
    """Optimize image for better OCR results"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if image is in RGBA mode
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize if image is too large (OpenAI has a size limit)
            max_size = 2048
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Adjust quality and save
            optimized_path = f"{image_path}_optimized.jpg"
            img.save(optimized_path, 'JPEG', quality=95, optimize=True)
            return optimized_path
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return image_path
    
def pdf_to_images_without_poppler(pdf_path):
    try:
        random_suffix = generate_random_string()
        output_folder = f"output_images_{random_suffix}"
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        pdf_document = fitz.open(pdf_path)
        image_paths = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            # Increase the resolution for better quality
            zoom = 2  # Increase this value for higher resolution
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            image_filename = os.path.join(output_folder, f"page_{page_num + 1}.png")
            pix.save(image_filename)
            
            # Optimize the saved image
            optimized_path = optimize_image(image_filename)
            image_paths.append(optimized_path)
            print(f"Saved and optimized: {optimized_path}")
            
        pdf_document.close()
        return output_folder, image_paths
    except Exception as e:
        print(f"An error occurred: {e}")
        raise