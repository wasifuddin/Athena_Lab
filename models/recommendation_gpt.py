from openai import OpenAI

import json
from db_reader import gallery_reader as sqr
import sys
import path

dir = path.Path(__file__).abspath()
sys.path.append(dir.parent.parent)
api_key = "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"

model = "ft:gpt-3.5-turbo-1106:megamind-tech:abzo-noyobo-v1:8fE9gubE"
model = "gpt-4-turbo-preview"
llm_client = OpenAI(api_key=api_key,)

file_path = "system_json/gallery.json"
def getSystemText(jsonFile):
    with open(jsonFile) as f: data = json.load(f)
    return data

system_message = getSystemText(file_path)

art_list = []
advertise_state = False
conversation_count = 0
promotion_text = "Want to know about our exhibitions and events we held in this art gallery then scan the QR code and subscribe to stay updated about the amazing art works here"

def predict(input, session_id):
    global message_history, system_message, art_list, advertise_state, conversation_count, promotion_text
    newSession = False
    if newSession:
        art_list = []
        advertise_state = False
        conversation_count = 0
    message_history = system_message
    message_history.append({"role": "user", "content": f"{input}"})


    message_history.append({'role': 'user', 'content': input})
    conversation_count += 1
    functions = [
        {
            "name": "get_art_description",
            "description": "Retrieve the description of the mentioned art and provide an art curator's perspective on the artwork",
            "parameters": {
                "type": "object",
                "properties": {
                    "art_name": {
                        "type": "string",
                        "description": "Name of the Art. For example: POULTRY NO. 5, RED ROSES",
                    }
                },
                "required": ["art_name"],
            },
        },
        {
            "name": "get_art_characteristics",
            "description": "Retrieve the name of the art and provide information about its composition, dimensions, and print type. For example: 1) Can you tell me the characteristics of this art? 2) What is the art made of? 3) Tell me about the properties of the art?",
            "parameters": {
                "type": "object",
                "properties": {
                    "art_name": {
                        "type": "string",
                        "description": "Name of the Art. For example: POULTRY NO. 5, RED ROSES",
                    }
                },
                "required": ["art_name"],
            },
        },

        {
            "name": "get_art_recommendation",
            "description": "Recommend and suggest various types of art to people based on particular size. Examples of user prompt 1) Tell me about some art 2) Show me some arts in 35 by 35 size. 3) Can you tell me about some of the arts",
            "parameters": {
                "type": "object",
                "properties": {
                    "art_name": {
                        "type": "string",
                        "description": "Name of the Art. For example: POULTRY NO. 5, RED ROSES",
                    },
                    "art_length_size": {
                        "type": "number",
                        "description": "Length of the Art or Painting in inches. For example: Can you show me art of size 25 by 35. Here 'art_length_size'= 25.",
                    },
                    "art_breadth_size": {
                        "type": "number",
                        "description": "Breadth of the Art or Paintng in inches. For example: Can you show me art of size 25 by 35. Here 'art_breadth_size'= 35.",
                    },

                    "art_price_range_start": {
                        "type": "integer",
                        "description": "Price of the Art or the Painting in CAD Canadian Dollors. For example: Can you show me art of price like 3000 to 9000. art_price_range_start = 3000",
                    },
                    "art_price_range_end": {
                        "type": "integer",
                        "description": "Price of the Art or the Painting in CAD Canadian Dollors. For example: Can you show me art of price like 3000 to 9000. art_price_range_end = 9000",
                    },
                    "art_price_search_type": {
                        "type": "string",
                        "enum": ["above", "below", "between", "equal"],
                        "description": "Search type of the price of the art. For example: Show me arts works from between price range 6000-7000. art_price_search_type = between. Show me arts under 10000. art_price_search_type= below. Show me arts over 10000. art_price_search_type= above",
                    },
                    "art_type": {
                        "type": "string",
                        "enum": ['aquatint', 'limestone', 'spray paint', 'linen', 'ceramic', 'woodblock', 'collage',
                                 'print', 'triptych', 'crayon', 'bronze', 'pastel', 'acrylic', 'brass', 'cotton',
                                 'graphite', 'encaustic', 'pearl', 'plaster', 'board', 'watercolour', 'mezzotint',
                                 'magazine', 'canvas', 'soapstone', 'japanese', 'mixed media', 'fine art', 'paper',
                                 'etching', 'antique', 'ink', 'resin', 'diptych', 'gesso', 'plexiglass', 'cement',
                                 'wax', 'quadriptych', 'liquitex', 'rag', 'photograph', 'silver leaf', 'panel',
                                 'monoprint', 'acid free', 'gold', 'glass', 'aluminum', 'pigment ink', 'wood', 'marble',
                                 'oil'],
                        "description": "Type of the material the Art is made of like water color, pastel color oil. For example: Can you show me art made up of oil on canvas",
                    },
                }
            },
        },
        {
            "name": "get_artist_recommendation",
            "description": "Recommend and suggest various Artist. For example: 1) Suggest me some artists? 2) Tell me about an artist here? 3) Name an artist at Abbozzo 4) Tell me about some art creators here",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "Name of the Artist",
                    }
                }
            },
        },

        {
            "name": "get_art_price",
            "description": "Retrieve the price of the Art or Painting. For example: What is the price of the art work? Tell me the price of this art?",
            "parameters": {
                "type": "object",
                "properties": {
                    "art_name": {
                        "type": "string",
                        "description": "Name of the Art. For example: POULTRY NO. 5, RED ROSES",
                    }
                }
            },
            "required": ["art_name"],

        },

        {
            "name": "get_artist_name",
            "description": "Retrieve the name of the Artist who made or drew or painted the Art or Painting",
            "parameters": {
                "type": "object",
                "properties": {
                    "art_name": {
                        "type": "string",
                        "description": "Name of the Art. For example: POULTRY NO. 5, RED ROSES",
                    }
                }
            },
            "required": ["art_name"],

        },

        {
            "name": "get_arts_of_artist",
            "description": "Suggest the Art, Paintings or the works using the Artist name from user question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "First Name of the Artist.For example: What are the arts or painting done by Alex? Result: artist_name = Alex",
                    }
                }
            },
            "required": ["artist_name"],

        },

    ]

    response = llm_client.chat.completions.create(
        model=model,
        max_tokens=128,
        user=session_id,
        messages=message_history,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    if response_message.function_call:
        available_functions = {
            "get_art_description": sqr.art_description,
            "get_art_recommendation": sqr.art_recommendation,
            "get_art_characteristics": sqr.art_characteristics,
            "get_arts_of_artist": sqr.artist_art_suggestion,
            "get_art_price": sqr.art_price,
            "get_artist_name": sqr.art_artist_name,
            "get_artist_recommendation": sqr.artist_recommendation

        }
        function_name = response_message.function_call.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(response_message.function_call.arguments)
        function_response = function_to_call(function_args)
        # print("The response")
        # print(function_response[0].get("Information_required"))
        #
        # print("Function Name: ", function_name)
        # print("Function To Call: ", function_to_call)
        # print("Function Args: ", function_args)
        # print("Function response: ", function_response)
        if function_response[0] is not None:
            print(function_response)
            # print("The function response is", function_response[0]["Art_Name"])
            # print("The function response is", function_response[0]["Artist_Name"])

            # Function response database response dict
            if function_response[0].get("command") is None:
                art_name = function_response[0]["Art_Name"]
                artist_name = function_response[0]["Artist_Name"]
                message_history.append(response_message)
                message_history.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": str(function_response[0])
                    }
                )
                second_response = llm_client.chat.completions.create(
                    # model="gpt-3.5-turbo-1106",
                    model=model,
                    max_tokens=256,
                    user=session_id,
                    messages=message_history),
                # get a new response from GPT where it can see the function response
                answer = second_response[0].choices[0].message.content.split("\n")[0]
                Art_Name = function_response[0]["Art_Name"]
                img_url = function_response[1]
                if not advertise_state:
                    if Art_Name not in art_list:
                        art_list.append(Art_Name)
                    else:
                        img_url = "https://d3edkvggxkcni7.cloudfront.net/Utensils/qrcode.png"
                        advertise_state = True
                        answer = answer + promotion_text
                        msg_hist = [{"role": "system",
                                     "content": " You are Athena who takes input the response and answers it in a different way by rephrasing the response and  improving the grammar of the response"},
                                    {"role": "assistant", "content": answer}]
                        second_response = llm_client.chat.completions.create(
                            model="gpt-3.5-turbo-1106",
                            max_tokens=256,
                            messages=msg_hist),
                        answer = second_response[0].choices[0].message.content.split("\n")[0]
                message_history.append({'role': 'assistant', 'content': answer})
                return {"answer": answer, "img_url": img_url, "art_name":art_name, "artist_name":artist_name}
            else:
                msg_hist = [{"role": "system",
                             "content": " You are Athena who takes input the response and answers it in a different way by rephrasing the response and  improving the grammar of the response"},
                            {"role": "assistant",
                             "content": "Sure I'm here to help. Do you have any specific art preferences of the art you want like price range, size or art made type. Such as water colour, ink painting etc"}]
                second_response = llm_client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    max_tokens=256,
                    messages=msg_hist),
                answer = second_response[0].choices[0].message.content.split("\n")[0]
                print(answer)
                message_history.append({"role": "assistant", "content": answer})
                return {"answer": answer}
        else:

            second_response = llm_client.chat.completions.create(
                model=model,
                max_tokens=256,
                user=session_id,
                messages=message_history,
            )  # get a new response from GPT where it can see the function response
            img_url = None
            answer = second_response[0].choices[0].message.content.split("\n")[0]
            if conversation_count > 1 and not advertise_state:
                img_url = "https://d3edkvggxkcni7.cloudfront.net/Utensils/qrcode.png"
                answer = answer + promotion_text
                msg_hist = [{"role": "system", "content": " You are Athena who takes input the response and answers it in a different way by rephrasing the response and  improving the grammar of the response"}]
                msg_hist.append({"role": "assistant", "content": answer})
                second_response = llm_client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    max_tokens=256,
                    messages=msg_hist),
                answer = second_response[0].choices[0].message.content.split("\n")[0]
                advertise_state = True
            message_history.append({'role': 'assistant', 'content': answer})
            return {"answer": answer, "img_url": img_url, "art_name":"Scan Me"}

    else:
        img_url = None
        answer = response.choices[0].message.content.split("\n")[0]
        if conversation_count > 1 and not advertise_state:
            img_url = "https://d3edkvggxkcni7.cloudfront.net/Utensils/qrcode.png"
            answer = answer + promotion_text
            msg_hist = [{"role": "system", "content": " You are Athena who takes input the response and answers it in a different way by rephrasing the response and  improving the grammar of the response"}]
            msg_hist.append({"role": "assistant", "content": answer})
            second_response = llm_client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                max_tokens=256,
                messages=msg_hist),
            answer = second_response[0].choices[0].message.content.split("\n")[0]
            advertise_state = True
        message_history.append({'role': 'assistant', 'content': answer})
        return {"answer": answer, "img_url": img_url}


if __name__ == '__main__':
    while True:
        line = input()
        print(predict(line, "asda3423"))

