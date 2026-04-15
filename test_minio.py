#!/usr/bin/env python
import os
import sys

# Add the backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from minio import Minio

print("Testing MinIO connection...")
print(f"Endpoint: {settings.STORAGES['default']['OPTIONS']['endpoint_url']}")
print(f"Access Key: {settings.STORAGES['default']['OPTIONS']['access_key']}")
print(f"Bucket: {settings.STORAGES['default']['OPTIONS']['storage_bucket_name']}")

endpoint = settings.STORAGES['default']['OPTIONS']['endpoint_url'].replace('http://', '').replace('https://', '')

try:
    minio_client = Minio(
        endpoint=endpoint,
        access_key=settings.STORAGES['default']['OPTIONS']['access_key'],
        secret_key=settings.STORAGES['default']['OPTIONS']['secret_key'],
        secure=False,
    )
    
    print("✓ Connected to MinIO!")
    
    buckets = minio_client.list_buckets()
    print(f"✓ Buckets: {[b.name for b in buckets.buckets]}")
    
    bucket_name = settings.STORAGES['default']['OPTIONS']['storage_bucket_name']
    if minio_client.bucket_exists(bucket_name):
        print(f"✓ Bucket '{bucket_name}' exists")
        # List objects
        objects = minio_client.list_objects(bucket_name)
        print(f"✓ Objects in bucket: {[obj.object_name for obj in objects]}")
    else:
        print(f"✗ Bucket '{bucket_name}' does NOT exist")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
