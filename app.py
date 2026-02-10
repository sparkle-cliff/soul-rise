import os
import json
import urllib.request
import urllib.error

import streamlit as st

OPENROUTER_URL = "https://api.openrouter.ai/v1/chat/completions"
OPENROUTER_API_KEY = ""

def call_openrouter(messages, api_key, model="gpt-4o-mini"):
    payload = {
        "model": model,
        "messages": messages,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(OPENROUTER_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp_text = resp.read().decode("utf-8")
            resp_json = json.loads(resp_text)
            # Try common places for assistant content
            try:
                content = resp_json["choices"][0]["message"]["content"]
            except Exception:
                # fallback for variants
                try:
                    content = resp_json["choices"][0]["text"]
                except Exception:
                    content = str(resp_json)
            return content
    except urllib.error.HTTPError as e:
        try:
            err = e.read().decode()
        except Exception:
            err = str(e)
        return f"HTTPError: {e.code} - {err}"
    except Exception as e:
        return f"Error: {e}"


def main():
    st.title(" Chatbot ")
    api_key = OPENROUTER_API_KEY
    st.sidebar.header("Settings")
    #api_key = st.sidebar.text_input("OpenRouter API Key", type="password", value=os.environ.get("OPENROUTER_API_KEY", ""))
    model = st.sidebar.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)

    if not api_key:
        st.sidebar.warning("Set your OpenRouter API key here or set OPENROUTER_API_KEY env var.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:")
        submit = st.form_submit_button("Send")

    if submit and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        if not api_key:
            st.error("No API key provided.")
        else:
            with st.spinner("Waiting for response..."):
                assistant_reply = call_openrouter(st.session_state.messages, api_key, model=model)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    st.markdown("---")
    for msg in st.session_state.messages[1:]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Assistant:** {msg['content']}")
        else:
            st.markdown(f"**{msg['role'].title()}:** {msg['content']}")

    if st.button("Clear chat"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]


if __name__ == "__main__":
    main()

