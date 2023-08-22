import streamlit as st
import openai
import os
from dotenv import load_dotenv
from prompts import prompts
load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

st.title("Use AI to help write your essay!")

# Load available standards
standards = list(prompts.keys())

# Let users select a standard from the sidebar
selected_standard = st.sidebar.selectbox("Choose a system prompt (optional)", standards)

# Load the selected system prompt
system_prompt = prompts[selected_standard]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for message in st.session_state["messages"]:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Set word limit
word_limit = st.sidebar.slider("Set word limit", 100, 2000, 1000)

# initialize model
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"

# Adding the temperature slider
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
st.sidebar.text(f"Current Temperature: {temperature}")

# user input
if user_prompt := st.chat_input("Start by typing your essay prompt"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # generate responses
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        if st.session_state.messages:
            for response in openai.ChatCompletion.create(
                model=st.session_state.model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=temperature,
                stream=True,
            ):
                # Check if the word limit is reached
                if len((full_response + response.choices[0].delta.get("content", "")).split()) <= word_limit:
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            assistant_word_count = len(full_response.split())
            st.text(f"Word count: {assistant_word_count}")

            st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Edit and continue
        edit_option = st.text_area("Edit your essay here:", full_response)
        if st.button('Continue from edit'):
            st.session_state.messages.append({"role": "user", "content": edit_option})

        # Export options

        st.download_button(
            label="Download this response to txt file",
            data=full_response,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_name="essay.txt"
        )

