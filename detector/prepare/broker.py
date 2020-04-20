import os
from azure.storage.blob import BlobServiceClient


class BlobBroker(object):
    
    def __init__(self, container='ackbarstorage'):
        self.container = container
        self.conn_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        self.blob_service_client = BlobServiceClient.from_connection_string(self.conn_str)
    
    def upload(self, fh, project, upload_id):
        path = '/'.join([project, str(upload_id)])
        blob_client = self.blob_service_client.get_blob_client(container=self.container,
                                                               blob=path)
        blob_client.upload_blob(fh)
        
    def download(self, project, upload_id):
        path = '/'.join([project, str(upload_id)])
        blob_client = self.blob_service_client.get_blob_client(container=self.container,
                                                               blob=path)
        return blob_client.download_blob().readall()