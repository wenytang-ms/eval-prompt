from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
import pathlib

def downloadApiSpecFiles(folder_path: str):
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=os.getenv('AZURE_STORAGE_ACCOUNT_URL'), credential=credential)
    # 下载文件
    container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    container_client = blob_service_client.get_container_client(container_name)
    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob.name)
        download_file_path = os.path.join(folder_path, blob.name)

        # 创建下载文件的目录（如果不存在）
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)

        # 下载 blob 到本地文件
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Blob {blob.name} downloaded to {download_file_path}")

if __name__ == "__main__":
    current_path = pathlib.Path(__file__).parent.resolve()
    api_func_folder = pathlib.Path(current_path, '../apisrc')
    downloadApiSpecFiles(api_func_folder)