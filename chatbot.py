import streamlit as st
import openai
import os
from dotenv import load_dotenv
from prompts import prompts
load_dotenv()

#import keys
openai.api_key = os.environ["OPENAI_API_KEY"]

# Display company logo at the top
st.image("assets\\Scholarlyst_Logo-transformed.png")

st.title("Hey, let me assist you on crafting your essay.")

# Load available standards
standards = list(prompts.keys())

# Sidebar organization
with st.sidebar:
    st.header("Model Controls")
    # Let users select a standard from the sidebar
    selected_standard = st.selectbox("Choose a system prompt (optional)", standards)

    # Toggle to edit the system prompt
    edit_prompt = st.checkbox("Edit system prompt")

    if edit_prompt:
        # Option to change the system_prompt for testing
        system_prompt = st.text_area("Change system prompt (for testing)", value=prompts[selected_standard])
        # Save the edited system prompt in session state
        st.session_state['edited_system_prompt'] = system_prompt
        if st.button('Confirm system prompt edit & restart chat'):
            # Clear the conversation
            st.session_state.messages = []
            # Restart the conversation with the edited system prompt
            st.session_state.messages.append({"role": "system", "content": system_prompt})
    else:
        # Load the edited system prompt if it exists in session state
        system_prompt = st.session_state.get('edited_system_prompt', prompts[selected_standard])

    # Set word limit
    word_limit = st.slider("Set word limit", 100, 2000, 1000)

    # Model toggle option
    models = ["gpt-3.5-turbo", "gpt-4"]
    if "model" not in st.session_state:
        st.session_state.model = models[0]
    try:
        st.session_state.model = st.selectbox("Choose a model", models, index=models.index(st.session_state.model))
    except openai.error.InvalidRequestError:
        st.error("The model you selected does not exist or you do not have access to it. Please select a different model.")

    # Adding the temperature slider
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    st.text(f"Current Temperature: {temperature}")

    # Reset Button
    if st.button('Reset Chat'):
        st.session_state.clear()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Auto greet the user when they first load the website
if "greeted" not in st.session_state:
    st.session_state.greeted = True
    st.session_state.messages.append({"role": "assistant", "content": "Hello, I'm here to help you write a winning scholarship essay. I will be guiding you through the process of crafting a compelling essay that will impress the scholarship committee. Are you ready to get started?"})

for message in st.session_state["messages"]:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# user input
if user_prompt := st.chat_input("Send a message"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # generate responses
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        

        if st.session_state.messages:
            try:
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
            except openai.error.InvalidRequestError:
                st.error("The model you selected you do not have access to. Please select a different model.")

            message_placeholder.markdown(full_response)

            assistant_word_count = len(full_response.split())
            if assistant_word_count > 500:
                st.text(f"Word count: {assistant_word_count}")

            st.session_state.messages.append({"role": "assistant", "content": full_response})



        # Export options
        if assistant_word_count > 500:
            st.download_button(
                label="Download this response to txt file",
                data=full_response,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                file_name="essay.txt"
            )





