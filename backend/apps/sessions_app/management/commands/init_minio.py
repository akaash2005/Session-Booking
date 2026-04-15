from django.core.management.base import BaseCommand
from django.conf import settings
from minio import Minio
from minio.error import S3Error
import json


class Command(BaseCommand):
    help = 'Initialize MinIO bucket for session uploads'

    def handle(self, *args, **options):
        if not settings.USE_MINIO:
            self.stdout.write(self.style.WARNING('MinIO is disabled'))
            return

        try:
            # Connect to MinIO
            minio_client = Minio(
                endpoint=settings.STORAGES['default']['OPTIONS']['endpoint_url'].replace('http://', '').replace('https://', ''),
                access_key=settings.STORAGES['default']['OPTIONS']['access_key'],
                secret_key=settings.STORAGES['default']['OPTIONS']['secret_key'],
                secure=False,
            )

            bucket_name = settings.STORAGES['default']['OPTIONS']['bucket_name']

            # Check if bucket exists
            if minio_client.bucket_exists(bucket_name):
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Bucket "{bucket_name}" already exists')
                )
            else:
                # Create bucket
                minio_client.make_bucket(bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Bucket "{bucket_name}" created successfully')
                )

            # Set public read policy
            try:
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": f"arn:aws:s3:::{bucket_name}/*"
                        }
                    ]
                }
                minio_client.set_bucket_policy(bucket_name, json.dumps(policy))
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Bucket policy set to public read')
                )
            except Exception as policy_err:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Could not set bucket policy: {policy_err}')
                )

        except S3Error as e:
            self.stdout.write(
                self.style.ERROR(f'✗ MinIO Error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error initializing bucket: {e}')
            )
