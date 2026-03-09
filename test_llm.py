print("âœ… test_llm.py started")

from backend.llm.llm_router import generate_response

print("âœ… Imported LLM router")

prompt = "Explain Transformer architecture in simple terms."

print("âœ… Sending prompt to LLM")

response = generate_response(prompt)

print("âœ… Got response from LLM")
print("\n===== LLM RESPONSE =====\n")
print(response)

