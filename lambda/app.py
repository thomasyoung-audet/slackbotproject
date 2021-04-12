import json

def lambda_handler(event, context):
    message = '{} {}'.format(event['first_name'], event['last_name'])
    
    return {
        'statusCode': 200,
        'output': message
    }
