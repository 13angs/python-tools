import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional, List, Dict, Any

class ObjectStorageUtil:
    """
    A utility class for interacting with object storage using boto3.
    Supports operations like uploading, downloading, listing, and deleting objects.
    """

    def __init__(
        self, 
        aws_access_key_id: str, 
        aws_secret_access_key: str, 
        endpoint_url: str
    ):
        """
        Initialize the object storage client.

        Args:
            aws_access_key_id (str): AWS access key ID
            aws_secret_access_key (str): AWS secret access key
            endpoint_url (str): Endpoint URL for the object storage service
        """
        try:
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url=endpoint_url
            )
            self._logger = logging.getLogger(self.__class__.__name__)
        except Exception as e:
            self._logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise

    def upload_file(
        self, 
        bucket_name: str, 
        file_path: str, 
        object_name: Optional[str] = None
    ) -> bool:
        """
        Upload a file to the specified bucket.

        Args:
            bucket_name (str): Name of the bucket
            file_path (str): Local path to the file to upload
            object_name (Optional[str]): Name of the object in the bucket. 
                                         If None, file_path is used.

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            if object_name is None:
                object_name = file_path

            self._s3_client.upload_file(file_path, bucket_name, object_name)
            self._logger.info(f"Successfully uploaded {file_path} to {bucket_name}/{object_name}")
            return True
        except ClientError as e:
            self._logger.error(f"Error uploading file: {str(e)}")
            return False

    def download_file(
        self, 
        bucket_name: str, 
        object_name: str, 
        file_path: str
    ) -> bool:
        """
        Download a file from the specified bucket.

        Args:
            bucket_name (str): Name of the bucket
            object_name (str): Name of the object to download
            file_path (str): Local path to save the downloaded file

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            self._s3_client.download_file(bucket_name, object_name, file_path)
            self._logger.info(f"Successfully downloaded {bucket_name}/{object_name} to {file_path}")
            return True
        except ClientError as e:
            self._logger.error(f"Error downloading file: {str(e)}")
            return False

    def list_objects(
        self, 
        bucket_name: str, 
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List objects in a bucket, optionally filtered by prefix.

        Args:
            bucket_name (str): Name of the bucket
            prefix (Optional[str]): Prefix to filter objects

        Returns:
            List[Dict[str, Any]]: List of object metadata
        """
        try:
            kwargs = {'Bucket': bucket_name}
            if prefix:
                kwargs['Prefix'] = prefix

            response = self._s3_client.list_objects_v2(**kwargs)
            objects = response.get('Contents', [])
            self._logger.info(f"Listed {len(objects)} objects in {bucket_name}")
            return objects
        except ClientError as e:
            self._logger.error(f"Error listing objects: {str(e)}")
            return []

    def delete_object(
        self, 
        bucket_name: str, 
        object_name: str
    ) -> bool:
        """
        Delete an object from a bucket.

        Args:
            bucket_name (str): Name of the bucket
            object_name (str): Name of the object to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            self._s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            self._logger.info(f"Successfully deleted {bucket_name}/{object_name}")
            return True
        except ClientError as e:
            self._logger.error(f"Error deleting object: {str(e)}")
            return False

    def create_bucket(
        self, 
        bucket_name: str
    ) -> bool:
        """
        Create a new bucket.

        Args:
            bucket_name (str): Name of the bucket to create

        Returns:
            bool: True if bucket creation successful, False otherwise
        """
        try:
            self._s3_client.create_bucket(Bucket=bucket_name)
            self._logger.info(f"Successfully created bucket {bucket_name}")
            return True
        except ClientError as e:
            self._logger.error(f"Error creating bucket: {str(e)}")
            return False
    
    def transform_object_list(self, objects):
        """
        Transform a list of object dictionaries into a list of lists.
        
        Args:
            objects (list): List of object dictionaries
        
        Returns:
            list: Transformed list of lists with formatted data
        """
        transformed_data = []
        
        for obj in objects:
            # Convert LastModified datetime to string
            last_modified = obj['LastModified']
            
            # Convert Size to human-readable format
            def human_readable_size(size_in_bytes):
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size_in_bytes < 1024.0:
                        return f"{size_in_bytes:.1f} {unit}"
                    size_in_bytes /= 1024.0
                return f"{size_in_bytes:.1f} TB"
            
            size = human_readable_size(obj['Size'])
            
            # Create a row for the list
            row = [
                obj['Key'],  # Object Name
                size,        # Size (human-readable)
                last_modified,  # Last Modified
                "Download Delete"  # Action column
            ]
            
            transformed_data.append(row)
        
        return transformed_data