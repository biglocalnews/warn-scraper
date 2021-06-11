import requests as req
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

def send_query():

    endpoint = 'https://api.biglocalnews.org/graphql'
    # Standardize to the key name used by bln-etl
    # to set the stage to replace all of below with
    # from bln_etl.api import Project
    # project_id = os.environ['WARN_PROJECT_ID']
    # project = Project.get(project_id)
    # to_upload = ['/path/to/file1', '/path/to/file2'] # Generate by code to gather file list
    # project.upload_files(to_upload)
    # Details here: https://github.com/biglocalnews/bln-etl#api
    token = os.environ['BLN_API_KEY']
    project_id = os.environ['WARN_PROJECT_ID']
    path = os.environ['WARN_DATA_PATH']
    # TODO: Replace most of below with above-mentioned bln_etl code
    token_type = 'JWT'

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
    uploaded_files = []
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

        
        msg = "{} uploaded.".format(file)
        logger.info(msg)
        uploaded_files.append(msg)

    return uploaded_files


if __name__ == '__main__':
    send_query()
