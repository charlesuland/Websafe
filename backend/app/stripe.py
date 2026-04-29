import os

import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_CONNECT_CLIENT_ID = os.getenv("STRIPE_CONNECT_CLIENT_ID", "")


def get_stripe_client():
    return stripe


def construct_webhook_event(payload: bytes, signature_header: str):
    return stripe.Webhook.construct_event(payload, signature_header, STRIPE_WEBHOOK_SECRET)


def create_customer(email: str, name: str, metadata: dict | None = None):
    return stripe.Customer.create(email=email, name=name, metadata=metadata or {})


def create_subscription(customer_id: str, price_id: str):
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        expand=["latest_invoice.payment_intent"]
    )
