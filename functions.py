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


# Add lead to Airtable
def send_email_report(email, content):
    email="taiwoomosehin6@gmail.com"
    content="Hello"
    # Email configuration
    sender_email = 'oolasegiri@instinctwave.net'  # Your email address
    sender_password = 'Olasegiri2021@'   # Your email password
    receiver_email = email  # Recipient's email address
    subject = 'Lead Created Report'

    # Create a MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Email body content
    body = f'Lead created successfully.\n\n{content}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a secure session with Gmail's outgoing SMTP server using your gmail account
        server = smtplib.SMTP('smtp.hostinger.com', 587)
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
            }
        ],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id
