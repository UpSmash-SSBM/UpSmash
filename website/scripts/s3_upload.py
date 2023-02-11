from boto3 import session
from botocore.client import Config

ACCESS_ID = 'DO00A6YYE8BKHHC3BRJH'
SECRET_KEY = 'YFT9udAT446LiFkA7K6AlYkT+dfuYZBTu4yCZDMhhZc'

# Initiate session
session = session.Session()
client = session.client('s3',
                        region_name='nyc3',
                        endpoint_url='https://slippifiles.nyc3.digitaloceanspaces.com',
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)

# Upload a file to your Space
client.upload_file('Game_20230211T132140.slp')
