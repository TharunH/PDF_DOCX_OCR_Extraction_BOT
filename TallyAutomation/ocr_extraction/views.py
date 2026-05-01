import os,logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework import status
from .pdf_to_img import crop_pdf_pages_with_text, fetch_jpeg_images
from .azure_python_v3 import img_text_azure


# Directory to store uploaded PDF files
UPLOAD_FOLDER = os.path.join(settings.BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@api_view(['POST'])
def upload_pdf(request):    
    try:
        file = request.data.get('file')
    
        if not file.name.endswith('.pdf'):
            return Response({'error': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file to the uploads folder
        filename = os.path.join(UPLOAD_FOLDER, file.name)
        with open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        main_output_folder = os.path.join(settings.BASE_DIR, "output_image")
        #texts_to_detect = ['CHEMICAL ANALYSIS','MECHANICAL PROPERTIES','CHEMICAL ANALYSIS','CHEMICAL PROPERTIES :',' CHEMICAL PROPERTIES : ','MECHANICAL PROPERTIES','CHEMICAL ANALYSIS',"Chemical Composition (%)", 'Mechanical Properties' ]
        
        # Assuming the same method signatures 
        crop_pdf_pages_with_text(filename, main_output_folder,texts_to_detect = [""])
        fetch_jpeg_images(main_output_folder)
        images = [os.path.join(main_output_folder, f) for f in os.listdir(main_output_folder) if f.endswith('.jpeg')]


          # Continue with processing...
        #for image in images:
            # Call the Azure Form Recognizer for each image
            #img_text_azure(image)
        
            #return Response({'message': 'Document Processing completed successfully'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'File uploaded successfully', 'filename': filename}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

