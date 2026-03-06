print("✅ test_llm.py started")

from llm.llm_router import generate_response

print("✅ Imported LLM router")

prompt = "Explain Transformer architecture in simple terms."

print("✅ Sending prompt to LLM")

response = generate_response(prompt)

print("✅ Got response from LLM")
print("\n===== LLM RESPONSE =====\n")
print(response)
