from prompt_utils import *
from database_utils import execute_sql
from bedrock_utils import *


def run_query_no_feedback(question, db_schema, prompt_callback, temperature=0.0):
    usr_query = question
    num_attempt = 1
    system_prompt, usr_msg = get_sql_query_prompt_generic_context(usr_query, db_schema)
    
    if prompt_callback is not None:
        prompt_callback(system_prompt + "\n\n" + usr_msg)
    
    sql_query = get_sql_query_with_llm(usr_msg, system_prompt, model_id=SONNET35_MODEL_ID, temperature=temperature)
    
    if_passed, response = execute_sql(sql_query)
    # This is used for logging
    # print("="*10)
    # print("Attempt #:", num_attempt)
    # print(sql_query)
    if not if_passed:
        print(response['Error'])
    # else:
        # print(response)
    return if_passed, response, sql_query, num_attempt


def run_query_with_feedback(user_query, prev_feedback, prev_sql_query, prev_response, num_attempt, db_schema):
    
    current_feedback = append_feedback(prev_feedback, prev_sql_query, prev_response['Error'], num_attempt)
    system_prompt, usr_msg = fix_sql_query_prompt(user_query, db_schema, current_feedback)
    sql_query = get_sql_query_with_llm(usr_msg, system_prompt, model_id=SONNET35_MODEL_ID)
    if_passed, response = execute_sql(sql_query)
    num_attempt = num_attempt + 1
    
    # print("="*10)
    # print("Attempt #:", num_attempt)
    # print(sql_query)
    if not if_passed:
        print(response['Error'])
    # else:
        # print(response)
        
    return if_passed, current_feedback, response, sql_query, num_attempt


def execute_python(code):
    try:
        exec(code)
        return True
    except Exception as e:
        return e


def generate_viz(sql_query, use_streamlit=False, prompt_callback=None):
    """
    """

    success, query_results = execute_sql(sql_query)

    prompt, system_prompt = build_description_prompt(query_results)
    description = invoke_model(prompt, SONNET35_MODEL_ID,system=system_prompt, max_tokens_gen=4096)

    prompt, system_prompt = build_python_gen_prompt(query_results, description, use_streamlit=use_streamlit)
    
    if prompt_callback is not None:
        prompt_callback(system_prompt + "\n\n" + prompt)
    
    response = invoke_model(prompt, SONNET35_MODEL_ID,system=system_prompt, max_tokens_gen=4096, temp=0.2)
    python_code = parse_code(response, "```python", "```")
    
    if use_streamlit:
        return True, python_code
    
    success = execute_python(python_code)
    
    return success, python_code


def generate_viz_v1(sql_query, use_streamlit=False, prompt_callback=None, execute=False):
    """
    """
    success, query_results = execute_sql(sql_query)
    prompt, system_prompt = build_python_gen_prompt_v1(query_results, use_streamlit=use_streamlit)
    
    if prompt_callback is not None:
        prompt_callback(system_prompt + "\n\n" + prompt)
    
    response = invoke_model(prompt, SONNET35_MODEL_ID, system=system_prompt, max_tokens_gen=4096, temp=0.2)
    python_code = parse_code(response, "```python", "```")
    
    if use_streamlit:
        return True, python_code
    
    if execute:
        success = execute_python(python_code)
    
    return success, python_code
