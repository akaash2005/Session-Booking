# Generated migration to switch from Stripe to Razorpay

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        # Remove Stripe field
        migrations.RemoveField(
            model_name='payment',
            name='stripe_payment_intent_id',
        ),
        # Add Razorpay fields
        migrations.AddField(
            model_name='payment',
            name='razorpay_order_id',
            field=models.CharField(default='temp', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='razorpay_signature',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        # Update currency default from USD to INR
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.CharField(default='INR', max_length=3),
        ),
        # Update status choices to include AUTHORIZED
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('authorized', 'Authorized'),
                    ('success', 'Success'),
                    ('failed', 'Failed'),
                    ('cancelled', 'Cancelled'),
                    ('refunded', 'Refunded'),
                ],
                default='pending',
                max_length=20
            ),
        ),
    ]
