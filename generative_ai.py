import requests

from transformers import AutoTokenizer
import json
import configparser
from helper import random_word

config = configparser.ConfigParser()
config.read("settings.ini")

API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
headers = {"Authorization": f"Bearer {config.get('ML', 'HF_TOKEN')}"}
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3-mini-4k-instruct")
tokenizer.chat_template = "{{ bos_token }}{% for message in messages %}\n{% if message['role'] == 'user' %}\n{{ '<|user|>\n' + message['content'] + '<|end|>' }}\n{% elif message['role'] == 'system' %}\n{{ '<|system|>\n' + message['content'] + '<|end|>' }}\n{% elif message['role'] == 'assistant' %}\n{{ '<|assistant|>\n'  + message['content'] + '<|end|>' }}\n{% endif %}\n{% if loop.last and add_generation_prompt %}\n{{ '<|assistant|>' }}\n{% endif %}\n{% endfor %}"
pre_prompt_path = config.get("ML", "GEN_PRE_PROMPT_PATH")


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def pipe(messages, **generation_args):
    return query(
        {
            "inputs": tokenizer.apply_chat_template(messages, tokenize=False),
            "parameters": {
                "return_full_text": False,
            },
        }
    )


def generate_title_and_description(products, export_json=False):
    # Generate title and description
    product_title_msg = ""
    for product in products:
        product_title_msg += f"Product title: '{product['title']}'\n"
    if product_title_msg[-1] == "\n":
        product_title_msg = product_title_msg[:-1]
    print(f"Prompt: {product_title_msg}")

    with open(pre_prompt_path) as user_file:
        json_string = user_file.read()
        messages = list(json.loads(json_string))
        messages.append({"role": "user", "content": f"{product_title_msg}"})

    output = pipe(messages)
    print(output)
    raw_response = output[0]["generated_text"].strip()
    index = 0
    rewritten = [row for row in raw_response.split("\n") if row != ""]
    new_products = []
    for product in products:
        split_values = rewritten[index].split(" D: ")

        if len(split_values) < 2:
            continue

        new_product = product.copy()
        new_product["title"] = split_values[0]
        new_product["description"] = split_values[1]
        new_products.append(new_product)
        index += 1

    if export_json:
        with open(f"products_{random_word(5)}.json", "w") as f:
            json.dump(new_products, f)
    return new_products
