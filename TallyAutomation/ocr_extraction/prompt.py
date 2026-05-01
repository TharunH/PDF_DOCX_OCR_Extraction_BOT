import json,re,logging
from langchain_openai import ChatOpenAI
import psycopg2 
from psycopg2 import sql,IntegrityError # Updated import for ChatOpenAI

# Initialize the LLM with the correct base_url and model
llm = ChatOpenAI(
    model="llama3-8b-8192",
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)
def get_list(input_data):
    # Define the base structure for each output dictionary
    output_structure = {
        "date": "",  
        "value_date": "",  
        "bank_ref": "",  
        "customer_ref": "",  
        "description": "",  
        "debit": "",  
        "credit": "",  
        "account_no": "",  
        "iban": "",  
        "account_name": "",  
        "start_date": "",  
        "end_date": "",  
        "opening_balance": "",  
        "closing_balance": "",  
        "report_date": "",  
        "entity": ""

    }
    
    # Construct prompt
    prompt = f"""
Given the following nested list data:

{input_data}

Your task is to convert each row in this list into a separate JSON object according to the provided template:

{json.dumps(output_structure, indent=4)}

Each JSON object should represent one row of the input data with keys aligned to the template. Please format your response as a list of JSON objects, with no explanations, additional text, or extra information.
"""

    # Assuming `llm` is an object to invoke the LLM response
    response = llm.invoke(prompt)

    # Process the LLM's response to JSON format
    try:
        extracted_data = json.loads(response.content)  # Convert the response to JSON
        ##print("Extracted Data:", json.dumps(extracted_data, indent=4))
        print(extracted_data)
        #insert_data(extracted_data)
        return extracted_data
    except json.JSONDecodeError:
        logging.warning("Failed to parse JSON response. Raw response:", response.content)
        return []
    

def clean_heat_no(heat_no):
    # Regex to match and extract the heat number (e.g., C38139)
    match = re.match(r"^(?:NO\s*)?([A-Za-z0-9]+)(?:\s+TEST)?$", heat_no)
    if match:
        return match.group(1)  # Return the cleaned heat number (C38139)
    return heat_no 

def insert_data(data):
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host="my-db-instance.cv1w79xov7zb.ap-south-1.rds.amazonaws.com",
        database="spira_dev",
        user="postgres",
        password="eGgHv69!VuE",
    )
    cursor = conn.cursor()

    # Prepare insert query with dynamic column handling
    insert_query = """
    INSERT INTO mtc_v5 ({columns}) VALUES ({values})
    """

    for record in data:
    # Clean the heat_no
        heat_no = clean_heat_no(record.get("heat_no", ""))
        
        # If the cleaned heat_no is empty, skip this record
        if not heat_no or heat_no in ["STD REQUIREMENT", ""]:
            continue
        
        # Filter out invalid entries and prepare the columns and values
        columns = []
        values = []
        for key, value in record.items():
            # If the value is not one of the invalid ones, include it in the columns/values
            if value not in ["--", "", "-- --"]:
                columns.append(key)
                values.append(value)

        # Update the 'heat_no' to the cleaned value
        columns[columns.index("heat_no")] = "heat_no"  # Ensure 'heat_no' column is present
        values[columns.index("heat_no")] = heat_no  # Update the cleaned heat_no value
        logging.warning(f"Processing Heat No: {heat_no}")
        # Execute the insertion only if there are valid columns and values
        if columns and values:
            try:
                cursor.execute(
                    sql.SQL(insert_query).format(
                        columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
                        values=sql.SQL(", ").join(sql.Placeholder() * len(values))
                    ),
                    values
                )
            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    # Log the duplicate and skip this record
                    #print(f"Duplicate heat_no {heat_no} found. Skipping record.")
                    continue  # Skip this record and move to the next

    # Commit transaction and close connection
    conn.commit()
    cursor.close()
    conn.close()