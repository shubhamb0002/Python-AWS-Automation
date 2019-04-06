import boto3
import click
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='shotty')
s3 = session.resource('s3')
#object = s3.Object('bucket_name', 'key')

@click.group()
def cli():
        "WebApp will deploy websites to S3"
        pass

@cli.command("list-buckets")
def list_buckets():
        "List all the S3 Buckets"
        for b in s3.buckets.all():
                print(b)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List all the objects of Bucket"
    for o in s3.Bucket(bucket).objects.all():
        print(o)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and Configure S3 bucket"
    s3_bucket = None        
    try :
    s3_bucket = s3.create_bucket(Bucket = bucket
    #    CreateBucketConfiguration = {                      --Use this if you want to give more configuration to your bucket
    #        'LocationConstraint': session.region_name}     --Use this if you are using different region from 'us-east-1'
            )

    except ClientError as e:
        if e.response['Error']['Code'] = 'BucketAlreadyOwnedByYou':
        s3_bucket = s3.Bucket(bucket)

        else:
            raise e


    policy ="""
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


if __name__ == '__main__':
    cli()
