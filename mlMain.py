import csv
from openai import OpenAI 
import pandas as pd
import tokenize
from io import BytesIO

# Set your OpenAI API key
Ted_API_KEY = open("C:/Users/Edward.Hogan/Testing/OpenAIGPT_testing/tedApiKey.txt", "r").read()
client = OpenAI(api_key=Ted_API_KEY)

def count_tokens_in_csv_column(csv_file, column_name):
    total_tokens = 0
    df = pd.read_csv(csv_file)
    if column_name in df.columns:
        for text in df[column_name]:
            tokens = tokenize.tokenize(BytesIO(text.encode('utf-8')).readline)
            total_tokens += sum(1 for _ in tokens if _.exact_type != tokenize.INDENT and _.exact_type != tokenize.DEDENT)

    return total_tokens

def count_tokens_in_string(input_string):
    total_tokens = 0

    tokens = tokenize.tokenize(BytesIO(input_string.encode('utf-8')).readline)
    total_tokens += sum(1 for _ in tokens if _.exact_type != tokenize.INDENT and _.exact_type != tokenize.DEDENT)

    return total_tokens

def read_technician_reports(csv_file):
    """
    Read historical technician reports from a CSV file.
    Returns a list of strings containing the reports.
    """
    technician_reports = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Assuming the text is in the first column
            technician_reports.append(row[0])
    # CSV has a title row
    technician_reports = technician_reports[1:-1]
    return technician_reports

def gptTest(input_text, historical_report):
    """
    Inputs a report as a string and compares it to a list of reports
    Returns true or false as a string based on comparison
    """

    
    # Collect input text from the user
    # input_text = input("Enter the text you want to analyze: ")
    prompt = '''Search this text for instances reports that are examples of an evaporator coil freezing or being frozen. The evaporator coil may be refered to as an evap and it freezing might 
    be refered to as icing or ice up. The text in historical_reports shows examples of reports that show this. Note exclude reports of condenser ice up. This is not what is being searched for 
    If text matches return the word 'true' if not return 'false':'''
    input_text = prompt + str(input_text)

    token_cost = 0.0010/1000
    
    # tokens = count_tokens_in_string(input_text) + count_tokens_in_string(historical_report)
    # total_cost = token_cost*tokens
    # print(total_cost)
    
    # Compare input text with historical reports using OpenAI API
    response = client.chat.completions.create(
        messages=[
            {
                "role":"assistant",
                "content": historical_report,
            },

            {
                "role": "user",
                "content": input_text,
            }
        ],
        model="gpt-3.5-turbo",

        max_tokens=500,

        # engine="davinci", 
        # prompt=input_text,
        # documents=historical_reports,
        # max_tokens=100
    )

    return response.choices[0].message.content
    
    # # Get similarity score from OpenAI API response
    # similarity_score = response['choices'][0]['score']
    
    # # Set a threshold for similarity
    # similarity_threshold = 0.5
    
    # # Determine whether the input text is similar to the technician reports
    # if similarity_score >= similarity_threshold:
    #     print("The input text is similar to historical technician reports.")
    # else:
    #     print("The input text is not similar to historical technician reports.")


# Path to the CSV file containing historical technician reports
hist_csv_file = "C:/Users/Edward.Hogan/Testing/OpenAIGPT_testing/evap_reports.csv"
historical_reports = read_technician_reports(hist_csv_file)
report_string = ",".join(str(element) for element in historical_reports)

test_csv_file = "C:/Users/Edward.Hogan/Testing/OpenAIGPT_testing/OD460_Test.csv"
df = pd.read_csv(test_csv_file)

# Iterate through a table of reports categorised by a serial number and print the output
outcome = []
for i in range(len(df)):
    test_output = gptTest(df.loc[i, "RepairerNotes"], report_string)

    # Note: GPT output has to be string, hence why return value is not boolean
    if test_output == 'true':
        print("Fridge Serial: " + str(df.loc[i, "SerialNumber"]) + " is an evaporator freeze up ")
        outcome.append([str(df.loc[i, "SerialNumber"]), True])
    elif test_output == 'false':
        print("Fridge Serial: " + str(df.loc[i, "SerialNumber"]) + " is not an evaporator freeze up ")
        outcome.append([str(df.loc[i, "SerialNumber"]), False])
    else:
        print("GPT Error")
        outcome.append([str(df.loc[i, "SerialNumber"]), "-"])

df_outcome = pd.DataFrame(outcome, columns=['Serial', 'Result'])
df_outcome.to_csv(test_csv_file[0:-4] + "_outcome2.csv", index=False)