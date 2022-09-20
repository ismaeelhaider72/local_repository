from operator import truediv
import boto3
import os
import json
import secrets

s3_client     = boto3.client('s3')
cfn_client    = boto3.client('cloudformation',region_name='us-east-1')
iam_client    = boto3.client('iam',region_name='us-east-1')
account_id    = boto3.client('sts',region_name='us-east-1').get_caller_identity().get('Account')
secret_client = boto3.client('secretsmanager',region_name = 'us-east-1')


STACK_NAME     = os.environ['STACK_NAME']  #'bitpolicy'
SERVER         = "dealerons" 
HOME_DIRECTORY = os.environ['HOME_DIRECTORY'] #'dealerons-sftp'
USERNAME       = os.environ['username']


################################################################
############ stack existance check ################################
################################################################

def check_if_stack_exists(stack):
    cfn_resp   = cfn_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE'])
    cfn_stacks = cfn_resp['StackSummaries']

    for cfn_stack in cfn_stacks:
        if cfn_stack['StackName'] == stack:
            print(f"stack named {cfn_stack['StackName']} already exists")
            return True
    return False

################################################################
############ bucket existance check ############################
################################################################

def check_if_bucket_exists(bucket_name):
    s3_buckets = s3_client.list_buckets()["Buckets"]
    for bucket in s3_buckets:
        if bucket['Name'] == bucket_name:
            print(f"bucket named {bucket['Name']} already exists")
            return True
    return False


################################################################
################### create policy ##############################
################################################################

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


################################################################
################### create role ################################
################################################################

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
    
    resp = iam_client.create_role(
        RoleName = f"{username}-sftp-role",
        AssumeRolePolicyDocument = assume_role_policy_document
    )
    print()
    return resp['Role']['RoleName']

################################################################
############ attach policy to role #############################
################################################################

def attach_policy_to_role(policy_arn,role_name):
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        print("policy attached to role")

################################################################
################### create secrets #############################
################################################################

def create_secret(username,bucket,role_name,server):
    password = secrets.token_urlsafe(12)
    secret_string = '{"HomeDirectory": "/{bucket}", "Password": "{password}","Role":"arn:aws:iam::{account_id}:role/{role_name}"}'\
        .replace('{bucket}',bucket)\
        .replace('{password}',password)\
        .replace('{account_id}',account_id)\
        .replace('{role_name}',role_name)

    resp = secret_client.create_secret(
        Name=f'SFTP1-{server}/{username}',
        SecretString=secret_string
    )
    print('secret created')
    return resp

if __name__ == "__main__":

    policy = None
    role   = None


    # check cloudformationstack and bucket | policy role attachment secret | remove exception handling | 

    # print(check_if_policy_exists(account_id,"ismaeel"))

    # print(check_if_role_exists("sdf"))
        
    # print(check_if_secret_exists("ismaeel"))
    # 
    # print(create_policy("testingbucketismaeel","ismaeelhaider5"))  


    if check_if_stack_exists(STACK_NAME) and check_if_bucket_exists(HOME_DIRECTORY):
        print("stack or bucket found")
        policy_arn = create_policy(HOME_DIRECTORY,USERNAME)
        RoleName   = create_role(USERNAME)
        # print(policy_arn)
        # print(policy_arn)
        attach_policy_to_role(policy_arn,RoleName)
        create_secret(USERNAME,HOME_DIRECTORY,RoleName,server=SERVER.title())
    else:
        print("stack or bucket not found")    



"""
    if check_if_stack_exists("Transunion-SFTP"):
        print("stack exist")
        if check_if_bucket_exists("dealeron-sftp-1"):
            print("bucket exist")
        else:
            print("bucket not exist")    
    else:
        print("stack not exist")    
"""
    # if check_if_stack_exists() and check_if_bucket_exists():

    #     if check_if_policy_exists(account_id,USERNAME):
    #         fetch_policy(account_id,USERNAME)
    #     else:
    #         create_policy(HOME_DIRECTORY,USERNAME)

    #     if check_if_role_exists(USERNAME):
    #         role = fetch_role(USERNAME)
    #     else:
    #         role = create_role(USERNAME)

    #     attach_policy_to_role(policy["arn"],role["name"])

    #     if not check_if_secret_exists():
    #         create_secret(USERNAME,HOME_DIRECTORY,role["name"])






    # policy_arn = create_policy(HOME_DIRECTORY,USERNAME)
    # role_name   = create_role(USERNAME)

    # attach_policy_to_role(policy_arn,role_name)

    # create_secret(USERNAME, HOME_DIRECTORY, role_name )
    # print(check_if_policy_exists(account_id=account_id,username=USERNAME))
    # print(check_if_secret_exists(USERNAME))
    # print(fetch_policy(account_id,USERNAME))
