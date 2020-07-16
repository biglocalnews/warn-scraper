#!/usr/bin/python
import requests as req
from pathlib import Path
import os

def send_query():

    endpoint = 'https://api.biglocalnews.org/graphql'
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODMyODEyMTcsIm5iZiI6MTU4MzI4MTIxNywianRpIjoiNjYyOGE4NTgtMDMwOC00M2E3LWFiZmYtYTA1NWZiNjE1ZmM1IiwiaWRlbnRpdHkiOiJkNjE2MjU3YS02OThhLTRlNjEtODcyZi02MzNmNTkxOWNkMzgiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.S5Y-S9WN-z7VCTsMV4u_Kyw00gFQXfBi9FA6-mEIF3k'
    token_type = 'JWT'
    # Test_id = "UHJvamVjdDo5ZmE5NDNhOC0xNzljLTQwYTItYmY5My1lMmMyMWQwNzUzYmY="
    # warn_id = "UHJvamVjdDpiZGM5NmU1MS1kMzBhLTRlYTctODY4Yi04ZGI4N2RjMzQ1ODI="

    path = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/'

    def gql(query, vars={}):
        res = req.post(
            endpoint,
            json={'query': query, 'variables': vars },
            headers={'Authorization': f'{token_type} {token}'}
        ) 
        res.raise_for_status() # raises error if not HTTP response 200 (OK)
        return res.json()

    def upload(src_file_path, uri):
        with open(src_file_path, 'rb') as file:
            headers = {'content-type': 'application/octet-stream', 'host': 'storage.googleapis.com'}
            res = req.put(uri, data=file, headers=headers)
        res.raise_for_status()

    uploadFile = '''
    mutation UploadFile(
    $input: FileURIInput!
    ) {
        createFileUploadUri(input: $input) {
            ok{
            uri
            }
        }
    }
    '''

    dirs = os.listdir(path)
    for file in dirs:

        if file == '.DS_Store':
            continue
        if file == '.ipynb_checkpoints':
            continue

        input = { 
        "fileName": file,
        "projectId": "UHJvamVjdDpiZGM5NmU1MS1kMzBhLTRlYTctODY4Yi04ZGI4N2RjMzQ1ODI="
    }
        res = gql(uploadFile, vars={'input': input})
        upload_uri = res["data"]["createFileUploadUri"]["ok"]["uri"]
        upload_uri
        upload(f'{path}/{file}', upload_uri)
        
        print(input)
        print('uploaded')


if __name__ == '__main__':
    send_query()