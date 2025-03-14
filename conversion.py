import fitz  # PyMuPDF
import os

def pdf_to_images_without_poppler(pdf_path, output_folder):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Loop through all pages and save as images
        for page_num in range(len(pdf_document)):
            # Get the page
            page = pdf_document[page_num]

            # Render the page to an image
            pix = page.get_pixmap()

            # Save the image
            image_filename = os.path.join(output_folder, f"page_{page_num + 1}.png")
            pix.save(image_filename)
            print(f"Saved: {image_filename}")

        print("PDF successfully converted to images.")
        pdf_document.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "file.pdf"

    # Output folder for images
    output_folder = "output_images"

    # Convert PDF to images
    pdf_to_images_without_poppler(pdf_path, output_folder)