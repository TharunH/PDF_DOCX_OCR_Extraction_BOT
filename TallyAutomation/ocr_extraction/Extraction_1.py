from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://tallyautomation.cognitiveservices.azure.com/"
key = "37ab9351ec524f3ab7592bd97db6d378"

client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Path to the PDF file
file_path = "TallyAutomation/Documents/Other Expenses/SATIONARY.pdf"

# Open file in binary mode
with open(file_path, "rb") as f:
    poller = client.begin_analyze_document("prebuilt-read", document=f)

result = poller.result()

# Print recognized text
for page in result.pages:
    for line in page.lines:
        print(line.content)

