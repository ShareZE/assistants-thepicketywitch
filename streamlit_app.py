import datetime
import time

import streamlit as st
from openai import OpenAI


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

assistant_id = st.secrets["ASSISTANT_ID"]
thread = client.beta.threads.create()
store_name = 'Pickety Witch'


st.set_page_config(page_title=f"Chat with the {store_name}-ecommerce-brand Assistant, powered by OpenAI",
                   page_icon="🦙",
                   layout="centered",
                   initial_sidebar_state="auto",
                   menu_items=None)
st.title(f"Chat with the `{store_name}-ecommerce-brand` Assistant")


if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": f"Ask me a question about the ecommerce, such as `analysis order volume by origin`."}
    ]

if prompt := st.chat_input("Your question"):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start = datetime.datetime.now()
            try:
                message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=prompt
                )
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id
                )
                is_continue_retrieve = True
                while is_continue_retrieve:
                    run = client.beta.threads.runs.retrieve(
                        thread_id=run.thread_id,
                        run_id=run.id
                    )
                    is_continue_retrieve = (run.status != 'completed')

                    if is_continue_retrieve:
                        time.sleep(10)
                    else:
                        messages = client.beta.threads.messages.list(
                            thread_id=thread.id
                        )
                        content = messages.data[0].content[0].text.value
            except Exception as e:
                pass
                content = 'Can you give me more information?'
            end = datetime.datetime.now()
            st.write(f'{content}`({(end - start).seconds}s)`')
            message = {"role": "assistant", "content": content}
            st.session_state.messages.append(message)  # Add response to message history
