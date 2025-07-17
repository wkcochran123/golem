from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import deepspeed

app = Flask(__name__)

# Load tokenizer and model
model_id = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
base_model = AutoModelForCausalLM.from_pretrained(model_id)
ds_model = deepspeed.init_inference(base_model, mp_size=1)

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    data = request.get_json()
    messages = data.get("messages", [])
    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Missing or invalid 'messages' field"}), 400

    # Construct prompt from chat messages
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"{role}: {content}\n"

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    with torch.no_grad():
        output_ids = ds_model.generate(
            input_ids,
            max_new_tokens=50,
            do_sample=False
        )

    completion_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    response = {
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": completion_text
                },
                "finish_reason": "length"
            }
        ],
        "usage": {
            "prompt_tokens": len(input_ids[0]),
            "completion_tokens": len(output_ids[0]) - len(input_ids[0]),
            "total_tokens": len(output_ids[0])
        }
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5000)

