from datetime import datetime, timedelta
from typing import Dict, List
from app.db.models import ProgramLevel
import json


SPLITS = [
	{"day": "Push", "groups": ["chest", "shoulders", "triceps"]},
	{"day": "Pull", "groups": ["back", "biceps", "forearms"]},
	{"day": "Legs", "groups": ["legs", "abs", "calves"]},
	{"day": "Upper", "groups": ["back", "chest", "shoulders"]},
	{"day": "Lower", "groups": ["legs", "abs", "glutes"]},
]

# Полная база упражнений по группам мышц и уровням
EXERCISES_DATABASE = {
	"back": {
		"beginner": [
			{"name": "Подтягивания с резинкой", "video_url": "https://youtu.be/back_beginner_1", "description": "Подтягивания с помощью резиновой ленты для облегчения"},
			{"name": "Тяга гантелей в наклоне", "video_url": "https://youtu.be/back_beginner_2", "description": "Тяга гантелей к поясу в наклоне"},
			{"name": "Горизонтальная тяга", "video_url": "https://youtu.be/back_beginner_3", "description": "Тяга блока к поясу сидя"},
			{"name": "Тяга верхнего блока", "video_url": "https://youtu.be/back_beginner_4", "description": "Тяга верхнего блока к груди"},
			{"name": "Гиперэкстензия", "video_url": "https://youtu.be/back_beginner_5", "description": "Разгибание спины на тренажере"}
		],
		"novice": [
			{"name": "Подтягивания широким хватом", "video_url": "https://youtu.be/back_novice_1", "description": "Подтягивания на турнике широким хватом"},
			{"name": "Тяга штанги в наклоне", "video_url": "https://youtu.be/back_novice_2", "description": "Тяга штанги к поясу в наклоне"},
			{"name": "Тяга Т-грифа", "video_url": "https://youtu.be/back_novice_3", "description": "Тяга Т-грифа одной рукой"},
			{"name": "Подтягивания обратным хватом", "video_url": "https://youtu.be/back_novice_4", "description": "Подтягивания обратным хватом"},
			{"name": "Тяга гантелей лежа", "video_url": "https://youtu.be/back_novice_5", "description": "Тяга гантелей лежа на скамье"},
			{"name": "Тяга нижнего блока", "video_url": "https://youtu.be/back_novice_6", "description": "Тяга нижнего блока к поясу"},
			{"name": "Тяга верхнего блока за голову", "video_url": "https://youtu.be/back_novice_7", "description": "Тяга верхнего блока за голову"},
			{"name": "Тяга одной гантели в наклоне", "video_url": "https://youtu.be/back_novice_8", "description": "Тяга одной гантели с упором на колено"},
			{"name": "Тяга каната", "video_url": "https://youtu.be/back_novice_9", "description": "Тяга каната к лицу"},
			{"name": "Тяга в тренажере Смита", "video_url": "https://youtu.be/back_novice_10", "description": "Тяга штанги в тренажере Смита"}
		],
		"advanced": [
			{"name": "Подтягивания с весом", "video_url": "https://youtu.be/back_advanced_1", "description": "Подтягивания с дополнительным весом"},
			{"name": "Тяга штанги в наклоне с паузой", "video_url": "https://youtu.be/back_advanced_2", "description": "Тяга с паузой в верхней точке"},
			{"name": "Подтягивания на одной руке", "video_url": "https://youtu.be/back_advanced_3", "description": "Подтягивания с помощью одной руки"},
			{"name": "Тяга гантелей с супинацией", "video_url": "https://youtu.be/back_advanced_4", "description": "Тяга с поворотом кисти"},
			{"name": "Тяга верхнего блока узким хватом", "video_url": "https://youtu.be/back_advanced_5", "description": "Тяга узким хватом к груди"},
			{"name": "Тяга Т-грифа с паузой", "video_url": "https://youtu.be/back_advanced_6", "description": "Тяга с паузой в верхней точке"},
			{"name": "Подтягивания с хлопком", "video_url": "https://youtu.be/back_advanced_7", "description": "Подтягивания с хлопком в верхней точке"},
			{"name": "Тяга гантелей в наклоне с паузой", "video_url": "https://youtu.be/back_advanced_8", "description": "Тяга с паузой в верхней точке"},
			{"name": "Тяга каната одной рукой", "video_url": "https://youtu.be/back_advanced_9", "description": "Тяга каната одной рукой"},
			{"name": "Тяга нижнего блока с паузой", "video_url": "https://youtu.be/back_advanced_10", "description": "Тяга с паузой в верхней точке"},
			{"name": "Подтягивания с резинкой и весом", "video_url": "https://youtu.be/back_advanced_11", "description": "Комбинированное упражнение"},
			{"name": "Тяга штанги в наклоне с дроп-сетом", "video_url": "https://youtu.be/back_advanced_12", "description": "Тяга с дроп-сетом"},
			{"name": "Тяга гантелей лежа с паузой", "video_url": "https://youtu.be/back_advanced_13", "description": "Тяга лежа с паузой"},
			{"name": "Подтягивания с изменением хвата", "video_url": "https://youtu.be/back_advanced_14", "description": "Подтягивания с сменой хвата"},
			{"name": "Тяга верхнего блока с паузой", "video_url": "https://youtu.be/back_advanced_15", "description": "Тяга с паузой в нижней точке"}
		],
		"pro": [
			{"name": "Подтягивания с весом 20кг+", "video_url": "https://youtu.be/back_pro_1", "description": "Подтягивания с большим дополнительным весом"},
			{"name": "Тяга штанги в наклоне с дроп-сетом", "video_url": "https://youtu.be/back_pro_2", "description": "Тяга с дроп-сетом и паузами"},
			{"name": "Подтягивания на одной руке без помощи", "video_url": "https://youtu.be/back_pro_3", "description": "Полные подтягивания на одной руке"},
			{"name": "Тяга гантелей с супинацией и паузой", "video_url": "https://youtu.be/back_pro_4", "description": "Тяга с поворотом и паузой"},
			{"name": "Тяга верхнего блока с дроп-сетом", "video_url": "https://youtu.be/back_pro_5", "description": "Тяга с дроп-сетом"},
			{"name": "Тяга Т-грифа с дроп-сетом", "video_url": "https://youtu.be/back_pro_6", "description": "Тяга с дроп-сетом и паузами"},
			{"name": "Подтягивания с хлопком и весом", "video_url": "https://youtu.be/back_pro_7", "description": "Подтягивания с хлопком и весом"},
			{"name": "Тяга гантелей в наклоне с дроп-сетом", "video_url": "https://youtu.be/back_pro_8", "description": "Тяга с дроп-сетом"},
			{"name": "Тяга каната с дроп-сетом", "video_url": "https://youtu.be/back_pro_9", "description": "Тяга каната с дроп-сетом"},
			{"name": "Тяга нижнего блока с дроп-сетом", "video_url": "https://youtu.be/back_pro_10", "description": "Тяга с дроп-сетом"},
			{"name": "Подтягивания с резинкой и большим весом", "video_url": "https://youtu.be/back_pro_11", "description": "Комбинированное упражнение с весом"},
			{"name": "Тяга штанги в наклоне с суперсетом", "video_url": "https://youtu.be/back_pro_12", "description": "Тяга с суперсетом"},
			{"name": "Тяга гантелей лежа с дроп-сетом", "video_url": "https://youtu.be/back_pro_13", "description": "Тяга лежа с дроп-сетом"},
			{"name": "Подтягивания с изменением хвата и весом", "video_url": "https://youtu.be/back_pro_14", "description": "Подтягивания с сменой хвата и весом"},
			{"name": "Тяга верхнего блока с суперсетом", "video_url": "https://youtu.be/back_pro_15", "description": "Тяга с суперсетом"},
			{"name": "Тяга Т-грифа с суперсетом", "video_url": "https://youtu.be/back_pro_16", "description": "Тяга с суперсетом"},
			{"name": "Подтягивания с хлопком и большим весом", "video_url": "https://youtu.be/back_pro_17", "description": "Подтягивания с хлопком и большим весом"},
			{"name": "Тяга гантелей в наклоне с суперсетом", "video_url": "https://youtu.be/back_pro_18", "description": "Тяга с суперсетом"},
			{"name": "Тяга каната с суперсетом", "video_url": "https://youtu.be/back_pro_19", "description": "Тяга каната с суперсетом"},
			{"name": "Тяга нижнего блока с суперсетом", "video_url": "https://youtu.be/back_pro_20", "description": "Тяга с суперсетом"}
		]
	},
	"chest": {
		"beginner": [
			{"name": "Отжимания от стены", "video_url": "https://youtu.be/chest_beginner_1", "description": "Отжимания от стены для начинающих"},
			{"name": "Жим гантелей лежа", "video_url": "https://youtu.be/chest_beginner_2", "description": "Жим гантелей лежа на скамье"},
			{"name": "Разведение гантелей лежа", "video_url": "https://youtu.be/chest_beginner_3", "description": "Разведение гантелей лежа на скамье"},
			{"name": "Жим в тренажере", "video_url": "https://youtu.be/chest_beginner_4", "description": "Жим в тренажере для груди"},
			{"name": "Отжимания с колен", "video_url": "https://youtu.be/chest_beginner_5", "description": "Отжимания с колен"}
		],
		"novice": [
			{"name": "Отжимания от пола", "video_url": "https://youtu.be/chest_novice_1", "description": "Классические отжимания от пола"},
			{"name": "Жим штанги лежа", "video_url": "https://youtu.be/chest_novice_2", "description": "Жим штанги лежа на скамье"},
			{"name": "Разведение гантелей лежа", "video_url": "https://youtu.be/chest_novice_3", "description": "Разведение гантелей лежа"},
			{"name": "Жим гантелей на наклонной скамье", "video_url": "https://youtu.be/chest_novice_4", "description": "Жим гантелей на наклонной скамье"},
			{"name": "Отжимания на брусьях", "video_url": "https://youtu.be/chest_novice_5", "description": "Отжимания на брусьях"},
			{"name": "Жим штанги на наклонной скамье", "video_url": "https://youtu.be/chest_novice_6", "description": "Жим штанги на наклонной скамье"},
			{"name": "Разведение гантелей на наклонной скамье", "video_url": "https://youtu.be/chest_novice_7", "description": "Разведение гантелей на наклонной скамье"},
			{"name": "Жим в тренажере Смита", "video_url": "https://youtu.be/chest_novice_8", "description": "Жим в тренажере Смита"},
			{"name": "Отжимания с широкой постановкой рук", "video_url": "https://youtu.be/chest_novice_9", "description": "Отжимания с широкой постановкой рук"},
			{"name": "Жим гантелей лежа с паузой", "video_url": "https://youtu.be/chest_novice_10", "description": "Жим гантелей лежа с паузой"}
		],
		"advanced": [
			{"name": "Отжимания с хлопком", "video_url": "https://youtu.be/chest_advanced_1", "description": "Отжимания с хлопком в верхней точке"},
			{"name": "Жим штанги лежа с паузой", "video_url": "https://youtu.be/chest_advanced_2", "description": "Жим штанги лежа с паузой"},
			{"name": "Разведение гантелей лежа с паузой", "video_url": "https://youtu.be/chest_advanced_3", "description": "Разведение гантелей лежа с паузой"},
			{"name": "Жим гантелей на наклонной скамье с паузой", "video_url": "https://youtu.be/chest_advanced_4", "description": "Жим гантелей на наклонной скамье с паузой"},
			{"name": "Отжимания на брусьях с весом", "video_url": "https://youtu.be/chest_advanced_5", "description": "Отжимания на брусьях с дополнительным весом"},
			{"name": "Жим штанги на наклонной скамье с паузой", "video_url": "https://youtu.be/chest_advanced_6", "description": "Жим штанги на наклонной скамье с паузой"},
			{"name": "Разведение гантелей на наклонной скамье с паузой", "video_url": "https://youtu.be/chest_advanced_7", "description": "Разведение гантелей на наклонной скамье с паузой"},
			{"name": "Жим в тренажере Смита с паузой", "video_url": "https://youtu.be/chest_advanced_8", "description": "Жим в тренажере Смита с паузой"},
			{"name": "Отжимания с широкой постановкой рук и хлопком", "video_url": "https://youtu.be/chest_advanced_9", "description": "Отжимания с широкой постановкой рук и хлопком"},
			{"name": "Жим гантелей лежа с дроп-сетом", "video_url": "https://youtu.be/chest_advanced_10", "description": "Жим гантелей лежа с дроп-сетом"},
			{"name": "Отжимания с хлопком и весом", "video_url": "https://youtu.be/chest_advanced_11", "description": "Отжимания с хлопком и дополнительным весом"},
			{"name": "Жим штанги лежа с дроп-сетом", "video_url": "https://youtu.be/chest_advanced_12", "description": "Жим штанги лежа с дроп-сетом"},
			{"name": "Разведение гантелей лежа с дроп-сетом", "video_url": "https://youtu.be/chest_advanced_13", "description": "Разведение гантелей лежа с дроп-сетом"},
			{"name": "Жим гантелей на наклонной скамье с дроп-сетом", "video_url": "https://youtu.be/chest_advanced_14", "description": "Жим гантелей на наклонной скамье с дроп-сетом"},
			{"name": "Отжимания на брусьях с большим весом", "video_url": "https://youtu.be/chest_advanced_15", "description": "Отжимания на брусьях с большим дополнительным весом"}
		],
		"pro": [
			{"name": "Отжимания с хлопком и большим весом", "video_url": "https://youtu.be/chest_pro_1", "description": "Отжимания с хлопком и большим дополнительным весом"},
			{"name": "Жим штанги лежа с дроп-сетом", "video_url": "https://youtu.be/chest_pro_2", "description": "Жим штанги лежа с дроп-сетом и паузами"},
			{"name": "Разведение гантелей лежа с дроп-сетом", "video_url": "https://youtu.be/chest_pro_3", "description": "Разведение гантелей лежа с дроп-сетом"},
			{"name": "Жим гантелей на наклонной скамье с дроп-сетом", "video_url": "https://youtu.be/chest_pro_4", "description": "Жим гантелей на наклонной скамье с дроп-сетом"},
			{"name": "Отжимания на брусьях с большим весом", "video_url": "https://youtu.be/chest_pro_5", "description": "Отжимания на брусьях с большим дополнительным весом"},
			{"name": "Жим штанги на наклонной скамье с дроп-сетом", "video_url": "https://youtu.be/chest_pro_6", "description": "Жим штанги на наклонной скамье с дроп-сетом"},
			{"name": "Разведение гантелей на наклонной скамье с дроп-сетом", "video_url": "https://youtu.be/chest_pro_7", "description": "Разведение гантелей на наклонной скамье с дроп-сетом"},
			{"name": "Жим в тренажере Смита с дроп-сетом", "video_url": "https://youtu.be/chest_pro_8", "description": "Жим в тренажере Смита с дроп-сетом"},
			{"name": "Отжимания с широкой постановкой рук и хлопком с весом", "video_url": "https://youtu.be/chest_pro_9", "description": "Отжимания с широкой постановкой рук и хлопком с весом"},
			{"name": "Жим гантелей лежа с суперсетом", "video_url": "https://youtu.be/chest_pro_10", "description": "Жим гантелей лежа с суперсетом"},
			{"name": "Отжимания с хлопком и большим весом", "video_url": "https://youtu.be/chest_pro_11", "description": "Отжимания с хлопком и большим дополнительным весом"},
			{"name": "Жим штанги лежа с суперсетом", "video_url": "https://youtu.be/chest_pro_12", "description": "Жим штанги лежа с суперсетом"},
			{"name": "Разведение гантелей лежа с суперсетом", "video_url": "https://youtu.be/chest_pro_13", "description": "Разведение гантелей лежа с суперсетом"},
			{"name": "Жим гантелей на наклонной скамье с суперсетом", "video_url": "https://youtu.be/chest_pro_14", "description": "Жим гантелей на наклонной скамье с суперсетом"},
			{"name": "Отжимания на брусьях с максимальным весом", "video_url": "https://youtu.be/chest_pro_15", "description": "Отжимания на брусьях с максимальным дополнительным весом"},
			{"name": "Жим штанги на наклонной скамье с суперсетом", "video_url": "https://youtu.be/chest_pro_16", "description": "Жим штанги на наклонной скамье с суперсетом"},
			{"name": "Разведение гантелей на наклонной скамье с суперсетом", "video_url": "https://youtu.be/chest_pro_17", "description": "Разведение гантелей на наклонной скамье с суперсетом"},
			{"name": "Жим в тренажере Смита с суперсетом", "video_url": "https://youtu.be/chest_pro_18", "description": "Жим в тренажере Смита с суперсетом"},
			{"name": "Отжимания с широкой постановкой рук и хлопком с большим весом", "video_url": "https://youtu.be/chest_pro_19", "description": "Отжимания с широкой постановкой рук и хлопком с большим весом"},
			{"name": "Жим гантелей лежа с трисетом", "video_url": "https://youtu.be/chest_pro_20", "description": "Жим гантелей лежа с трисетом"}
		]
	}
}

# Упражнения без инвентаря
BODYWEIGHT_EX = {
	"beginner": [
		{"name": "Приседания", "video_url": "https://youtu.be/bodyweight_beginner_1", "description": "Классические приседания без веса"},
		{"name": "Отжимания от стены", "video_url": "https://youtu.be/bodyweight_beginner_2", "description": "Отжимания от стены для начинающих"},
		{"name": "Планка 20с", "video_url": "https://youtu.be/bodyweight_beginner_3", "description": "Планка на 20 секунд"},
		{"name": "Выпады на месте", "video_url": "https://youtu.be/bodyweight_beginner_4", "description": "Выпады на месте без веса"},
		{"name": "Подъемы на носки", "video_url": "https://youtu.be/bodyweight_beginner_5", "description": "Подъемы на носки стоя"},
		{"name": "Скручивания", "video_url": "https://youtu.be/bodyweight_beginner_6", "description": "Скручивания лежа на спине"},
		{"name": "Отжимания с колен", "video_url": "https://youtu.be/bodyweight_beginner_7", "description": "Отжимания с колен"},
		{"name": "Приседания с выпрыгиванием", "video_url": "https://youtu.be/bodyweight_beginner_8", "description": "Приседания с выпрыгиванием"},
		{"name": "Берпи", "video_url": "https://youtu.be/bodyweight_beginner_9", "description": "Берпи для начинающих"},
		{"name": "Мостик", "video_url": "https://youtu.be/bodyweight_beginner_10", "description": "Мостик лежа на спине"}
	],
	"novice": [
		{"name": "Отжимания", "video_url": "https://youtu.be/bodyweight_novice_1", "description": "Классические отжимания от пола"},
		{"name": "Выпады", "video_url": "https://youtu.be/bodyweight_novice_2", "description": "Выпады вперед"},
		{"name": "Планка 30с", "video_url": "https://youtu.be/bodyweight_novice_3", "description": "Планка на 30 секунд"},
		{"name": "Приседания с выпрыгиванием", "video_url": "https://youtu.be/bodyweight_novice_4", "description": "Приседания с выпрыгиванием"},
		{"name": "Берпи", "video_url": "https://youtu.be/bodyweight_novice_5", "description": "Классические берпи"},
		{"name": "Отжимания с широкой постановкой рук", "video_url": "https://youtu.be/bodyweight_novice_6", "description": "Отжимания с широкой постановкой рук"},
		{"name": "Выпады в стороны", "video_url": "https://youtu.be/bodyweight_novice_7", "description": "Выпады в стороны"},
		{"name": "Планка с подъемом ноги", "video_url": "https://youtu.be/bodyweight_novice_8", "description": "Планка с подъемом ноги"},
		{"name": "Приседания с хлопком", "video_url": "https://youtu.be/bodyweight_novice_9", "description": "Приседания с хлопком в верхней точке"},
		{"name": "Отжимания с хлопком", "video_url": "https://youtu.be/bodyweight_novice_10", "description": "Отжимания с хлопком"}
	],
	"advanced": [
		{"name": "Отжимания + хлопок", "video_url": "https://youtu.be/bodyweight_advanced_1", "description": "Отжимания с хлопком в верхней точке"},
		{"name": "Пистолетики", "video_url": "https://youtu.be/bodyweight_advanced_2", "description": "Приседания на одной ноге"},
		{"name": "Планка 45с", "video_url": "https://youtu.be/bodyweight_advanced_3", "description": "Планка на 45 секунд"},
		{"name": "Приседания с выпрыгиванием и хлопком", "video_url": "https://youtu.be/bodyweight_advanced_4", "description": "Приседания с выпрыгиванием и хлопком"},
		{"name": "Берпи с хлопком", "video_url": "https://youtu.be/bodyweight_advanced_5", "description": "Берпи с хлопком в верхней точке"},
		{"name": "Отжимания с широкой постановкой рук и хлопком", "video_url": "https://youtu.be/bodyweight_advanced_6", "description": "Отжимания с широкой постановкой рук и хлопком"},
		{"name": "Выпады в стороны с прыжком", "video_url": "https://youtu.be/bodyweight_advanced_7", "description": "Выпады в стороны с прыжком"},
		{"name": "Планка с подъемом ноги и руки", "video_url": "https://youtu.be/bodyweight_advanced_8", "description": "Планка с подъемом ноги и руки"},
		{"name": "Приседания с хлопком и прыжком", "video_url": "https://youtu.be/bodyweight_advanced_9", "description": "Приседания с хлопком и прыжком"},
		{"name": "Отжимания с хлопком и прыжком", "video_url": "https://youtu.be/bodyweight_advanced_10", "description": "Отжимания с хлопком и прыжком"}
	],
	"pro": [
		{"name": "Отжимания в стойке у стены", "video_url": "https://youtu.be/bodyweight_pro_1", "description": "Отжимания в стойке на руках у стены"},
		{"name": "Прыжковые приседания", "video_url": "https://youtu.be/bodyweight_pro_2", "description": "Приседания с максимальным выпрыгиванием"},
		{"name": "Планка 60с", "video_url": "https://youtu.be/bodyweight_pro_3", "description": "Планка на 60 секунд"},
		{"name": "Приседания с выпрыгиванием и двойным хлопком", "video_url": "https://youtu.be/bodyweight_pro_4", "description": "Приседания с выпрыгиванием и двойным хлопком"},
		{"name": "Берпи с двойным хлопком", "video_url": "https://youtu.be/bodyweight_pro_5", "description": "Берпи с двойным хлопком"},
		{"name": "Отжимания в стойке на руках", "video_url": "https://youtu.be/bodyweight_pro_6", "description": "Отжимания в стойке на руках без опоры"},
		{"name": "Выпады в стороны с двойным прыжком", "video_url": "https://youtu.be/bodyweight_pro_7", "description": "Выпады в стороны с двойным прыжком"},
		{"name": "Планка с подъемом ноги и руки и поворотом", "video_url": "https://youtu.be/bodyweight_pro_8", "description": "Планка с подъемом ноги и руки и поворотом"},
		{"name": "Приседания с хлопком и двойным прыжком", "video_url": "https://youtu.be/bodyweight_pro_9", "description": "Приседания с хлопком и двойным прыжком"},
		{"name": "Отжимания с хлопком и двойным прыжком", "video_url": "https://youtu.be/bodyweight_pro_10", "description": "Отжимания с хлопком и двойным прыжком"}
	]
}


def estimate_working_weight(weight_kg: float | None, level: ProgramLevel | None) -> int:
	if not weight_kg:
		return 10
	factor = {ProgramLevel.beginner: 0.2, ProgramLevel.novice: 0.3, ProgramLevel.advanced: 0.4, ProgramLevel.pro: 0.5}.get(level or ProgramLevel.beginner, 0.25)
	return max(5, int(weight_kg * factor))


def get_exercises_for_muscle_group(muscle_group: str, level: ProgramLevel) -> List[Dict]:
	"""Получить упражнения для конкретной группы мышц и уровня"""
	if muscle_group in EXERCISES_DATABASE:
		return EXERCISES_DATABASE[muscle_group].get(level.value, [])
	return []


def get_bodyweight_exercises(level: ProgramLevel) -> List[Dict]:
	"""Получить упражнения без инвентаря для уровня"""
	return BODYWEIGHT_EX.get(level.value, [])


def generate_week_plan(level: ProgramLevel, goal: str, weight_kg: float | None, has_equipment: bool) -> Dict:
	week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
	plan: Dict[str, List[Dict]] = {}
	
	if not has_equipment:
		# Домашние тренировки без инвентаря
		ex_list = get_bodyweight_exercises(level)
		for i in range(7):
			day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
			# Выбираем случайные упражнения для каждого дня
			import random
			day_exercises = random.sample(ex_list, min(5, len(ex_list)))
			plan[day] = [
				{
					"name": ex["name"], 
					"sets": 3, 
					"reps": 12,
					"video_url": ex["video_url"],
					"description": ex["description"]
				} for ex in day_exercises
			]
		return {
			"type": "bodyweight", 
			"goal": goal, 
			"level": level.value, 
			"week_start": week_start.isoformat(), 
			"days": plan
		}
	else:
		# Сплит PPL/Upper/Lower
		for i in range(5):
			day = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
			split = SPLITS[i]
			entries = []
			for g in split["groups"]:
				exercises = get_exercises_for_muscle_group(g, level)
				if exercises:
					# Выбираем случайные упражнения для группы мышц
					import random
					selected_exercises = random.sample(exercises, min(3, len(exercises)))
					entries.append({
						"group": g,
						"exercises": [
							{
								"name": ex["name"], 
								"sets": 4, 
								"reps": 10, 
								"weight": estimate_working_weight(weight_kg, level),
								"video_url": ex["video_url"],
								"description": ex["description"]
							} for ex in selected_exercises
						]
					})
			plan[day] = entries
		return {
			"type": "split", 
			"goal": goal, 
			"level": level.value, 
			"week_start": week_start.isoformat(), 
			"days": plan
		}


def get_muscle_groups() -> List[str]:
	"""Получить список всех групп мышц"""
	return list(EXERCISES_DATABASE.keys())


def get_split_info() -> List[Dict]:
	"""Получить информацию о сплитах"""
	return SPLITS