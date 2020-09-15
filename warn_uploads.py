import requests as req
from pathlib import Path
import os

def send_query():

    endpoint = 'https://api.biglocalnews.org/graphql'
    token = os.environ['QUERY_TOKEN'] 
    token_type = 'JWT'
    project_id = os.environ['WARN_PROJECT_ID']
    path = os.environ['WARN_DATA_PATH']
    

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
        "projectId": project_id
    }
        res = gql(uploadFile, vars={'input': input})
        upload_uri = res["data"]["createFileUploadUri"]["ok"]["uri"]
        upload_uri
        upload(f'{path}/{file}', upload_uri)
        
        print(file, ' uploaded')


if __name__ == '__main__':
    send_query()