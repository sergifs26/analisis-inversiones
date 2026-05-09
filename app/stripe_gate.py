import stripe
import streamlit as st


def has_active_subscription(email: str) -> bool:
    """Devuelve True si el email tiene una suscripcion Stripe activa."""
    stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "")
    if not stripe.api_key or stripe.api_key == "sk_test_TU_CLAVE_AQUI":
        return True  # Sin clave configurada: permitir acceso en desarrollo local

    try:
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            return False
        subs = stripe.Subscription.list(
            customer=customers.data[0].id,
            status="active",
            limit=1,
        )
        return len(subs.data) > 0
    except stripe.error.StripeError:
        return False
