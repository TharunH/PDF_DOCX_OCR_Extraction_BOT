from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import logging,os
#from import prompt
#import prompt 


endpoint = "https://eastus.api.cognitive.microsoft.com/"
key = "f31a11c8e5694d8b9fc66dc7553b5f98"

model_id = "Tally_Automation"
#model_id='Rilson_v4'

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
source='page_*.jpeg'
def img_text_azure(source):
    try:
        with open(source, "rb") as pdf_file:
            poller = document_analysis_client.begin_analyze_document(model_id, pdf_file)
            result = poller.result()
            
            
        undesired_keywords= ['']
        desired_keywords = ['']
        row_data=[]
        for i, table in enumerate(result.tables):
           
            if any(keyword.lower() in cell.content.lower() for keyword in undesired_keywords for cell in table.cells):
                continue  
            # Check if any of the desired keywords are present in the table cells
            if any(keyword.lower() in cell.content.lower() for keyword in desired_keywords for cell in table.cells):
                columns = []
                rows = []
                
                for cell in table.cells:
                    if cell.column_index >= len(columns):
                        columns.extend([None] * (cell.column_index - len(columns) + 1))
                    if cell.row_index >= len(rows):
                        rows.extend([[]] * (cell.row_index - len(rows) + 1))
                    columns[cell.column_index] = cell.content
                    rows[cell.row_index].append(cell.content)
                
                row_data.append(rows)
                
                row =[]
                

                row_data.insert(0,row)
        
    
        #prompt.get_list(row_data)
    except Exception as e:
        logging.warning(f"An error occurred during image processing: {e}")

    finally:
        # Delete the image file after processing
        try:
            if os.path.exists(source):
                os.remove(source)
                logging.warning(f"File {source} deleted successfully.")
            else:
                logging.warning(f"File {source} not found.")
        except Exception as delete_error:
            logging.warning(f"An error occurred while deleting the file: {delete_error}")
