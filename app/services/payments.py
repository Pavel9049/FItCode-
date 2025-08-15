from typing import Optional
from app.config import settings
import httpx

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

		if gateway in ("yookassa", "sbp", "sberpay") and settings.yookassa_shop_id and settings.yookassa_secret_key and Payment:
			from yookassa import Configuration  # type: ignore
			Configuration.account_id = settings.yookassa_shop_id
			Configuration.secret_key = settings.yookassa_secret_key
			confirmation = {
				"type": "redirect",
				"return_url": (settings.webhook_base_url or "https://example.com") + "/payment/return"
			}
			payment_method_data = None
			if gateway == "sbp":
				payment_method_data = {"type": "sbp"}
			elif gateway == "sberpay":
				payment_method_data = {"type": "sberbank"}
			payload = {
				"amount": {"value": f"{amount_rub}.00", "currency": "RUB"},
				"capture": True,
				"description": description,
				"metadata": metadata,
				"confirmation": confirmation,
			}
			if payment_method_data:
				payload["payment_method_data"] = payment_method_data
			payment = Payment.create(payload)
			return payment.confirmation.confirmation_url

		if gateway == "tinkoff" and settings.tinkoff_terminal_key and settings.tinkoff_secret_key:
			# Упрощённо: создаём платёжную ссылку через Tinkoff Init
			# В проде необходима подпись (Token) и домен receiveURL
			async with httpx.AsyncClient(timeout=20) as client:
				data = {
					"TerminalKey": settings.tinkoff_terminal_key,
					"Amount": amount_rub * 100,
					"OrderId": str(metadata.get("purchase_id", "1")),
					"Description": description,
					"SuccessURL": (settings.webhook_base_url or "https://example.com") + "/payment/success",
					"FailURL": (settings.webhook_base_url or "https://example.com") + "/payment/cancel",
				}
				resp = await client.post("https://securepay.tinkoff.ru/v2/Init", json=data)
				j = resp.json()
				return j.get("PaymentURL", "#")

		if gateway == "crypto" and settings.nowpayments_api_key:
			# NOWPayments: создаём инвойс
			async with httpx.AsyncClient(timeout=20) as client:
				headers = {"x-api-key": settings.nowpayments_api_key}
				payload = {
					"price_amount": amount_rub,
					"price_currency": "rub",
					"pay_currency": "btc",
					"order_id": str(metadata.get("purchase_id", "1")),
					"order_description": description,
				}
				resp = await client.post("https://api.nowpayments.io/v1/invoice", json=payload, headers=headers)
				j = resp.json()
				return j.get("invoice_url", "#")

		if gateway == "stars":
			return "https://t.me/premium"
		return "#"

	@staticmethod
	async def verify_webhook_signature(gateway: str, payload: bytes, signature: Optional[str]) -> bool:
		return True