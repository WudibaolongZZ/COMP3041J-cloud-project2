# data_loader.py
import os
from dotenv import load_dotenv

import oss2
import time

load_dotenv()


# 【防坑神器】：强制告诉 Python，直接连接阿里云，不要走电脑上的 VPN/代理软件
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = '*'

def download_dataset():
    # 填入你刚才保存的 AK 和 SK
    access_key_id = os.getenv("ALIBABA_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_ACCESS_KEY_SECRET")
    
    # 授权
    auth = oss2.Auth(access_key_id, access_key_secret)
    
    # 填写你的 Bucket 所在的 Endpoint
    # 注意：如果后续你的 ECS 和 OSS 在同一个地域（如都是杭州），这里可以填内网 endpoint，例如：oss-cn-hangzhou-internal.aliyuncs.com，速度极快且免流量费！
    # endpoint = 'http://oss-cn-hangzhou.aliyuncs.com' 
    endpoint = 'http://oss-cn-hangzhou-internal.aliyuncs.com' 
    bucket_name = 'miniproject2-group-03'
    
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    
    local_file_name = 'full_data.csv' # 下载到云服务器上的文件名
    oss_file_name = 'Comp3041J MiniProject 2 Dataset.csv' # 你之前传到 OSS 上的文件名
    
    print("Start downloading dataset from Alibaba Cloud OSS...")
    start_time = time.time()
    
    # 执行下载
    bucket.get_object_to_file(oss_file_name, local_file_name)
    
    print(f"Download complete! Time cost: {time.time() - start_time:.2f} seconds.")

if __name__ == '__main__':
    download_dataset()