from datetime import datetime, timedelta
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

SAMPLE_MEALS = [
	{"title": "Овсянка с ягодами", "kcal": 320, "proteins": 12, "fats": 8, "carbs": 52, "tags": "breakfast"},
	{"title": "Курица с рисом", "kcal": 450, "proteins": 35, "fats": 10, "carbs": 55, "tags": "lunch"},
	{"title": "Лосось и киноа", "kcal": 520, "proteins": 40, "fats": 20, "carbs": 45, "tags": "dinner"},
	{"title": "Творог с орехами", "kcal": 280, "proteins": 22, "fats": 12, "carbs": 20, "tags": "snack"},
]


def generate_week_menu() -> Dict:
	week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
	days: Dict[str, List[Dict]] = {}
	for i in range(7):
		day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
		days[day] = SAMPLE_MEALS
	return {"week_start": week_start.isoformat(), "days": days}


def render_menu_pdf(menu: Dict) -> bytes:
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=A4)
	width, height = A4
	y = height - 50
	c.setFont("Helvetica-Bold", 16)
	c.drawString(50, y, "Меню на неделю")
	y -= 30
	c.setFont("Helvetica", 11)
	for day, meals in menu["days"].items():
		c.drawString(50, y, day)
		y -= 20
		for m in meals:
			line = f"- {m['title']} — {m['kcal']} ккал / {m['proteins']}Б/{m['fats']}Ж/{m['carbs']}У"
			c.drawString(70, y, line)
			y -= 16
			if y < 80:
				c.showPage()
				y = height - 50
	c.showPage()
	c.save()
	buf.seek(0)
	return buf.read()