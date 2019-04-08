# -*- coding: utf-8 -*-

"""Classes for S3 Bucket. """

import mimetypes
from pathlib import Path
from botocore.exceptions import ClientError
import boto3


class BucketManager:
    """Manage an S3 Bucket. """

    def __init__(self, session):
        """ Create a Bucket Manager Object. """
        self.session = session
        self.s3 = self.session.resource('s3')


    def all_buckets(self):
        """Get the interator for all the bickets."""
        return self.s3.buckets.all()


    def all_objects(self, bucket):
        """ Get an iterator of all the objects in bucket."""
        return self.s3.Bucket(bucket).objects.all()


    def init_bucket(self, bucket_name):
        """ Create new bucket or return the existing one by name"""
        s3_bucket = None
        try :
            s3_bucket = self.s3.create_bucket(
                Bucket = bucket_name
        #       CreateBucketConfiguration = {                      --Use this if you want to give more configuration to your bucket
        #               'LocationConstraint': self.session.region_name}     --Use this if you are using different region from 'us-east-1'
                )

        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)

            else:
                raise error

        return s3_bucket


    def set_policy(self, bucket):
        """ Set the Bucket policy to be readable by everyone."""
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
        """ this will configure details for the website."""

        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument' : {
                'Key':'error.html'
                    },
            'IndexDocument' : {
                'Suffix': 'index.html'
                    }
            })


    @staticmethod
    def upload_file(bucket, path, key):
        """Upload path to S3 bucket at key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/html'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType' : 'text/html'
            })

    def sync(self, pathname, bucket_name):
        """ Sync the pathname document with the S3 Bucket """
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()
        def handle_directory(target):
            for p in target.iterdir():

                if p.is_dir():
                    handle_directory(p)

                if p.is_file():
                    self.upload_file(bucket, str(p), str(p.relative_to(root)))

        handle_directory(root)
