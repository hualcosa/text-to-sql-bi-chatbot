import time
import json
import boto3
import sys
from botocore.config import Config
from botocore.exceptions import ClientError

BEDROCK_CONFIG = Config(
    region_name = 'us-west-2',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

BEDROCK_RT = boto3.client("bedrock-runtime", config = BEDROCK_CONFIG)
HAIKU_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
SONNET35_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
SONNET_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
LLAMA31_70B_MODEL_ID = "meta.llama3-1-70b-instruct-v1:0"


def invoke_claude(prompt, system, model_id, client, max_tokens_gen=512, temp=0.0):
    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens_gen,
        "temperature": temp,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
        "system": system
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except ClientError as e:
    # Check if the error is a ThrottlingException
        if e.response['Error']['Code'] == 'ThrottlingException':
            for i in range(3):
                try:
                    print("Invoking Model.", end="", flush=True)
                    for i in range(60):
                        if i % 2 == 0:
                            print(".", end="", flush=True)
                        time.sleep(1)
                    response = client.invoke_model(modelId=model_id, body=request)
                    break
                except:
                    pass

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        sys.exit()

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    return model_response["content"][0]["text"]


# Define the prompt for the model.
prompt = "Describe the purpose of a 'hello world' program in one line."


def invoke_llama(prompt, model_id, client, max_tokens_gen=512, temp=0.0):
    # Embed the prompt in Llama 3's instruction format.
    formatted_prompt = f"""
    <|begin_of_text|>
    <|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    # Format the request payload using the model's native structure.
    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": max_tokens_gen,
        "temperature": temp,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        sys.exit()

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["generation"]
    return response_text


# Use the native inference API to send a text message to Mistral.
def invoke_mistral(prompt, model_id, client, max_tokens_gen=512, temp=0.0):
    # Embed the prompt in Mistral's instruction format.
    formatted_prompt = f"<s>[INST] {prompt} [/INST]"

    # Format the request payload using the model's native structure.
    native_request = {
        "prompt": formatted_prompt,
        "max_tokens": max_tokens_gen,
        "temperature": temp,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        sys.exit()

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["outputs"][0]["text"]
    return response_text


def invoke_model(prompt, model_id, system="", max_tokens_gen=512, temp=0.0):
    
    client = BEDROCK_RT
    
    if 'claude' in model_id:
        return invoke_claude(prompt, system, model_id, client, max_tokens_gen=max_tokens_gen, temp=temp)
    elif 'llama3' in model_id:
        return invoke_llama(prompt, model_id, client, max_tokens_gen=max_tokens_gen)
    elif 'mistral' in model_id:
        return invoke_mistral(prompt, model_id, client, max_tokens_gen, temp)
    else:
        return "Model is not supported"
    

# # for testing
# if __name__ == "__main__":

#     prompt = "What is the weather like today?"

#     for i in range(100):
#         print(invoke_model(prompt, SONNET35_MODEL_ID))
