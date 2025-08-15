from aiogram import Router, types
from aiogram.filters import Command
from app.services.meals import generate_week_menu, render_menu_pdf

router = Router()


@router.message(Command("menu"))
async def menu_week(message: types.Message):
	menu = generate_week_menu()
	text_lines = ["Меню на неделю:\n"]
	for day, meals in menu["days"].items():
		text_lines.append(day)
		for m in meals:
			text_lines.append(f"• {m['title']} — {m['kcal']} ккал / {m['proteins']}Б/{m['fats']}Ж/{m['carbs']}У")
		text_lines.append("")
	await message.answer("\n".join(text_lines))

	pdf_bytes = render_menu_pdf(menu)
	await message.answer_document(types.BufferedInputFile(pdf_bytes, filename="menu.pdf"), caption="Скачать меню (PDF)")