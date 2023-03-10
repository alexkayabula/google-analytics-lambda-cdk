import json
import sys
import logging
import psycopg2
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

secret_name = "mysecret"
region_name = "eu-west-1"
session = boto3.session.Session()

def database_connection():
    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/secrets-manager.html
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        client = session.client(service_name='secretsmanager',region_name=region_name,)
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
            text_secret_json_data = json.loads( text_secret_data )
            rds_host  =  text_secret_json_data["host"]
            db_name =  text_secret_json_data["dbname"]
            name =  text_secret_json_data["username"]
            password =  text_secret_json_data["password"]
    except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.error("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                logger.error("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                logger.error("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                logger.error("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                logger.error("An error occurred on service side:", e)
    try:
        text_secret_data = get_secret_value_response['SecretString']
        text_secret_json_data = json.loads( text_secret_data )
        rds_host  =  text_secret_json_data["host"]
        db_name =  text_secret_json_data["dbname"]
        name =  text_secret_json_data["username"]
        password =  text_secret_json_data["password"]
        connection = psycopg2.connect(host=rds_host, user=name, password=password, database=db_name)
    except psycopg2.DatabaseError as e:
        logger.error("ERROR: Unexpected error: Could not connect to PostgreSQL instance.")
        logger.error(e)
        sys.exit()
    else:
        logger.info("SUCCESS: Connection to RDS PostgreSQL instance succeeded.")
        return connection
