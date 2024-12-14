import os
import boto3
import pandas as pd
from prompt_utils import *
from database_utils import execute_sql
from bedrock_utils import *
from utils import *
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

    
class SqlState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    user_input: str
    num_sql_attempt: int
    use_streamlit_viz: bool
    if_sql_valid: bool
    context: str
    sql_query: str
    feedback: str
    error: str
    data: pd.DataFrame
    if_viz_success: bool
    viz_code: str
    response: str
    prompt_callback: object
    sql_query_callback: object
    query_result_callback: object
    python_prompt_callback: object
    python_code_callback: object
#    response: Annotated[list, add_messages]
    
def create_sql_graph():
    graph_builder = StateGraph(SqlState)
    
    def get_context(state: SqlState):
        # When context is already extracted to file, read from file.
        # If not, extrac context.
        context_file_path = "db_schema.txt"
        if os.path.exists(context_file_path):
            with open(context_file_path, "r") as f:
                db_schema = f.read()
        else:            
            schemas_dict = get_all_table_schema()
            db_schema = "\n\n".join(schemas_dict)
            
            with open(context_file_path, "w") as f:
                f.write(db_schema)
        return {
            "context": db_schema
        }
    
    def run_query_no_feedback_wrapper(state: SqlState):
        print("Running txt2sql...")
        if_passed, response, sql_query, current_attempt = run_query_no_feedback(question = state["user_input"], 
                                                                                db_schema = state["context"],
                                                                                prompt_callback = state['prompt_callback'],
                                                                                temperature= 0.2
                                                                               )
        
        # show the sql query in the backend processes window
        state['sql_query_callback'](sql_query)
        
        update = {
            "num_sql_attempt": current_attempt,
            "if_passed": if_passed,
            "sql_query": sql_query,
            "feedback": "",
        }
        
        if if_passed:
            update['data'] = response
            state['query_result_callback'](response)
        else:
            update['error'] = response['Error']

        return update
    
    def run_query_with_feedback_wrapper(state: SqlState):
        
        if_passed, current_feedback, response, sql_query, current_attempt = run_query_with_feedback(user_query = state["user_input"], 
                                                                                                    prev_feedback = state["feedback"],
                                                                                                    prev_sql_query = state["sql_query"], 
                                                                                                    prev_response = {"Error": state['error']}, 
                                                                                                    num_attempt = state["num_sql_attempt"], 
                                                                                                    db_schema= state["context"])
        update = {
            "num_sql_attempt": current_attempt,
            "if_passed": if_passed,
            "sql_query": sql_query,
            "feedback": current_feedback,
        }
        
        if if_passed:
            update['data'] = response
        else:
            update['error'] = response['Error']

        return update
        
    def check_for_valid_sql(state: SqlState):
        max_attempts = 10
        if state['if_passed']:
            return 'valid'
        elif state['num_sql_attempt'] == max_attempts:
            return 'max_attempt_reached'
        else:
            return 'not_valid'
        
    def generate_viz_wrapper(state: SqlState):
        
        if "use_streamlit_viz" not in state:
            use_streamlit = False
        else:
            use_streamlit = state['use_streamlit_viz']
        
        if_viz_success, viz_code = generate_viz(sql_query = state['sql_query'], use_streamlit=use_streamlit, prompt_callback=state['python_prompt_callback'])
        
        state['python_code_callback'](viz_code)
        
        return {"if_viz_success": if_viz_success, "viz_code":viz_code}
    
    
    def generate_response(state: SqlState):
        
        prompt_template = """Generate a natural language response to the <quesiton> below using the <data_table>.
        
<data_table>
{data_table}
</data_table>

<question>
{question}
</question>
        """
        prompt = prompt_template.format(question=state['user_input'], data_table=state['data'].to_string())
        response = invoke_model(prompt, SONNET35_MODEL_ID)
        
        return {"response" : response}
        
    
    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("get_context", get_context)
    graph_builder.add_node("txt_to_sql", run_query_no_feedback_wrapper)
    graph_builder.add_node("fix_sql", run_query_with_feedback_wrapper)
    graph_builder.add_node("sql_to_viz", generate_viz_wrapper)
    graph_builder.add_node("generate_response", generate_response)
    
    graph_builder.add_edge(START, "get_context")
    graph_builder.add_edge("get_context", "txt_to_sql")
    graph_builder.add_conditional_edges('txt_to_sql', check_for_valid_sql, {
        "valid" : "sql_to_viz", 
        "not_valid" : "fix_sql"
    })
    
    
    
    graph_builder.add_conditional_edges('fix_sql', check_for_valid_sql, {
        "valid" : "sql_to_viz", 
        "not_valid" : "fix_sql",
        "max_attempt_reached": END
    })
    graph_builder.add_edge("sql_to_viz", "generate_response")
    graph_builder.add_edge("generate_response", END)
    
    graph = graph_builder.compile()
    
    return graph