import boto3
import click

session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')

@click.group()
def cli():
    "Webotron deploys website to AWS"
    pass


@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List all objects in a s3 bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


if __name__ == '__main__':
    cli()


# this file is run as a script, run it
# if this file is imported as a module, don't run it
