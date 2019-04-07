#!/usr/bin/python
# -*- coding: utf-8 -*-

""" WebApp deploys website with AWS.

This automates the deploying of websites to AWS.
- Confifure AWS s3 Buckets:
    - create them
    - Set themup for static website hosting
    - Deploy local files to themu
- Configure DNS with AWS Route53
- Configure Content Delivery Network and SSL with AWS CloudFront
"""
from pathlib import Path
import mimetypes

import boto3
from botocore.exceptions import ClientError
import click

session = boto3.Session(profile_name='shotty')
s3 = session.resource('s3')
#object = s3.Object('bucket_name', 'key')


@click.group()
def cli():
        """WebApp will deploy websites to S3."""
        pass


@cli.command("list-buckets")
def list_buckets():
        """List all the S3 Buckets"""
        for b in s3.buckets.all():
                print(b)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List all the objects of Bucket."""
    for o in s3.Bucket(bucket).objects.all():
        print(o)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and Configure S3 bucket."""
    s3_bucket = None
    try :
        s3_bucket = s3.create_bucket(
            Bucket = bucket
    #       CreateBucketConfiguration = {                      --Use this if you want to give more configuration to your bucket
    #               'LocationConstraint': session.region_name}     --Use this if you are using different region from 'us-east-1'
            )

    except ClientError as error:
        if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)

        else:
            raise error


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
        """ % s3_bucket.name

    policy = policy.strip()

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument' : {
            'Key':'error.html'
                },
        'IndexDocument' : {
            'Suffix': 'index.html'
                }
        })

    #    url = "https://%s.s3-website.us-east-1.amazonaws.com" %s s3_bucket.name


def s3_upload(s3_bucket, path, key):
    """Upload path to S3 bucket at key."""
    content_type = mimetypes.guess_type(key)[0] or 'text/html'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType' : 'text/html'
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """This contents of PATHNAME to BUCKET."""

    s3_bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()
    def handle_directory(target):
        for p in target.iterdir():

            if p.is_dir():
                handle_directory(p)

            if p.is_file():
                s3_upload(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)
    #pass

if __name__ == '__main__':
    cli()
