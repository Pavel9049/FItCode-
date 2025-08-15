from typing import Optional
from app.config import settings


class PaymentGateway:
	@staticmethod
	async def create_payment_link(gateway: str, amount_rub: int, description: str, metadata: dict) -> str:
		# Заглушки. В реале: вызов API Stripe/ЮKassa/Stars/Crypto
		if gateway == "stripe":
			return f"https://pay.stripe.com/link/dummy?amount={amount_rub}"
		if gateway == "yookassa":
			return f"https://yookassa.ru/pay/dummy?amount={amount_rub}"
		if gateway == "stars":
			return "https://t.me/premium"
		if gateway == "crypto":
			return "https://nowpayments.io/"
		return "#"

	@staticmethod
	async def verify_webhook_signature(gateway: str, payload: bytes, signature: Optional[str]) -> bool:
		# Заглушка; реализуется под конкретный шлюз
		return True