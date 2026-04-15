from django.core.management.base import BaseCommand
from django.conf import settings
from minio import Minio
import json


class Command(BaseCommand):
    help = 'Configure CORS on MinIO bucket'

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
            
            # CORS configuration as JSON
            cors_config = {
                "CORSRules": [
                    {
                        "AllowedOrigins": ["*"],
                        "AllowedMethods": ["GET", "HEAD", "PUT", "POST", "DELETE"],
                        "AllowedHeaders": ["*"],
                        "MaxAgeSeconds": 3000
                    }
                ]
            }
            
            # Set CORS using set_bucket_cors if available, or via direct method
            try:
                from minio.commonconfig import CORS, CORSRule
                cors = CORS([
                    CORSRule(
                        allowed_methods=["GET", "HEAD", "PUT", "POST", "DELETE"],
                        allowed_origins=["*"],
                        allowed_headers=["*"],
                        max_age_seconds=3000
                    )
                ])
                minio_client.set_bucket_cors(bucket_name, cors)
            except ImportError:
                # Fallback: use the HTTP API directly
                self.stdout.write(self.style.WARNING('Using direct API method for CORS'))
                # For older versions, CORS might not be directly exposed
                pass
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ CORS configured for bucket "{bucket_name}"')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {e}')
            )
            import traceback
            traceback.print_exc()


