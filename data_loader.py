# data_loader.py
import os
from dotenv import load_dotenv

import oss2
import time

load_dotenv()


os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = '*'

def download_dataset():
    access_key_id = os.getenv("ALIBABA_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_ACCESS_KEY_SECRET")

    auth = oss2.Auth(access_key_id, access_key_secret)
    

    endpoint = 'http://oss-cn-hangzhou-internal.aliyuncs.com' 
    bucket_name = 'miniproject2-group-03'
    
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    
    local_file_name = 'full_data.csv'
    oss_file_name = 'Comp3041J MiniProject 2 Dataset.csv'
    
    print("Start downloading dataset from Alibaba Cloud OSS...")
    start_time = time.time()

    bucket.get_object_to_file(oss_file_name, local_file_name)
    
    print(f"Download complete! Time cost: {time.time() - start_time:.2f} seconds.")

if __name__ == '__main__':
    download_dataset()