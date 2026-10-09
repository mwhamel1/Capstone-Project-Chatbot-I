import streamlit as st
import json
from agent import run_agent
from tools import AVAILABLE_TOOLS
from retriever import general_faq

ALL_TOOLS = AVAILABLE_TOOLS.copy()
ALL_TOOLS["general_faq"] = general_faq

st.title("Local Bakery Pre-Order Assistant")
st.info("Disclosure: I am an AI software assistant here to help you check stock and reserve pastries.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_log" not in st.session_state:
    st.session_state.tool_log = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

for msg in st.session_state.messages:
    if isinstance(msg, dict):
        role = msg.get("role")
        content = msg.get("content")
        has_tools = False
    else:
        role = getattr(msg, "role", None)
        content = getattr(msg, "content", None)
        has_tools = bool(getattr(msg, "tool_calls", None))

    if role in ["user", "assistant"] and content and not has_tools and role != "system":
        with st.chat_message(role):
            st.write(content)

if st.session_state.pending_action:
    call = st.session_state.pending_action
    args = json.loads(call.function.arguments)
    st.warning(f"The assistant wants to {call.function.name}: {args}. Do you confirm?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm Action"):
            try:
                result = ALL_TOOLS[call.function.name](**args)
            except Exception as error:
                result = f"Tool failed: {error}"
            
            st.session_state.messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })
            st.session_state.tool_log.append(f"Confirmed {call.function.name} with {call.function.arguments} -> {result}")
            st.session_state.pending_action = None
            reply, _ = run_agent(st.session_state.messages)
            if reply:
                st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
            
    with col2:
        if st.button("Cancel Action"):
            st.session_state.messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": "User denied the confirmation."
            })
            st.session_state.tool_log.append(f"Denied {call.function.name} with {call.function.arguments}")
            st.session_state.pending_action = None
            reply, _ = run_agent(st.session_state.messages)
            if reply:
                st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

user_input = st.chat_input("Ask about our pastries or place an order...")

if user_input and not st.session_state.pending_action:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    reply, pending_call = run_agent(st.session_state.messages)
    
    if pending_call:
        st.session_state.pending_action = pending_call
        st.rerun()
    elif reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

st.sidebar.title("System Log")
for log_entry in st.session_state.tool_log:
    st.sidebar.text(log_entry)