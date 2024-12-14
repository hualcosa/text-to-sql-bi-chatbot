from database_utils import execute_sql
from bedrock_utils import invoke_model, HAIKU_MODEL_ID, SONNET_MODEL_ID, SONNET35_MODEL_ID
import pandas as pd


def get_sql_query_prompt_no_context(usr_query):
    system_prompt = f"""
Transform the following natural language requests into valid SQL queries.

Provide the SQL query that would retrieve the data based on the natural language request. Give the SQL query in the following format.
```sql
```
    """

    usr_msg = f"""
    {usr_query}
    """
    return system_prompt, usr_msg


def parse_code(text, pattern1, pattern2):
    """
    """
    end = text.rfind(pattern2)
    start = text.find(pattern1) + len(pattern1)
    
    return text[start:end].strip()


def get_sql_query_with_llm(prompt, system_prompt, model_id=SONNET35_MODEL_ID, temperature=0.0):
    # Invoke LLM for input formatting
    
    content = invoke_model(prompt, SONNET35_MODEL_ID, system=system_prompt,temp=temperature)

    # content = get_claude_response_text(response)
    #print(content)
    sql_query = parse_code(content, "```sql", "```")
    return sql_query


def get_sql_query_prompt_generic_context(usr_query, db_schema):
    system_prompt = f"""Transform the following natural language <question> into valid SQL queries. Assume a database with the following database <schema> exists: 

<schema>
{db_schema}
<schema>


<hints>
- "_flag" columns have the following values ["Y", "N"]
- Use the column "season" from the "game_summary" table to filter for year. The season column only accepts 4 digit years.
- join with "game_summary" table to get the access to the "season" column.
- Use the "season" column from the "game_summary" table to filter, do not use "season_id" from the game table.
- If a column should be numerical but its varying character in the <schema>, cast it as a numerical column

Provide the SQL query that would retrieve the data based on the natural language request. Give the SQL query in the following format.
```sql
```
</hints>
    """

    usr_msg = f"""
<question>    
{usr_query}
</question>
    """
    return system_prompt, usr_msg


def get_table_schema(table_name):
    if_executed, ddl_schema = execute_sql(f'SHOW TABLE "aim330"."public"."{table_name}"')
    if if_executed:
        return ddl_schema["Show Table DDL statement"][0]
    else:
        return []

    
def get_all_table_schema():
    schemas = []
    if_executed, table_data = execute_sql('SHOW TABLES FROM SCHEMA "aim330"."public"')
    if if_executed:
        for table_name in table_data.table_name:
            schema = get_table_schema(table_name)
            schemas.append(f"{table_name} : {schema}")
    return schemas


def append_feedback(prev_feedback, prev_sql_query, sql_execute_error, num_attempt):
    current_feedback = f"""
    
    Attempt #{num_attempt} generated sql query as follows:
    {prev_sql_query}
    
    However, it gave the following error when executed:
    {sql_execute_error}   
    """
    
    feedback = prev_feedback + current_feedback    
    return feedback


def fix_sql_query_prompt(usr_query, db_schema, feedback=None):
    system_prompt = f"""Transform the following natural language requests into valid SQL queries. Assume a database with the following tables and columns exists: 
{db_schema}
    
Here is some feedback from previous attempts:
{feedback}

Fix the SQL query based on the feedback to answer the natural language request. Give the SQL query in the following format.
```sql
```
    """

    usr_msg = f"""
    {usr_query}
    """
    return system_prompt, usr_msg


def build_description_prompt(query_results):
    """
    """
    system_prompt = """You are a National Basketball Association (NBA) data table expert. Your goal is to describe the <table> below in a paragraph."""
    prompt = f"""<table>{query_results.to_string(index=False)}</table>"""

    return prompt, system_prompt


def build_python_gen_prompt(query_results, description, use_streamlit=False):
    """
    """

    system_prompt = """You are a python data visualization expert. 
    """

    if use_streamlit:
        prompt = f"""Given the discription of  table and the table itself, define a python function called "create_streamlit_chart" to visualize the data. 

<table>{query_results.to_string()}</table>

<description>{description}</description>

- Determine the best way to visualize the data
- If the table only has one column, use a streamlit table.
- Use the streamlit package for charts.
- Do not use python ranges to create time variables.
- Only create one graph that is most appropriate for the <table> data
- Use the actual data in the python function to create a pandas dataframe
- Make sure to include a title before the chart
- the function must return a streamlit chart or table
- Only return your python code in the following format
```python
```
        """
    else:
        prompt = f"""Given the discription of the table and the table itself write python code to visualize the data. 

<table>{query_results.to_string()}</table>

<description>{description}</description>

- Determine the best way to visualize the data
- If the table only has one column, use a plotly table.
- Use the plotly package for charts.
- Do not use python ranges to create time variables.
- Only return your python code in the format
- use the print function to show the plotly image
```python
```
        """

    return prompt, system_prompt


def build_python_gen_prompt_v1(query_results, use_streamlit=False):
    """
    """
    system_prompt = """You are a python data visualization expert and a National Basketball Association (NBA) data table expert."""
    if use_streamlit:
        prompt = f"""Your goal is to FIRST describe the <table> below in a paragraph in the given <description></description> tags. Then, use the discription in <description> tag and the table itself, define a python function called "create_streamlit_chart" to visualize the data.
<table>{query_results.to_string()}</table>
<description></description>
- Determine the best way to visualize the data
- If the table only has one column, use a streamlit table.
- Use the streamlit package for charts.
- Do not use python ranges to create time variables.
- Only create one graph that is most appropriate for the <table> data
- Use the actual data in the python function to create a pandas dataframe
- Make sure to include a title before the chart
- the function must return a streamlit chart or table
- Only return your python code in the following format
```python
```
        """
    else:
        prompt = f"""Your goal is to FIRST describe the <table> below in a paragraph in <description></description> tags. Then, use the discription in <description> tag and the table itself to write python code to visualize the data.
<table>{query_results.to_string()}</table>
<description></description>
- Determine the best way to visualize the data
- If the table only has one column, use a plotly table.
- Use the plotly package for charts.
- Do not use python ranges to create time variables.
- Only return your python code in the format
- use the print function to show the plotly image
```python
```
        """
    return prompt, system_prompt
