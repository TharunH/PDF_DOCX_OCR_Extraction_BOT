import os
import logging
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from langchain_openai import ChatOpenAI
from .OCR_extraction import extract_from_text
import json
from .prompt import get_list
from .azure_python_v3 import img_text_azure
#import azure_python_v3, azure_python_v2, azure_python_v1

# Function to extract text from an image using OCR
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logging.error(f"Error occurred while processing the image: {e}")
        return None

# Function to analyze text with LLM
def analyze_text_with_llm(extracted_text):
    if not extracted_text.strip():
        return "No text found in the image."
    
    # Define LLM prompt for extraction
    prompt = f"""
    Extract the following information from the text below:
    1. Name of the Company
    
    Text: {extracted_text}
    
    Provide the output in the following format:
      "Name": "Company name"
    """
    
    # Send the prompt to the LLM
    #response = llm.invoke(input=[{"role": "user", "content": prompt}])
    #return response.content if response else "LLM response error."

# Function to crop PDF pages containing specified text
def crop_pdf_pages_with_text(pdf_path, output_folder, texts_to_detect):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    POPPLER_PATH = r"C:/Users/THARUN_H/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin"
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
  
    for i, page in enumerate(pages):
        pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
        text_1 = pytesseract.image_to_string(page)
        
        if any(text_to_detect in text_1 for text_to_detect in texts_to_detect):
            cropped_img = page.crop(page.getbbox())
            output_path = os.path.join(output_folder, f"page_{i + 1}.jpeg")
            cropped_img.save(output_path, 'JPEG', quality=100)
        else:
            logging.warning(f"No specified text found on page {i + 1}.")

# Function to process JPEG images and send to the appropriate Azure function
def fetch_jpeg_images(root_folder):
    for folder_name, _, filenames in os.walk(root_folder):
        filenames.sort()  # Sort filenames in ascending order
        for filename in filenames:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                image_path = os.path.join(folder_name, filename)
                extracted_text = extract_text_from_image(image_path)
                logging.warning(f"Processing {image_path} - extracted text: {extracted_text}")
                get_list(extracted_text)

                # with open(image_path, "r", encoding="utf-8", errors="ignore") as f:
                #     text = f.read()

                #     parsed_data = extract_from_text(text)

                #     # For API return
                #     print(json.dumps(parsed_data, indent=2))

                # Analyze text with LLM if required
                #analyzed_text = analyze_text_with_llm(extracted_text)
                #logging.info(f"LLM Analysis: {analyzed_text}")
                
                # Determine the correct Azure function based on the extracted company name
                #analyzed_text_upper = analyzed_text.upper() if analyzed_text else ""
                
                #if "IGP" in analyzed_text_upper:
                img_text_azure(image_path)
                #elif "RILSON" in analyzed_text_upper:
                    #azure_python_v2.img_text_azure(image_path)
                #elif "EXCELLENT" in analyzed_text_upper:
                    #azure_python_v1.img_text_azure(image_path)
                #else:
                    #logging.warning("Please upload a valid Company MTC Document")

# Example usage
#main_output_folder = "output_image"
#texts_to_detect = [""]
#crop_pdf_pages_with_text('C:/Users/THARUN_H/Desktop/Tally_Automation/OCR_Extraction/TallyAutomation/Documents/Bank Satatement/bank Statement - ENBD.pdf', main_output_folder,texts_to_detect)
#fetch_jpeg_images(main_output_folder)
