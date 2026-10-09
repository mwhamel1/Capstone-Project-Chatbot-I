import json
import time
import streamlit as st
from groq import Groq, RateLimitError, APIError
from tools import AVAILABLE_TOOLS, TOOL_SCHEMAS
from retriever import general_faq, FAQ_TOOL_SCHEMA

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

ALL_TOOLS = AVAILABLE_TOOLS.copy()
ALL_TOOLS["general_faq"] = general_faq
ALL_SCHEMAS = TOOL_SCHEMAS + [FAQ_TOOL_SCHEMA]

SYSTEM_PROMPT = """You are a helpful assistant for a local bakery. 
You must explicitly refuse to take orders for custom event cakes or large corporate catering. 
If a user asks for a custom cake, state you only handle daily pastry pre-orders and direct them to call the bakery's main phone number to speak with a human decorator."""

def run_agent(messages, retries=2):
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    for attempt in range(retries + 1):
        try:
            for _ in range(5):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=messages,
                    tools=ALL_SCHEMAS,
                    tool_choice="auto",
                )
                message = response.choices[0].message

                if not message.tool_calls:
                    return message.content, None

                messages.append(message)
                
                for call in message.tool_calls:
                    name = call.function.name
                    
                    if name in ["place_order", "cancel_order"]:
                        return None, call

                    if name not in ALL_TOOLS:
                        result = f"Error: no tool named {name} exists."
                    else:
                        try:
                            args = json.loads(call.function.arguments)
                            result = ALL_TOOLS[name](**args)
                        except json.JSONDecodeError as error:
                            result = f"Error: malformed arguments. {error}"
                        except TypeError as error:
                            result = f"Error: wrong arguments for {name}. {error}"
                        except Exception as error:
                            result = f"Error: {name} failed. {error}"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(result),
                    })
                    
                    if "tool_log" in st.session_state:
                        st.session_state.tool_log.append(f"Called {name} with {call.function.arguments} -> {result}")

            return "I was not able to finish that request.", None

        except RateLimitError:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return "I am getting more requests than I can handle right now. Try again in a minute.", None
        except APIError:
            return "I cannot reach my language service at the moment. Please contact the help desk directly.", None