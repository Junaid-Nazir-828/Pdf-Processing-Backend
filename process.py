# import base64
# from openai import OpenAI
# import constant

# def get_text_from_image(image_path, retry_count=3):
#     """Extract text from image using OpenAI's Vision API with retries"""
#     last_error = None
    
#     client = OpenAI(api_key=constant.api)  # Replace with your API key
    
#     for attempt in range(retry_count):
#         try:
#             with open(image_path, "rb") as image_file:
#                 encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
#             response = client.chat.completions.create(
#                 model="gpt-4o",  # Use gpt-4-vision-preview as it's still the correct model name
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": "Please extract all the text from this image. If you see any text in the image, provide it exactly as written. If you can't see the text clearly, mention which parts are unclear."
#                             },
#                             {
#                                 "type": "image_url",
#                                 "image_url": {
#                                     "url": f"data:image/jpeg;base64,{encoded_image}"
#                                 }
#                             }
#                         ]
#                     }
#                 ],
#                 max_tokens=1000
#             )
            
#             extracted_text = response.choices[0].message.content
#             if "I'm sorry, I can't help with" in extracted_text:
#                 if attempt < retry_count - 1:
#                     print(f"Retrying image {image_path} (attempt {attempt + 1})")
#                     continue
#             return extracted_text
            
#         except Exception as e:
#             last_error = str(e)
#             if attempt < retry_count - 1:
#                 print(f"Error on attempt {attempt + 1}: {e}")
#                 continue
            
#     return f"Failed to extract text after {retry_count} attempts. Last error: {last_error}"

import base64
from openai import OpenAI
import constant

def get_text_from_image(image_path, retry_count=3):
    """Extract text from image using OpenAI's Vision API with retries"""
    last_error = None
   
    client = OpenAI(api_key=constant.api)  # Replace with your API key
   
    for attempt in range(retry_count):
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
           
            response = client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4-vision-preview as it's still the correct model name
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all the text from this image. If you see any text in the image, provide it exactly as written. If you can't see the text clearly, mention which parts are unclear."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )
           
            extracted_text = response.choices[0].message.content
            if "I'm sorry, I can't help with" in extracted_text:
                if attempt < retry_count - 1:
                    print(f"Retrying image {image_path} (attempt {attempt + 1})")
                    continue
            return extracted_text
           
        except Exception as e:
            last_error = str(e)
            if attempt < retry_count - 1:
                print(f"Error on attempt {attempt + 1}: {e}")
                continue
           
    return f"Failed to extract text after {retry_count} attempts. Last error: {last_error}"

def analyze_text_with_openai(text, prompt):
    """Analyze the extracted text using OpenAI API with the given prompt"""
    try:
        client = OpenAI(api_key=constant.api)
        
        # Combine the prompt with the text for analysis
        full_prompt = f"{prompt}\n\nTEXTO A EVALUAR:\n\n{text}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ],
            max_tokens=2000
        )
        
        analysis_result = response.choices[0].message.content
        return analysis_result
    
    except Exception as e:
        print(f"Error analyzing text with OpenAI: {e}")
        return f"Error in analysis: {str(e)}"