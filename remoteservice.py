# -*- coding=utf-8
from baseservice import *

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import os

class RemoteService(BaseService):

    def __init__(self, context): 
            super().__init__(context)

    def service_listremote(self):
        id_file = os.getenv("HOME")+"/cos_user.txt"
        parts = open(id_file, "r").read().split("\n")
        secret_id = parts[0]
        secret_key = parts[1]
        region = 'ap-beijing'
        token = None 
        scheme = 'https' 
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
        client = CosS3Client(config)
        response = client.list_buckets()
        print("发现如下的Bucket：")
        for bucket in response['Buckets']['Bucket']:  
            print("\t",bucket['Name'])
        bucket_name = input("请输入要探查的bucket名称：").strip()
        if bucket_name !="":
            prefix = input("请输入查询的对象的前缀：")
            response = client.list_objects(Bucket=bucket_name,Prefix=prefix)
            results = response['Contents']
            count = 1
            for item in results:
                print("\t[%d]"%count, "Key=%s"%item['Key'], "\tTime=%s"%item['LastModified'], "\tSize=%s"%format(int(item['Size']), ','))
                count+=1
            
        '''

        {
            'ETag': '"9a4802d5c99dafe1c04da0a8e7e166bf"',
            'Last-Modified': 'Wed, 28 Oct 2014 20:30:00 GMT',
            'Cache-Control': 'max-age=1000000',
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': 'attachment; filename="filename.jpg"',
            'Content-Encoding': 'gzip',
            'Content-Language': 'zh-cn',
            'Content-Length': '16807',
            'Expires': 'Wed, 28 Oct 2019 20:30:00 GMT',
            'x-cos-meta-test': 'test',
            'x-cos-version-id': 'MTg0NDUxODMzMTMwMDM2Njc1ODA',
            'x-cos-request-id': 'NTg3NzQ3ZmVfYmRjMzVfMzE5N182NzczMQ=='
        }
        '''