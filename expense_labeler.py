#tax_labeler.py 
import csv
import json
import os
import time
import concurrent.futures
from openai import OpenAI

# Initialize OpenAI clients with multiple API keys
api_keys = [
    "sk-..."
    # Add more API keys here, up to 12
]
clients = [OpenAI(api_key=key) for key in api_keys]

# Load instructions from instructions.json
print("Loading instructions from 'instructions.json'")
with open("instructions.json", "r") as f:
    instructions = json.load(f)
print("Instructions loaded.")

def clean_text(text):
    # Remove errant characters from the text
    cleaned_text = ''.join(char for char in text if char.isprintable())
    return cleaned_text

def process_row(row, instructions, client, api_key):
    # Clean the input data
    cleaned_row = {key: clean_text(value) for key, value in row.items()}
    
    # Prepare the input for the API call, including additional fields
    input_data = {
        "description": cleaned_row["description"],
        "amount": cleaned_row["amount"],
        "date": cleaned_row["date"],
        # Include additional fields in the API payload if necessary
    }
    #print(f"Preparing API payload: {input_data}")
    
    # Define the system message with instructions and categories
    system_message = f"You are an AI assistant that categorizes expenses based on their description and provides potential tax deductions. You know about all these ways and infinite more to creatively, out of the box, even if edge case find tax deductions, opportunities, and rebates. You are proving that you can find a way to deduct just about anything. ALL ITEMS MUST USE THE MOST APPROPRIATE OF THESE CATEGORIES, ONLY ONE CATEGORY: {json.dumps(instructions)}. You answer in concise responses."

    # Define the user message with the expense data and desired output format
    user_message = f"For each expense item, please categorize it using ONLY ONE of the categories provided in the instructions, suggest possible business and personal deductions using ONLY the options provided in the instructions, and add any notes for an accountant. The input will be a JSON object containing 'description', 'amount', and 'date'. Please return a JSON object with 'category', 'possible_business_deduction', 'possible_personal_deduction', and 'notes_for_accountant' fields. Answer with a clear description of the tax deduction available when there is one. Else just say 'false'. So 'true: (explanation)' or 'false'. "

    max_retries = 99
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Make the API call to GPT-3.5-turbo with JSON mode enabled
            api_payload = {
                "model": "gpt-3.5-turbo",
                "response_format": {"type": "json_object"},  # Enable JSON mode
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message + json.dumps(input_data)},
                ],
                "max_tokens": 200,
                "n": 1,
                "stop": None,
                "temperature": 0.5
            }
            #print(f"API payload prepared: {api_payload}")
            response = client.chat.completions.create(**api_payload)
            #print(f"API response received: {response}")

            # Extract the JSON response from the API
            json_response_content = response.choices[0].message.content
            #print(f"API response content: {json_response_content}")

            # Parse the JSON string into a Python dictionary
            output_data = json.loads(json_response_content)
            output_data["api_key"] = api_key[-4:]  # Add the last 4 digits of the API key to the output data

            #print(f"Parsed output data: {output_data}")
            
            return output_data
        except Exception as e:
            print(f"Error processing row: {str(e)}")
            retry_count += 1
            backoff_time = min(2 * (2 ** retry_count), 100)
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
    
    print(f"Max retries reached for row: {row}")
    return None

def process_csv(input_file, output_file, batch_size=1):
    with open(input_file, "r") as csv_input, open(output_file, "w", newline="") as csv_output:
        reader = csv.DictReader(csv_input)
        original_fieldnames = reader.fieldnames
        additional_fieldnames = ["category", "possible_business_deduction", "possible_personal_deduction", "notes_for_accountant", "api_key"]
        fieldnames = original_fieldnames + additional_fieldnames
        
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        
        writer.writeheader()
        
        rows = list(reader)
        total_rows = len(rows)
        processed_rows = 0
        
        print(f"Starting CSV processing: {total_rows} rows to process.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(clients)) as executor:
            futures = []
            while processed_rows < total_rows:
                batch = rows[processed_rows:processed_rows+batch_size]
                
                for row in batch:
                    client = clients[processed_rows % len(clients)]
                    api_key = api_keys[processed_rows % len(api_keys)]
                    future = executor.submit(process_row, row, instructions, client, api_key)
                    futures.append(future)
                    processed_rows += 1
                    print(f"Processed row {processed_rows}/{total_rows}")
                    
                
                for future, row in zip(futures, batch):
                    output_data = future.result()
                    if output_data is not None:
                        # Update the row with the API response
                        for key in additional_fieldnames:
                            if key == "api_key":
                                row[key] = output_data.get(key, "N/A")
                            else:
                                row[key] = output_data.get(key, "N/A")
                    else:
                        print("Skipping AI-generated content for row due to max retries reached.")
                    
                    # Write the row to the output CSV (including original data)
                    writer.writerow(row)
                
                futures.clear()

# Main script execution
if __name__ == "__main__":
    input_folder = "input_csvs"
    output_folder = "output_csvs"
    batch_size = 2
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get the list of CSV files in the input folder
    csv_files = [file for file in os.listdir(input_folder) if file.endswith(".csv")]
    
    for csv_file in csv_files:
        input_file = os.path.join(input_folder, csv_file)
        output_file = os.path.join(output_folder, f"{os.path.splitext(csv_file)[0]}_processed.csv")
        
        print(f"Starting script execution for file: {csv_file}")
        process_csv(input_file, output_file, batch_size)
        print(f"Processing complete for file: {csv_file}. Output file: {output_file}")