# -*- coding: utf-8 -*-

import mimetypes
from pathlib import Path
from botocore.exceptions import ClientError

""" Classes for S3 Buckets."""

class BucketManager:
    """Manager an S3 Bucket."""
    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = session.resource('s3')

    def all_buckets(self):
        """Get all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket):
        """Get all objects in an S3 bucket."""
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self, bucket_name):
        """ """
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration= {
                    'LocationConstraint' : self.session.region_name })
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket)
            else:
                raise error

        return s3_bucket


    def set_policy(self, bucket):
        """ """
        policy = """
        {
          "Version":"2012-10-17",
          "Statement":[{
          "Sid":"PublicReadGetObject",
          "Effect":"Allow",
          "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::%s/*"
              ]
            }
          ]
        }
        """ % bucket.name

        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)


    def configure_website(self, bucket):
        """ ."""
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
        }})


    @staticmethod
    def upload_file(bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        print(key)
        key = key.replace('\\', '/')
        print(key)
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            }
        )


    def sync(self, pathname, bucket_name):
        """ ."""
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
