import json, tiktoken
from langchain_core.messages import BaseMessage

def count_tokens(text: str, model="gpt-4o-mini"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def count_all_messages_tokens(messages: list[BaseMessage], model="gpt-4o-mini"):
    enc = tiktoken.encoding_for_model(model)
    total_tokens = 0
    for m in messages:
        content = m.content if isinstance(m.content, str) else json.dumps(m.content, default=str)
        total_tokens += len(enc.encode(content))
    print(f"Total tokens in messages stack: {total_tokens}")
    return total_tokens