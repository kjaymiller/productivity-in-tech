from boto3 import resource

s3 = resource('s3')
bucket = s3.Bucket('pitpodcast')


def add_released(bucket):
    for obj in bucket.objects.filter(Prefix='Released'):
        if obj.key.endswith('.mp3'):
            print(obj.key)
