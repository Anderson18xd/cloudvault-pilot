import os
import hashlib
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class S3Service:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_client = boto3.client("s3", region_name=self.region)

    def upload_file_and_get_url(self, file_path: str, object_name: str) -> dict:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()

        try:
            self.s3_client.upload_file(file_path, self.bucket, object_name)
            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_name},
                ExpiresIn=3600
            )
            return {"object_name": object_name, "sha256": file_hash, "url": presigned_url}
        except ClientError as e:
            raise RuntimeError(f"Error en S3: {e}")
