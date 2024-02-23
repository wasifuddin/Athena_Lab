from openai import OpenAI

import json
import sys
import path

dir = path.Path(__file__).abspath()
sys.path.append(dir.parent.parent)
api_key = "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"

model = "ft:gpt-3.5-turbo-1106:megamind-tech:martello-noyobo-v1:8fDuBPfs"
model = "gpt-4-turbo-previews"

llm_client = OpenAI(
    api_key=api_key,
)

session_id = "ww1204343kjrewre3"

def getSystemText(jsonFile):
    with open(jsonFile) as f: data = json.load(f)
    return data
json_path = "system_json/faq.json"

system_message = getSystemText(json_path)

message_history = []
campaign1_status = False
campaign2_status = False

functions = [
    {
        "name": "topic_discussed",
        "description": "Activates in response to user input related to Martello Alley or Martello on Brock, such as its story, location, or history. This function helps in tailoring prompts or responses to include specific information about Martello Alley, enhancing the relevance and accuracy of the generated content.",
        "parameters": {
            "type": "object",
            "properties": {
                "campaign": {
                    "type": "boolean",
                    "description": "Flag that is set to true when the user input includes mentions of Martello Alley's story, location, or historical aspects. It aids in identifying the focus of the user's interest for more targeted prompt generation."
                },
            },
        },
    }
]


def campain_function_call(answer):
    global model, message_history, functions, session_id
    try:
        response = llm_client.chat.completions.create(
            model=model,
            max_tokens=128,
            user=session_id,
            messages=message_history,
            functions=functions,
            function_call="auto",
        )
    except:
        response = llm_client.chat.completions.create(
            model=model,
            max_tokens=128,
            user=session_id,
            messages=message_history,
            functions=functions,
            function_call="auto",
        )

    response_message = response.choices[0].message
    print("The response message is:", response_message)
    if response_message.function_call:
        available_functions = {
            "topic_discussed": campaign_discussed,
        }
        function_name = response_message.function_call.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message.function_call.arguments)
        function_response = function_to_call(function_args)
        if function_response is not None:
            msg_hist = [{"role": "system",
                         "content": " You are Yobo at Martello on Brock who takes input the response and answers it improving the grammar of the response"},
                        {"role": "user", "content": str(function_response)}]
            second_response = llm_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=256,
                messages=msg_hist),
            answer = second_response[0].choices[0].message.content.split("\n")[0]
            return {"answer": answer}
        return {"answer": answer}
    return {"answer": answer}


def campaign_discussed(info, context=None):
    print(info)
    global message_history
    global campaign1_status, campaign2_status
    campaign_check = info.get("campaign", False)

    if not campaign1_status and campaign_check:
        campaign1_status = True
        context = message_history[-1]['content']
        print(context)
        message_history.pop()
        return {"role": "assistant",
                "content": context + " There's a larger Martello Alley on Wellington Street, just a 2-minute walk from here. Do you want directions to get there"}
    if not campaign2_status and campaign1_status and campaign_check:
        campaign2_status = True
        context = message_history[-1]['content']
        message_history.pop()
        return {
            "role": "assistant",
            "content": f"{context} Also, don't forget to join our vibrant community on Instagram! Follow us @martelloalley for the latest updates, exclusive content, and a behind-the-scenes look at Martello Alley."}


def predict(input, session_id):
    global message_history, system_message, campaign1_status, campaign2_status
    message_history = system_message
    message_history.append({"role": "user", "content": f"{input}"})
    response = llm_client.chat.completions.create(
        model=model,
        max_tokens=128,
        user=session_id,
        messages=message_history,
    )
    message_history.pop()
    answer = response.choices[0].message.content
    message_history.append({'role': 'user', 'content': answer})

    if not campaign1_status or not campaign2_status:
        # answer = campain_function_call(answer)
        message_history.append({'role': 'user', 'content': answer})
        print("Checking Answer")
        message_history.append({"role": "user", "content": f"{input}"})
        message_history.append({"role": "assistant", "content": answer})
        return {"answer": answer}
    msg_hist = [{"role": "system",
                 "content": " You are Yobo at Martello on Brock who takes input the response and answers it by  improving the grammar of the response"}]
    msg_hist.append({"role": "assistant", "content": answer + " Should I tell you more"})
    second_response = llm_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        max_tokens=256,
        messages=msg_hist),
    answer = second_response[0].choices[0].message.content.split("\n")[0]
    print(answer)
    message_history.append({"role": "user", "content": f"{input}"})
    message_history.append({"role": "assistant", "content": answer})
    return {"answer": answer}


if __name__ == '__main__':
    while True:
        line = input()
        print(predict(line, "asda3423"))
        print(campaign1_status, campaign2_status)




