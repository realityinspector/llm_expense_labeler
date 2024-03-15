# Expense Labeler

## Description
Expense Labeler is a Python script designed to automate the categorization of financial transactions for expense purposes. Utilizing OpenAI's GPT models, it reads from a CSV file, processes each transaction with AI-informed decisions on potential expense deductions, and outputs the categorized transactions into a new CSV file. It supports handling multiple transactions concurrently by leveraging Python's `concurrent.futures` and can work with multiple OpenAI API keys to distribute requests efficiently.

## THIS IS AN OPEN SOURCE RESEARCH EXPERIMENT. IT DOES NOT PROVIDE FINANCIAL ADVICE. IT'S RELEASED FOR YOUR TESTING ONLY AND SHOULD NOT BE USED FOR ANY OTHER PURPOSE.

My experience is that it was moderatly helpful. 

## Installation

Before running Expense Labeler, ensure you have Python installed on your system. This script requires Python 3.6 or newer.

1. Clone this repository to your local machine.
   ```bash
   git clone <repository-url>

    Navigate into the cloned directory.

    bash

cd <cloned-directory>

Install the required Python packages.

bash

    pip install -r requirements.txt

Requirements

    Python 3.6+
    openai Python package
    Internet access for OpenAI API calls

Usage

To use Expense Labeler, follow these steps:

    Prepare your API keys for OpenAI and add them to the api_keys list in expense_labeler.py.
    Ensure your transaction data is in CSV format and placed in the input_csvs folder. The script expects columns for "description", "amount", and "date" at a minimum.
    Run the script with the following command:

    bash

    python expense_labeler.py

    Processed files will be saved in the output_csvs folder with additional columns for expense categorization and deduction suggestions.

Customization

You can customize the script's behavior by modifying the instructions.json file to include your specific categorization rules and deduction guidelines.
License

This project is licensed under the MIT License - see the LICENSE file for details.

vbnet


Remember to replace `<repository-url>` and `<cloned-directory>` with your actual repository URL and the directory name into which you clone the repository, respectively. This README provides a comprehensive guide to get users started with your project.

