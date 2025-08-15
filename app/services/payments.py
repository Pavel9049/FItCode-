from typing import Optional
from app.config import settings

try:
	import stripe  # type: ignore
except Exception:
	stripe = None

try:
	from yookassa import Payment  # type: ignore
except Exception:
	Payment = None


class PaymentGateway:
	@staticmethod
	async def create_payment_link(gateway: str, amount_rub: int, description: str, metadata: dict) -> str:
		if gateway == "stripe" and settings.stripe_api_key and stripe:
			stripe.api_key = settings.stripe_api_key
			session = stripe.checkout.Session.create(
				mode="payment",
				payment_method_types=["card"],
				line_items=[{
					"price_data": {
						"currency": "rub",
						"product_data": {"name": description},
						"unit_amount": amount_rub * 100,
					},
					"quantity": 1,
				}],
				metadata=metadata,
				success_url=(settings.webhook_base_url or "https://example.com") + "/payment/success",
				cancel_url=(settings.webhook_base_url or "https://example.com") + "/payment/cancel",
			)
			return session.get("url")

		if gateway == "yookassa" and settings.yookassa_shop_id and settings.yookassa_secret_key and Payment:
			# yookassa требует глобальной конфигурации через SDK, но для простоты создадим платёж напрямую
			from yookassa import Configuration  # type: ignore
			Configuration.account_id = settings.yookassa_shop_id
			Configuration.secret_key = settings.yookassa_secret_key
			payment = Payment.create({
				"amount": {"value": f"{amount_rub}.00", "currency": "RUB"},
				"capture": True,
				"description": description,
				"metadata": metadata,
				"confirmation": {
					"type": "redirect",
					"return_url": (settings.webhook_base_url or "https://example.com") + "/payment/return"
				}
			})
			return payment.confirmation.confirmation_url

		if gateway == "stars":
			return "https://t.me/premium"  # TODO: Stars-интеграция
		if gateway == "crypto":
			return "https://nowpayments.io/"
		return "#"

	@staticmethod
	async def verify_webhook_signature(gateway: str, payload: bytes, signature: Optional[str]) -> bool:
		# Заглушка; проверьте подписи в проде (Stripe: sig header, YooKassa: ip/секрет)
		return True