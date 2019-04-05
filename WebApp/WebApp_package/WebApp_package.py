import boto3
import click

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



if __name__ == '__main__':
    cli()
