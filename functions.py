import json
import requests
import os
from openai import OpenAI
from prompts import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
# GOOGLE_CLOUD_API_KEY = os.environ['GOOGLE_CLOUD_API_KEY']
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

# Init OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)


# Add lead to Airtable
def create_lead(name, phone, address):
  url = "https://api.airtable.com/v0/appM1yx0NobvowCAg/Leads"  # Change this to your Airtable API URL
  headers = {
      "Authorization": AIRTABLE_API_KEY,
      "Content-Type": "application/json"
  }
  data = {
      "records": [{
          "fields": {
              "Name": name,
              "Phone": phone,
              "Address": address
          }
      }]
  }
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200:
    print("Lead created successfully.")
    return response.json()
  else:
    print(f"Failed to create lead: {response.text}")


# Function to calculate ad cost for a traffic source
def calculate_ad_cost(visitors, acquisition_type, cpm, cpc):
    if acquisition_type == "impression":
        # return cpm * visitors
        print(cpm * visitors)
    elif acquisition_type == "clicks":
        # return cpc * visitors
        print(cpc * visitors)
    else:
        # return 0
        print(0)


# Function to calculate total ad cost for all traffic sources
def calculate_total_ad_cost(traffic_sources):
    total_ad_cost = 0
    for source in traffic_sources:
        total_ad_cost += source["ad_cost"]
    return total_ad_cost

# Function to calculate total ad cost for all product types
def calculate_total_ad_cost_for_products(products):
    total_ad_cost = 0
    for product in products:
        total_ad_cost += calculate_total_ad_cost(product["traffic_sources"])
    return total_ad_cost


# Function to calculate potential lead for a traffic source
def calculate_potential_leads(visitors, ctr):
    return ctr * visitors


# Function to calculate total potential_leads for all traffic sources
def calculate_total_potential_leads(traffic_sources):
    total_potential_lead = 0
    for source in traffic_sources:
        total_potential_lead += source["potential_lead"]
    return total_potential_lead

# Function to calculate total ad cost for all product types
def calculate_total_potential_leads_for_products(products):
    total_potential_lead = 0
    for product in products:
        total_potential_lead += calculate_total_potential_leads(product["traffic_sources"])
    return total_potential_lead


# Function to calculate total closed customers for a traffic source
def calculate_total_closed_customers(traffic_sources):
    total_closed_customers = 0
    for source in traffic_sources:
        total_closed_customers += source["closed_customers"]
    return total_closed_customers

def calculate_total_closed_customers_for_products(products):
    total_closed_customers = 0
    for product in products:
        total_closed_customers += calculate_total_ad_cost(product["traffic_sources"])
    return total_closed_customers


# Function to calculate total closed customers for a traffic source
def calculate_total_visitors(traffic_sources):
    total_visitors = 0
    for source in traffic_sources:
        total_visitors += source["visitors"]
    return total_visitors

def calculate_total_monthly_revenue(products):
    total_visitors = 0
    for source in products:
        total_visitors += source["monthly_revenue"]
    return total_visitors

def calculate_total_product_cost(products):
    total_product_cost = 0
    for source in products:
        total_product_cost += source["actual_product_cost"]
    return total_product_cost

# Function to calculate total Operating expenses in different categories
def calculate_total_expenses(expenses):
    total_expenses = sum(expenses.values())
    return total_expenses

# Function to calculate total Overhead expenses in different categories
def calculate_total_overhead_expenses(overhead_expenses):
    total_overhead_expenses = sum(overhead_expenses.values())
    return total_overhead_expenses


# send email
def send_email(email, subject, content):
    email=email
    content=content
    # Email configuration
    sender_email = os.environ['HOST_EMAIL_ADDRESS']
    sender_password = os.environ['HOST_EMAIL_PASSWORD']   # Your email password
    receiver_email = email  # Recipient's email address
    subject = subject

    # Create a MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Email body content
    body = f'\n\n{content}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a secure session with Gmail's outgoing SMTP server using your gmail account
        server = smtplib.SMTP(os.environ['HOST_EMAIL_SERVER'], os.environ['HOST_EMAIL_PORT'])
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("Email report sent successfully.")
    except Exception as e:
        print(f"Failed to send email report: {str(e)}")

# send_email_report(["taiwoomosehin6@gmail.com","tertimothy@gmail.com","olasegirioluwafemi@gmail.com"], "content")



# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # If no assistant.json is present, create a new assistant using the below specifications

    # To change the knowledge document, modifiy the file name below to match your document
    # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
    file = client.files.create(file=open("knowledgebase.txt", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(
        # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
        instructions=assistant_instructions,
        model="gpt-3.5-turbo-1106",
        tools=[
            {
                "type": "retrieval"  # This adds the knowledge base as a tool
            },
            {
                "type": "function",  # This adds the lead capture as a tool
                "function": {
                    "name": "create_lead",
                    "description":
                    "Capture lead details and save to Airtable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the lead."
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the lead."
                            },
                            "address": {
                                "type": "string",
                                "description": "Address of the lead."
                            }
                        },
                        "required": ["name", "phone", "address"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_ad_cost",
                    "description": "Calculate the cost of advertising based on different acquisition types.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "visitors": {
                                "type": "integer",
                                "description": "Number of visitors or impressions."
                            },
                            "acquisition_type": {
                                "type": "string",
                                "description": "Type of acquisition ('impression' or 'clicks')."
                            },
                            "cpm": {
                                "type": "number",
                                "description": "Cost per thousand impressions (CPM) in dollars."
                            },
                            "cpc": {
                                "type": "number",
                                "description": "Cost per click (CPC) in dollars."
                            }
                        },
                        "required": ["visitors", "acquisition_type", "cpm", "cpc"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "Send an email to user specified address, requests email if does not have it yet and the user must provide content generate content if content doesn't exist, the system should try to create one",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Recipient's email address."},
                            "subject": {"type": "string", "description": "Subject of the email."},
                            "content": {"type": "string", "description": "Content of the email."}
                        },
                        "required": ["email", "subject", "content"]
                    }
                }
            }
        ],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id
