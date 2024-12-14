import sys

sys.path.append("/home/ec2-user/SageMaker/bi-chatbot-riv-builder/utilities/")

import streamlit as st
from datetime import datetime
import boto3
from botocore.config import Config
import json
import pandas as pd
import time
from langgraph_utils import create_sql_graph, SqlState
from utils import execute_python

st.set_page_config(layout="wide")
st.image("assets/aws-logo.png", width=200 )
st.title("AWS Re:Invent AIM330 Builder Session Demo") 
                
graph = create_sql_graph()




# Streamed response emulator
def stream_simulator(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)

if "messages" not in st.session_state:
    st.session_state['messages'] = []


col1, col2 = st.columns(2)

def show_prompt(text):
    with right_container.chat_message("ai"):
        st.markdown("## SQL Prompt")
        st.code(text)

        
def show_sql(sql):
    with right_container.chat_message("ai"):
        st.markdown("## SQL Query")
        st.code(sql, language="sql")
        
        
def show_query_results(df):
    with right_container.chat_message("ai"):
        st.markdown('## Query Results')
        st.write(df)
        
        
def show_python_prompt(text):
    with right_container.chat_message("ai"):
        st.markdown("## Python Visualization Prompt")
        st.code(text)
        
def show_python(python):
    with right_container.chat_message("ai"):
        st.markdown("## Python Visualization")
        st.code(python, language="python")


with col2:
    st.markdown("## Backend Processes")
    with st.container():
        global right_container
        right_container = st.container(height=600, border=True)

with col1:
    st.markdown("## BI Chatbot Assistant")
    with st.container():
        left_container = st.container(height=600, border=True)
    
        for message in st.session_state.messages:
            with left_container.chat_message(message[0]):
                st.markdown(message[1])
        
        # Accept user input
        if question := st.selectbox("Select Question", ["How many games are played per year?", "What team had the highest scoring average at home in 2019?"], index=None):#st.chat_input("Hello, how can I help?", key="bi-chatbot"):
            # Add user message to chat history
            st.session_state.messages.append(("human", question))

            with left_container.chat_message("human"):
                st.markdown(question)


            # Display assistant response in chat message container
            with left_container.chat_message("assistant"):

                with st.spinner("Working on it..."):
                    # invoke langgraph here 
                    # time.sleep(5)
                    response = graph.invoke(
                        SqlState(
                            user_input=question, 
                            num_sql_attempt=0, 
                            use_streamlit_viz=True, 
                            prompt_callback=show_prompt,
                            sql_query_callback=show_sql,
                            query_result_callback=show_query_results,
                            python_prompt_callback=show_python_prompt,
                            python_code_callback=show_python
                        )
                    )
                    st.write_stream(stream_simulator(response['response']))

                # st.code(response['viz_code'])
                # result = execute_python()

                    try:
                        exec(response['viz_code'])
                        exec("chart = create_streamlit_chart()")
                        # exec("st.write(chart)")
                        # exec('st.session_state.messages.append(("assistant", chart))')

                    except Exception as e:
                        print("error displaying chart:", e)

            # check for response and return, there was an error with calculating if response is not there
            # show the SQL for debugging purposes
            st.session_state.messages.append(("assistant", response['response']))
            # st.session_state.messages.append(("assistant", response))

