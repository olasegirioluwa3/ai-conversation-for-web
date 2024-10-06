import json
import os
import time
from flask import Flask, request, jsonify, render_template
import openai
from openai import OpenAI
import functions
import json
import time

def email_results_prompt_handler(client, thread_id, run_id, tool_call):
    # Process email
    print("In email prompt handler");
    arguments = json.loads(tool_call.function.arguments)
    output = functions.send_email(
        arguments["email"], 
        arguments["subject"], 
        arguments["content"]
    )
    
    print(arguments);
    # Log the output for debugging
    print(f"Output before submission: {output}")

    # Submit the tool output
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps(output)
            }
        ]
    )

def ad_cost_input_handler(client, thread_id, run_id, tool_call):
    """
    Handle the results of ad cost calculation and interaction.

    Parameters:
    - client: OpenAI client.
    - thread_id: ID of the conversation thread.
    - run_id: ID of the assistant run.
    - tool_call: Instance of the ToolCall class containing function details.
    """
    print("In ad cost results handler")

    # Extract arguments from the tool call
    arguments = json.loads(tool_call.function.arguments)
    
    # Perform the ad cost calculation
    cost = functions.calculate_ad_cost(
        arguments["visitors"],
        arguments["acquisition_type"],
        arguments["cpm"],
        arguments["cpc"]
    )

    # Log the output for debugging
    print(f"Ad Cost Calculation Output: {cost}")

    # Submit the tool output
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps(cost)
            }
        ]
    )

def create_lead_handler(client, thread_id, run_id, tool_call):
    # Process lead creation
    print("In lead creation handler");
    arguments = json.loads(tool_call.function.arguments)
    print(arguments);
    output = functions.create_lead(
        arguments["name"], 
        arguments["phone"],
        arguments["address"]
    )
    
    # Submit the tool output
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps(output)
            }
        ]
    )

    # Wait for a second before checking again
    time.sleep(1)

# Assuming `functions` is the module or class containing the send_email_report and create_lead functions.
# Make sure to replace it with the actual module or class in your code.

# Check OpenAI version compatibility
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
if current_version < required_version:
  raise ValueError(
      f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
  )
else:
  print("OpenAI version is compatible.")

# Create Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create or load assistant
assistant_id = functions.create_assistant(
    client)  # this function comes from "functions.py"


# Start conversation thread
@app.route('/start', methods=['GET'])
def start_conversation():
  print("Starting a new conversation...")
  thread = client.beta.threads.create()
  print(f"New thread created with ID: {thread.id}")
  return jsonify({"thread_id": thread.id})


# Generate response
@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  if not thread_id:
    print("Error: Missing thread_id")
    return jsonify({"error": "Missing thread_id"}), 400

  print(f"Received message: {user_input} for thread ID: {thread_id}")

  # Add the user's message to the thread
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  # Run the Assistant
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)

  # Check if the Run requires action (function call)
  while True:
      run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

      if run_status.status == 'completed':
          break
      elif run_status.status == 'requires_action':
          
          print(run_status.required_action.submit_tool_outputs);
          # Handle the function call
          for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
              if tool_call.function.name == "send_email":
                  # Prompt for email details
                  email_followup_prompt = "Sure, I'd be happy to help! Could you please provide the email address you'd like to send the message to?"
                  print(f"Assistant follow-up prompt: {email_followup_prompt}")

                  # Call the function to handle email prompt
                  email_results_prompt_handler(client, thread_id, run.id, tool_call)

              #   elif tool_call.function.name == "calculate_ad_cost":
              elif tool_call.function.name == "calculate_ad_cost":
                  # Prompt for ad cost details
                  ad_cost_prompt = """
                  To calculate the ad cost, please provide the following details:
                  - Number of visitors or impressions
                  - Acquisition type ("impression" or "clicks")
                  - Cost per thousand impressions (CPM) in dollars
                  - Cost per click (CPC) in dollars
                  """
                  print(f"Assistant follow-up prompt: {ad_cost_prompt}")

                  # You can optionally call a function to handle ad cost prompt here
                  # ad_cost_input_handler(client, thread_id, run.id, tool_call)

                  # Call the function to handle email prompt
                  ad_cost_input_handler(client, thread_id, run.id, tool_call)


              elif tool_call.function.name == "calculate_total_ad_cost_for_products":
                    # Prompt for product details
                    product_prompt = "Sure, I'd be happy to help! Could you please provide the details of the products you'd like to calculate the total ad cost for?"
                    print(f"Assistant follow-up prompt: {product_prompt}")

                    # Get the products from the user input
                    products = data.get('products', [])

                    # Call the function to handle product details
                    total_ad_cost = calculate_total_ad_cost_for_products(products)

                    # Submit the tool output with the result
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=[
                            {
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(total_ad_cost)
                            }
                        ]
                    )



            #   elif tool_call.function.name == "create_lead":
            #       # Prompt for lead information
            #       lead_followup_prompt = "Certainly! To create a lead, I need some details. What is the name of the lead you'd like to add to the CRM?"
            #       print(f"Assistant follow-up prompt: {lead_followup_prompt}")

            #       # Call the function to handle lead prompt
            #       create_lead_handler(client, thread_id, run.id, tool_call)

              time.sleep(1)  
              # Wait for a second before checking again

  # Retrieve and return the latest message from the assistant
  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  print(f"Assistant response: {response}")
  return jsonify({"response": response})



# Define routes
@app.route('/')
def index():
    return render_template('index.html')

# Define routes
@app.route('/form')
def form():
    return render_template('form.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
