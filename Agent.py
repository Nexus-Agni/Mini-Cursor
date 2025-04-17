from openai import OpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

gemini_api_key = os.getenv("GOOGLE_API_KEY")

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def run_command(command):
    result = os.system(command)
    return result


available_tools = {
    "run_command": {
        "fn": run_command,
        "description": "Takes an input and executes that command on the terminal and returns an output"
    }
}

system_prompt = """
You are helpul coding based AI assistant who is expert in the field of coding and specialised in solving coding problems and resolving coding related user queries. If you are asked about anything else other than coding related queries then you will reply with a message that you are not able to help you with that.

You work on 5 steps : Start, Plan, Action, Observe and Output. 
For the given user query and available tools, plan the step by step execution, based on the planning,
select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
Wait for the observation and based on the observation from the tool call resolve the user query.

Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

Output JSON Format:
{{
    "step": "string",
    "content": "string",
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function",
}}

Available Tools : 
    - run_command

Example : 
User Query : Create a python file in the current directory with a function named sum which can used to add two numbers.
{{step : "plan", content : "User is asking to create .py file and create a function named sum which will add two numbers and return the output."}}
{{step : "plan", content : "From the available tools run_command is the most appropriate tool to create a python file and add a function named sum which will add two numbers and return the output."}}
{{step : "action", function : "run_command", input : "touch sum.py && echo 'def sum(a,b): return a+b' >> sum.py"}}
{{step : "observe", content : "Python file is created with a function named sum which can used to add two numbers."}}
{{step : "output", content : "Python file is created with a function named sum which can used to add two numbers."}}
"""

messages = [
    {"role" : "system", "content":system_prompt}
]

query = input("> : ")
messages.append({"role" : "user", "content" : query})


while True:
    response = client.chat.completions.create(
        model='gemini-2.0-flash',
        response_format={"type":"json_object"},
        messages=messages
    )

    parsed_output = json.loads(response.choices[0].message.content)
    messages.append({"role" : "assistant", "content" : json.dumps(parsed_output)})

    if parsed_output.get("step") == "plan":
        print("🧠 ... ", parsed_output)
        continue

    if parsed_output.get("step") == "action":
        tool_name = parsed_output.get("function")
        tool_input = parsed_output.get("input")

        if available_tools.get(tool_name, False) != False : 
            output = available_tools[tool_name].get("fn")(tool_input)
            messages.append({"role" : "assistant" , "content" : json.dumps({"step": "observe", "output" : output})})
    

    if parsed_output.get("step") == "output" :
        print("🤖 : ", parsed_output)
        break