# Generated by Django 3.2.12 on 2022-05-25 00:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0006_orderdetail_error_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardtransaction',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='cardtransaction',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='discountcode',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='discountcode',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='order',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='order',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.AlterField(
            model_name='paypaltransaction',
            name='create_timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp'),
        ),
        migrations.AlterField(
            model_name='paypaltransaction',
            name='update_timestamp',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp'),
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(editable=False, max_length=128, unique=True)),
                ('random_slug', models.SlugField(editable=False, unique=True)),
                ('create_timestamp', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created timestamp')),
                ('update_timestamp', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated timestamp')),
                ('type', models.CharField(blank=True, choices=[('payment_action_intent_succeeded', 'payment_action_intent_succeeded'), ('payment_action_intent_failed', 'payment_action_intent_failed'), ('payment_action_customer_create', 'payment_action_customer_create'), ('payment_action_customer_create_error', 'payment_action_customer_create_error'), ('payment_action_customer_delete', 'payment_action_customer_delete'), ('payment_action_customer_delete_error', 'payment_action_customer_delete_error'), ('payment_action_subscription_create', 'payment_action_subscription_create'), ('payment_action_subscription_create_error', 'payment_action_subscription_create_error'), ('payment_action_subscription_cancel', 'payment_action_subscription_cancel'), ('payment_action_coupon_create', 'payment_action_coupon_create'), ('payment_action_coupon_create_error', 'payment_action_coupon_create_error'), ('payment_action_subscription_cancel_error', 'payment_action_subscription_cancel_error'), ('payment_action_payment_method_create', 'payment_action_payment_method_create'), ('payment_action_payment_method_create_error', 'payment_action_payment_method_create_error'), ('payment_action_payment_method_update', 'payment_action_payment_method_update'), ('payment_action_payment_method_attach', 'payment_action_payment_method_attach'), ('payment_action_payment_method_attach_error', 'payment_action_payment_method_attach_error'), ('payment_action_payment_method_modify', 'payment_action_payment_method_modify'), ('payment_action_payment_method_modify_error', 'payment_action_payment_method_modify_error'), ('payment_action_webhook_construct_error', 'payment_action_webhook_construct_error'), ('backend_anction_order_create', 'backend_anction_order_create'), ('backend_anction_order_create_error', 'backend_anction_order_create_error'), ('backend_anction_confirm_payment_order', 'backend_anction_confirm_payment_order'), ('backend_anction_confirm_payment_order_error', 'backend_anction_confirm_payment_order_error'), ('backend_anction_change_default_payment_method', 'backend_anction_change_default_payment_method'), ('backend_anction_edit_payment_method', 'backend_anction_edit_payment_method'), ('backend_anction_edit_payment_method_error', 'backend_anction_edit_payment_method_error'), ('backend_anction_create_order_without_pay', 'backend_anction_create_order_without_pay'), ('backend_anction_create_order_without_pay_error', 'backend_anction_create_order_without_pay_error')], max_length=255, null=True)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('card_number', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='payments.order')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]