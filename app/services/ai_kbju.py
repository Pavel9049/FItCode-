from typing import Optional, Dict
from app.config import settings

try:
	from google.cloud import vision  # type: ignore
except Exception:
	vision = None


async def estimate_kbju_from_photo(file_bytes: bytes) -> Dict:
	# Если доступен Vision API и есть креды — распознаём
	if vision and settings.google_application_credentials:
		try:
			client = vision.ImageAnnotatorClient()
			image = vision.Image(content=file_bytes)
			resp = client.label_detection(image=image)
			labels = [l.description for l in resp.label_annotations]
			desc = ", ".join(labels[:5])
			# Условная эвристика для ккал
			kcal = 300
			return {"kcal": kcal, "proteins": 20, "fats": 12, "carbs": 35, "notes": desc, "approx": True}
		except Exception:
			pass
	# Фоллбек: возврат усреднённых значений
	return {"kcal": 320, "proteins": 20, "fats": 15, "carbs": 30, "notes": "Оценка по умолчанию", "approx": True}