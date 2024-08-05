
import time
import json
from bc import *
queue_key = 'tx/3.json'
def check_file_existence(bucket_name, queue_key):
    try:
        # Use head_object to check if the file exists
        s3.head_object(Bucket=bucket_name, Key=queue_key)
        return True
    except Exception as e:
        # If the file does not exist, an exception will be raised
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise

        
def check_for_new_files(bucket_name, prefix, oldest_object):

    # List objects in the specified directory of the S3 bucket
    oldest_object[0]=check_file_existence(bucket_name,queue_key)
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    objects = [obj for obj in response.get('Contents', []) if (obj['Key'] != "tx/")&(obj['Key'] != queue_key)]
    if not objects:
        oldest_object[0]=False
        return oldest_object
    else:
        oldest_obj = min(objects, key=lambda x: x['LastModified'])
        if oldest_obj:
            key = oldest_obj['Key']
            response = s3.get_object(Bucket=bucket_name, Key=key)
            oldest_object[1]=response['Body'].read().decode()
            if key != "tx/" and oldest_object[0]!=False:
                s3.delete_object(Bucket=bucket_name, Key=key)
        oldest_object[2]=key
        return oldest_object

if __name__ == "__main__":
    chain = Blockchain()
    S3_DIRECTORY_PREFIX = 'tx/'  # Include trailing slash
    
    next_queue_key='tx/1.json'
    # Specify the interval (in seconds) for checking new files
    CHECK_INTERVAL = 60
    
    # Ensure the download directory exists
    
    oldest_object = [None,None,None,None]
    
    while True:
        chain = Blockchain()
        oldest_object = check_for_new_files(S3_BUCKET_NAME, S3_DIRECTORY_PREFIX, oldest_object)
        print(oldest_object)
        if oldest_object[0]==False:
            print("not time yet")
        else:
            s3.delete_object(Bucket=S3_BUCKET_NAME, Key=queue_key)
            block = json.loads(oldest_object[1], cls = BlockDecoder)
            a = chain.mining(block)
            if a != False:
                s3.upload_file("blocks.dat",S3_BUCKET_NAME, "blocks.dat")
                s3.put_object(Body="", Bucket=S3_BUCKET_NAME, Key=next_queue_key)
            else:
                json_data = json.dumps(block, cls=BlockEncoder)
                block_key = oldest_object[2]
                s3.put_object(Body=json_data, Bucket=S3_BUCKET_NAME, Key=block_key)
        time.sleep(CHECK_INTERVAL)

