import boto3
import json
import secrets

SERVER_NAME = 'dealeron'

STACK_NAME     = 'bitpolicy'
HOME_DIRECTORY = 'dealerons-sftp'
SECRET         = 'SFTP-Dealeron/'
USERNAME       = 'nomanikram'

s3_client     = boto3.client('s3')
cfn_client    = boto3.client('cloudformation')
iam_client    = boto3.client('iam')
account_id    = boto3.client('sts').get_caller_identity().get('Account')
secret_client = boto3.client('secretsmanager',region_name = 'us-east-1')

def dict_to_string(dict):
    return json.loads(json.dumps(dict, sort_keys=True, default=str))

def check_if_bucket_exists(bucket_name):
    s3_buckets = s3_client.list_buckets()["Buckets"]
    for bucket in s3_buckets:
        if bucket['Name'] == bucket_name:
            print(f"bucket named {bucket['Name']} already exists")
            return True
    return False

def check_if_stack_exists(stack):
    cfn_resp = cfn_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE'])
    cfn_stacks = cfn_resp['StackSummaries']

    for cfn_stack in cfn_stacks:
        if cfn_stack['StackName'] == stack:
            print(f"stack named {cfn_stack['StackName']} already exists")
            return True
    return False

def check_if_policy_exists(account_id,username):
    p_list = []
    policy_paginator = iam_client.get_paginator('list_policies')
    policy_arn = f"arn:aws:iam::{account_id}:policy/{username}-sftp-policy"
    for response in policy_paginator.paginate():
        for policy in response["Policies"]:
            if policy_arn == policy['Arn']:
                return True
    return False
    # pass
    # try:
    #     iam_client.get_policy(
    #         PolicyArn=f"arn:aws:iam::{account_id}:policy/{username}-sftp-policy"
    #     )
    #     return True
    # except Exception as e:
    #     return False

def fetch_policy(account_id,username):
    try:
        resp = iam_client.get_policy(
            PolicyArn=f"arn:aws:iam::{account_id}:policy/{username}-sftp-policy"
        )
        return {
           "name": resp["Policy"]["PolicyName"],
            "arn": resp["Policy"]["Arn"]
        }
    except Exception as e:
        print(f"policy do not exists {e}")

def create_policy(bucket_name,username):
    my_managed_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowListingOfUserFolder",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::{server_name}"
            ]
        },
        {
            "Sid": "HomeDirObjectAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObjectVersion",
                "s3:DeleteObject",
                "s3:GetObjectVersion"
            ],
            "Resource": "arn:aws:s3:::{server_name}/*"
        }
    ]
}
    my_managed_policy = json.dumps(my_managed_policy)
    my_managed_policy = my_managed_policy.replace('{server_name}',f'{bucket_name}')
    # try:
    policy = iam_client.create_policy(
        PolicyName=f'{username}-sftp-policy',
        PolicyDocument=my_managed_policy
    )
    print(f'policy: {username}-sftp-policy created')
    return policy['Policy']['Arn']
    # except:
    #     print(f'policy: {username}-sftp-policy exists')
    #     return f"arn:aws:iam::{account_id}:policy/{username}-sftp-policy"

def check_if_role_exists(username):
    roles = []
    # paginator = iam_client.get_paginator('list_roles')
    # paginator = iam_client.get_paginator('list_roles')
    RoleName=f"{username}-sftp-role"
    role_paginator = iam_client.get_paginator('list_roles')
    for response in role_paginator.paginate():
        response_role_names = [r.get('RoleName') for r in response['Roles']]
        for role in response_role_names:
            if role ==  RoleName:
                return True
    return False
    # try:
    #     iam_client.get_role(
    #         RoleName=f"{username}-sftp-role"
    #     )
    #     return True
    # except Exception as e:
    #     return False

def fetch_role(username):
        response = iam_client.get_role(
            RoleName=f"{username}-sftp-role"
        )
        return {
            "name": response["Role"]["RoleName"],
            "arn":  response["Role"]["Arn"]
        }
def create_role(username):
    assume_role_policy_document = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "transfer.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
    try:
        resp = iam_client.create_role(
            RoleName = f"{username}-sftp-role",
            AssumeRolePolicyDocument = assume_role_policy_document
        )
        print()
        return resp.Role.RoleName
    except:
        print('role already exists')
        return f'{username}-sftp-role'

def attach_policy_to_role(policy_arn,role_name):
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print("policy attached to role")

def check_if_secret_exists(username):
    SecretId=f'SFTP-{username}'
    secret_paginator = secret_client.get_paginator('list_secrets')
    for response in secret_paginator.paginate():
        for secret in  response["SecretList"]:
            if SecretId == secret["Name"]:
                return True
    return False


    # secrets = secret_client.list_secrets()
    # print(type(secrets))
    # return len(secrets)
    
    
    # try:
    #     secret_client.get_secret_value(
    #         SecretId=f'SFTP-{username}'
    #     )
    #     return True
    # except Exception as e:
    #     print(e)
    #     return False


def create_secret(username,bucket,role_name):
    password = secrets.token_urlsafe(12)
    secret_string = '{"HomeDirectory": "/{bucket}", "Password": "{password}","Role":"arn:aws:iam::{account_id}:role/{role_name}"}'\
        .replace('{bucket}',bucket)\
        .replace('{password}',password)\
        .replace('{account_id}',account_id)\
        .replace('{role_name}',role_name)
    try:
        secret_client.create_secret(
            Name=f'SFTP-{username}',
            SecretString=secret_string
        )
        print('secret created')
    except Exception as e:
        print(f'secret already present')