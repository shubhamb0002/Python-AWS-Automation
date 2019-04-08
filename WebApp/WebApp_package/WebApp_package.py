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
import boto3
import click
from bucket import BucketManager

session = boto3.Session(profile_name='shotty')
#s3 = session.resource('s3')
#object = s3.Object('bucket_name', 'key')
bucket_manager = BucketManager(session)


@click.group()
def cli():
        """WebApp will deploy websites to S3."""
        pass


@cli.command("list-buckets")
def list_buckets():
        """List all the S3 Buckets"""
        for bucket in bucket_manager.all_buckets():
                print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List all the objects of Bucket."""
    for o in bucket_manager.all_objects(bucket):
        print(o)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and Configure S3 bucket."""

    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """This contents of PATHNAME to BUCKET."""

    bucket_manager.sync(pathname, bucket)


if __name__ == '__main__':
    cli()
