import boto3
import pandas as pd
import json

redshift_client = boto3.client('redshift-data', region_name="us-west-2")
secrets_manager = boto3.client('secretsmanager', region_name="us-west-2")

with open("/home/ec2-user/SageMaker/bi-chatbot-riv-builder/config/config.json", 'r') as config_file:
    config = json.load(config_file)

    # Redshift cluster details
    CLUSTER_IDENTIFIER = config['REDSHIFT_CLUSTER_IDENTIFIER']
    DATABASE = config['REDSHIFT_DATABASE']
    SECRET_ARN = config['REDSHIFT_SECRET_ARN']
    
    
def get_secret():
    try:
        get_secret_value_response = secrets_manager.get_secret_value(SecretId=SECRET_ARN)
    except Exception as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            raise ValueError("Secret not found in SecretString")

secret = get_secret()
USERNAME = secret['username']

def get_values(record):
    values = []
    for val in record:
        for key in val.keys():
            values.append(val[key])
            
    return values


def execute_sql(query, show_progress=True):
    response = redshift_client.execute_statement(
            ClusterIdentifier=CLUSTER_IDENTIFIER,
            Database=DATABASE,
            DbUser=USERNAME,
            Sql=query,
        )
    
    id_ = response['Id']
    
    
    # check for
    status = "SUBMITTED"
    iterations = 0
    if show_progress:
        print("EXECUTING.", end="")
    while status != "FINISHED":
        response = redshift_client.describe_statement(Id=id_)
        status = response['Status']
        iterations += 1
        
        if status == 'FAILED':
            # print("")
            # print(response['Error'])
            return False, response
        
        if show_progress and iterations % 10 == 0:
            print(".", end="")
        
    data = redshift_client.get_statement_result(Id=id_)
    
    column_names = [col['name'] for col in data['ColumnMetadata']]
    records = [get_values(rec) for rec in data['Records']]
    
    df = pd.DataFrame.from_records(records, columns=column_names)
    
    if show_progress:
        print("")
    
    return True, df
