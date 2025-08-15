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
			{"name": "Гиперэкстензия", "video_url": "https://youtu.be/back_beginner_5", "description": "Разгибание спины на тренажере"},
			{"name": "Тяга одной гантели", "video_url": "https://youtu.be/back_beginner_6", "description": "Тяга одной гантели с упором на колено"},
			{"name": "Тяга каната сидя", "video_url": "https://youtu.be/back_beginner_7", "description": "Тяга каната к лицу сидя"},
			{"name": "Тяга в тренажере", "video_url": "https://youtu.be/back_beginner_8", "description": "Тяга в тренажере для спины"},
			{"name": "Подтягивания с поддержкой", "video_url": "https://youtu.be/back_beginner_9", "description": "Подтягивания с поддержкой партнера"},
			{"name": "Тяга резинки к поясу", "video_url": "https://youtu.be/back_beginner_10", "description": "Тяга резиновой ленты к поясу"}
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
	},
	"biceps": {
		"beginner": [
			{"name": "Сгибания рук с гантелями", "video_url": "https://youtu.be/biceps_beginner_1", "description": "Сгибания рук с гантелями стоя"},
			{"name": "Молотки", "video_url": "https://youtu.be/biceps_beginner_2", "description": "Сгибания рук молотковым хватом"},
			{"name": "Сгибания рук с резинкой", "video_url": "https://youtu.be/biceps_beginner_3", "description": "Сгибания рук с резиновой лентой"},
			{"name": "Концентрированные сгибания", "video_url": "https://youtu.be/biceps_beginner_4", "description": "Концентрированные сгибания сидя"},
			{"name": "Сгибания рук на скамье Скотта", "video_url": "https://youtu.be/biceps_beginner_5", "description": "Сгибания рук на скамье Скотта"},
			{"name": "Сгибания рук с гантелями сидя", "video_url": "https://youtu.be/biceps_beginner_6", "description": "Сгибания рук с гантелями сидя"},
			{"name": "Сгибания рук с одной гантелью", "video_url": "https://youtu.be/biceps_beginner_7", "description": "Сгибания рук с одной гантелью"},
			{"name": "Сгибания рук с резинкой стоя", "video_url": "https://youtu.be/biceps_beginner_8", "description": "Сгибания рук с резинкой стоя"},
			{"name": "Сгибания рук на нижнем блоке", "video_url": "https://youtu.be/biceps_beginner_9", "description": "Сгибания рук на нижнем блоке"},
			{"name": "Сгибания рук с гантелями в наклоне", "video_url": "https://youtu.be/biceps_beginner_10", "description": "Сгибания рук с гантелями в наклоне"}
		],
		"novice": [
			{"name": "Сгибания рук со штангой", "video_url": "https://youtu.be/biceps_novice_1", "description": "Сгибания рук со штангой стоя"},
			{"name": "Сгибания рук с гантелями с супинацией", "video_url": "https://youtu.be/biceps_novice_2", "description": "Сгибания рук с поворотом кисти"},
			{"name": "Молотки сидя", "video_url": "https://youtu.be/biceps_novice_3", "description": "Молотковые сгибания сидя"},
			{"name": "Сгибания рук на скамье Скотта со штангой", "video_url": "https://youtu.be/biceps_novice_4", "description": "Сгибания рук на скамье Скотта со штангой"},
			{"name": "Концентрированные сгибания с гантелью", "video_url": "https://youtu.be/biceps_novice_5", "description": "Концентрированные сгибания с гантелью"},
			{"name": "Сгибания рук с гантелями лежа", "video_url": "https://youtu.be/biceps_novice_6", "description": "Сгибания рук с гантелями лежа на скамье"},
			{"name": "Сгибания рук на верхнем блоке", "video_url": "https://youtu.be/biceps_novice_7", "description": "Сгибания рук на верхнем блоке"},
			{"name": "Сгибания рук с гантелями попеременно", "video_url": "https://youtu.be/biceps_novice_8", "description": "Сгибания рук с гантелями попеременно"},
			{"name": "Сгибания рук с резинкой сидя", "video_url": "https://youtu.be/biceps_novice_9", "description": "Сгибания рук с резинкой сидя"},
			{"name": "Сгибания рук с гантелями в наклоне сидя", "video_url": "https://youtu.be/biceps_novice_10", "description": "Сгибания рук с гантелями в наклоне сидя"}
		],
		"advanced": [
			{"name": "Сгибания рук со штангой с паузой", "video_url": "https://youtu.be/biceps_advanced_1", "description": "Сгибания рук со штангой с паузой"},
			{"name": "Сгибания рук с гантелями с супинацией и паузой", "video_url": "https://youtu.be/biceps_advanced_2", "description": "Сгибания рук с поворотом и паузой"},
			{"name": "Молотки с паузой", "video_url": "https://youtu.be/biceps_advanced_3", "description": "Молотковые сгибания с паузой"},
			{"name": "Сгибания рук на скамье Скотта с паузой", "video_url": "https://youtu.be/biceps_advanced_4", "description": "Сгибания рук на скамье Скотта с паузой"},
			{"name": "Концентрированные сгибания с паузой", "video_url": "https://youtu.be/biceps_advanced_5", "description": "Концентрированные сгибания с паузой"},
			{"name": "Сгибания рук с гантелями лежа с паузой", "video_url": "https://youtu.be/biceps_advanced_6", "description": "Сгибания рук с гантелями лежа с паузой"},
			{"name": "Сгибания рук на верхнем блоке с паузой", "video_url": "https://youtu.be/biceps_advanced_7", "description": "Сгибания рук на верхнем блоке с паузой"},
			{"name": "Сгибания рук с гантелями попеременно с паузой", "video_url": "https://youtu.be/biceps_advanced_8", "description": "Сгибания рук с гантелями попеременно с паузой"},
			{"name": "Сгибания рук с резинкой сидя с паузой", "video_url": "https://youtu.be/biceps_advanced_9", "description": "Сгибания рук с резинкой сидя с паузой"},
			{"name": "Сгибания рук с гантелями в наклоне сидя с паузой", "video_url": "https://youtu.be/biceps_advanced_10", "description": "Сгибания рук с гантелями в наклоне сидя с паузой"},
			{"name": "Сгибания рук со штангой с дроп-сетом", "video_url": "https://youtu.be/biceps_advanced_11", "description": "Сгибания рук со штангой с дроп-сетом"},
			{"name": "Сгибания рук с гантелями с супинацией и дроп-сетом", "video_url": "https://youtu.be/biceps_advanced_12", "description": "Сгибания рук с поворотом и дроп-сетом"},
			{"name": "Молотки с дроп-сетом", "video_url": "https://youtu.be/biceps_advanced_13", "description": "Молотковые сгибания с дроп-сетом"},
			{"name": "Сгибания рук на скамье Скотта с дроп-сетом", "video_url": "https://youtu.be/biceps_advanced_14", "description": "Сгибания рук на скамье Скотта с дроп-сетом"},
			{"name": "Концентрированные сгибания с дроп-сетом", "video_url": "https://youtu.be/biceps_advanced_15", "description": "Концентрированные сгибания с дроп-сетом"}
		],
		"pro": [
			{"name": "Сгибания рук со штангой с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_1", "description": "Сгибания рук со штангой с дроп-сетом и паузами"},
			{"name": "Сгибания рук с гантелями с супинацией и дроп-сетом", "video_url": "https://youtu.be/biceps_pro_2", "description": "Сгибания рук с поворотом и дроп-сетом"},
			{"name": "Молотки с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_3", "description": "Молотковые сгибания с дроп-сетом"},
			{"name": "Сгибания рук на скамье Скотта с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_4", "description": "Сгибания рук на скамье Скотта с дроп-сетом"},
			{"name": "Концентрированные сгибания с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_5", "description": "Концентрированные сгибания с дроп-сетом"},
			{"name": "Сгибания рук с гантелями лежа с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_6", "description": "Сгибания рук с гантелями лежа с дроп-сетом"},
			{"name": "Сгибания рук на верхнем блоке с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_7", "description": "Сгибания рук на верхнем блоке с дроп-сетом"},
			{"name": "Сгибания рук с гантелями попеременно с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_8", "description": "Сгибания рук с гантелями попеременно с дроп-сетом"},
			{"name": "Сгибания рук с резинкой сидя с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_9", "description": "Сгибания рук с резинкой сидя с дроп-сетом"},
			{"name": "Сгибания рук с гантелями в наклоне сидя с дроп-сетом", "video_url": "https://youtu.be/biceps_pro_10", "description": "Сгибания рук с гантелями в наклоне сидя с дроп-сетом"},
			{"name": "Сгибания рук со штангой с суперсетом", "video_url": "https://youtu.be/biceps_pro_11", "description": "Сгибания рук со штангой с суперсетом"},
			{"name": "Сгибания рук с гантелями с супинацией и суперсетом", "video_url": "https://youtu.be/biceps_pro_12", "description": "Сгибания рук с поворотом и суперсетом"},
			{"name": "Молотки с суперсетом", "video_url": "https://youtu.be/biceps_pro_13", "description": "Молотковые сгибания с суперсетом"},
			{"name": "Сгибания рук на скамье Скотта с суперсетом", "video_url": "https://youtu.be/biceps_pro_14", "description": "Сгибания рук на скамье Скотта с суперсетом"},
			{"name": "Концентрированные сгибания с суперсетом", "video_url": "https://youtu.be/biceps_pro_15", "description": "Концентрированные сгибания с суперсетом"},
			{"name": "Сгибания рук с гантелями лежа с суперсетом", "video_url": "https://youtu.be/biceps_pro_16", "description": "Сгибания рук с гантелями лежа с суперсетом"},
			{"name": "Сгибания рук на верхнем блоке с суперсетом", "video_url": "https://youtu.be/biceps_pro_17", "description": "Сгибания рук на верхнем блоке с суперсетом"},
			{"name": "Сгибания рук с гантелями попеременно с суперсетом", "video_url": "https://youtu.be/biceps_pro_18", "description": "Сгибания рук с гантелями попеременно с суперсетом"},
			{"name": "Сгибания рук с резинкой сидя с суперсетом", "video_url": "https://youtu.be/biceps_pro_19", "description": "Сгибания рук с резинкой сидя с суперсетом"},
			{"name": "Сгибания рук с гантелями в наклоне сидя с суперсетом", "video_url": "https://youtu.be/biceps_pro_20", "description": "Сгибания рук с гантелями в наклоне сидя с суперсетом"}
		]
	},
	"triceps": {
		"beginner": [
			{"name": "Разгибания рук с гантелью", "video_url": "https://youtu.be/triceps_beginner_1", "description": "Разгибания рук с гантелью из-за головы"},
			{"name": "Отжимания от скамьи", "video_url": "https://youtu.be/triceps_beginner_2", "description": "Отжимания от скамьи сзади"},
			{"name": "Разгибания рук с резинкой", "video_url": "https://youtu.be/triceps_beginner_3", "description": "Разгибания рук с резиновой лентой"},
			{"name": "Разгибания рук на блоке", "video_url": "https://youtu.be/triceps_beginner_4", "description": "Разгибания рук на верхнем блоке"},
			{"name": "Разгибания рук с гантелями лежа", "video_url": "https://youtu.be/triceps_beginner_5", "description": "Разгибания рук с гантелями лежа"},
			{"name": "Разгибания рук с одной гантелью", "video_url": "https://youtu.be/triceps_beginner_6", "description": "Разгибания рук с одной гантелью"},
			{"name": "Разгибания рук с резинкой стоя", "video_url": "https://youtu.be/triceps_beginner_7", "description": "Разгибания рук с резинкой стоя"},
			{"name": "Разгибания рук на нижнем блоке", "video_url": "https://youtu.be/triceps_beginner_8", "description": "Разгибания рук на нижнем блоке"},
			{"name": "Разгибания рук с гантелями сидя", "video_url": "https://youtu.be/triceps_beginner_9", "description": "Разгибания рук с гантелями сидя"},
			{"name": "Разгибания рук с гантелями в наклоне", "video_url": "https://youtu.be/triceps_beginner_10", "description": "Разгибания рук с гантелями в наклоне"}
		],
		"novice": [
			{"name": "Разгибания рук со штангой", "video_url": "https://youtu.be/triceps_novice_1", "description": "Разгибания рук со штангой из-за головы"},
			{"name": "Отжимания на брусьях", "video_url": "https://youtu.be/triceps_novice_2", "description": "Отжимания на брусьях"},
			{"name": "Разгибания рук с гантелями с пронацией", "video_url": "https://youtu.be/triceps_novice_3", "description": "Разгибания рук с поворотом кисти"},
			{"name": "Разгибания рук на скамье Скотта", "video_url": "https://youtu.be/triceps_novice_4", "description": "Разгибания рук на скамье Скотта"},
			{"name": "Концентрированные разгибания", "video_url": "https://youtu.be/triceps_novice_5", "description": "Концентрированные разгибания рук"},
			{"name": "Разгибания рук с гантелями лежа с паузой", "video_url": "https://youtu.be/triceps_novice_6", "description": "Разгибания рук с гантелями лежа с паузой"},
			{"name": "Разгибания рук на верхнем блоке с паузой", "video_url": "https://youtu.be/triceps_novice_7", "description": "Разгибания рук на верхнем блоке с паузой"},
			{"name": "Разгибания рук с гантелями попеременно", "video_url": "https://youtu.be/triceps_novice_8", "description": "Разгибания рук с гантелями попеременно"},
			{"name": "Разгибания рук с резинкой сидя", "video_url": "https://youtu.be/triceps_novice_9", "description": "Разгибания рук с резинкой сидя"},
			{"name": "Разгибания рук с гантелями в наклоне сидя", "video_url": "https://youtu.be/triceps_novice_10", "description": "Разгибания рук с гантелями в наклоне сидя"}
		],
		"advanced": [
			{"name": "Разгибания рук со штангой с паузой", "video_url": "https://youtu.be/triceps_advanced_1", "description": "Разгибания рук со штангой с паузой"},
			{"name": "Отжимания на брусьях с весом", "video_url": "https://youtu.be/triceps_advanced_2", "description": "Отжимания на брусьях с дополнительным весом"},
			{"name": "Разгибания рук с гантелями с пронацией и паузой", "video_url": "https://youtu.be/triceps_advanced_3", "description": "Разгибания рук с поворотом и паузой"},
			{"name": "Разгибания рук на скамье Скотта с паузой", "video_url": "https://youtu.be/triceps_advanced_4", "description": "Разгибания рук на скамье Скотта с паузой"},
			{"name": "Концентрированные разгибания с паузой", "video_url": "https://youtu.be/triceps_advanced_5", "description": "Концентрированные разгибания с паузой"},
			{"name": "Разгибания рук с гантелями лежа с паузой", "video_url": "https://youtu.be/triceps_advanced_6", "description": "Разгибания рук с гантелями лежа с паузой"},
			{"name": "Разгибания рук на верхнем блоке с паузой", "video_url": "https://youtu.be/triceps_advanced_7", "description": "Разгибания рук на верхнем блоке с паузой"},
			{"name": "Разгибания рук с гантелями попеременно с паузой", "video_url": "https://youtu.be/triceps_advanced_8", "description": "Разгибания рук с гантелями попеременно с паузой"},
			{"name": "Разгибания рук с резинкой сидя с паузой", "video_url": "https://youtu.be/triceps_advanced_9", "description": "Разгибания рук с резинкой сидя с паузой"},
			{"name": "Разгибания рук с гантелями в наклоне сидя с паузой", "video_url": "https://youtu.be/triceps_advanced_10", "description": "Разгибания рук с гантелями в наклоне сидя с паузой"},
			{"name": "Разгибания рук со штангой с дроп-сетом", "video_url": "https://youtu.be/triceps_advanced_11", "description": "Разгибания рук со штангой с дроп-сетом"},
			{"name": "Отжимания на брусьях с дроп-сетом", "video_url": "https://youtu.be/triceps_advanced_12", "description": "Отжимания на брусьях с дроп-сетом"},
			{"name": "Разгибания рук с гантелями с пронацией и дроп-сетом", "video_url": "https://youtu.be/triceps_advanced_13", "description": "Разгибания рук с поворотом и дроп-сетом"},
			{"name": "Разгибания рук на скамье Скотта с дроп-сетом", "video_url": "https://youtu.be/triceps_advanced_14", "description": "Разгибания рук на скамье Скотта с дроп-сетом"},
			{"name": "Концентрированные разгибания с дроп-сетом", "video_url": "https://youtu.be/triceps_advanced_15", "description": "Концентрированные разгибания с дроп-сетом"}
		],
		"pro": [
			{"name": "Разгибания рук со штангой с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_1", "description": "Разгибания рук со штангой с дроп-сетом и паузами"},
			{"name": "Отжимания на брусьях с большим весом", "video_url": "https://youtu.be/triceps_pro_2", "description": "Отжимания на брусьях с большим дополнительным весом"},
			{"name": "Разгибания рук с гантелями с пронацией и дроп-сетом", "video_url": "https://youtu.be/triceps_pro_3", "description": "Разгибания рук с поворотом и дроп-сетом"},
			{"name": "Разгибания рук на скамье Скотта с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_4", "description": "Разгибания рук на скамье Скотта с дроп-сетом"},
			{"name": "Концентрированные разгибания с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_5", "description": "Концентрированные разгибания с дроп-сетом"},
			{"name": "Разгибания рук с гантелями лежа с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_6", "description": "Разгибания рук с гантелями лежа с дроп-сетом"},
			{"name": "Разгибания рук на верхнем блоке с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_7", "description": "Разгибания рук на верхнем блоке с дроп-сетом"},
			{"name": "Разгибания рук с гантелями попеременно с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_8", "description": "Разгибания рук с гантелями попеременно с дроп-сетом"},
			{"name": "Разгибания рук с резинкой сидя с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_9", "description": "Разгибания рук с резинкой сидя с дроп-сетом"},
			{"name": "Разгибания рук с гантелями в наклоне сидя с дроп-сетом", "video_url": "https://youtu.be/triceps_pro_10", "description": "Разгибания рук с гантелями в наклоне сидя с дроп-сетом"},
			{"name": "Разгибания рук со штангой с суперсетом", "video_url": "https://youtu.be/triceps_pro_11", "description": "Разгибания рук со штангой с суперсетом"},
			{"name": "Отжимания на брусьях с суперсетом", "video_url": "https://youtu.be/triceps_pro_12", "description": "Отжимания на брусьях с суперсетом"},
			{"name": "Разгибания рук с гантелями с пронацией и суперсетом", "video_url": "https://youtu.be/triceps_pro_13", "description": "Разгибания рук с поворотом и суперсетом"},
			{"name": "Разгибания рук на скамье Скотта с суперсетом", "video_url": "https://youtu.be/triceps_pro_14", "description": "Разгибания рук на скамье Скотта с суперсетом"},
			{"name": "Концентрированные разгибания с суперсетом", "video_url": "https://youtu.be/triceps_pro_15", "description": "Концентрированные разгибания с суперсетом"},
			{"name": "Разгибания рук с гантелями лежа с суперсетом", "video_url": "https://youtu.be/triceps_pro_16", "description": "Разгибания рук с гантелями лежа с суперсетом"},
			{"name": "Разгибания рук на верхнем блоке с суперсетом", "video_url": "https://youtu.be/triceps_pro_17", "description": "Разгибания рук на верхнем блоке с суперсетом"},
			{"name": "Разгибания рук с гантелями попеременно с суперсетом", "video_url": "https://youtu.be/triceps_pro_18", "description": "Разгибания рук с гантелями попеременно с суперсетом"},
			{"name": "Разгибания рук с резинкой сидя с суперсетом", "video_url": "https://youtu.be/triceps_pro_19", "description": "Разгибания рук с резинкой сидя с суперсетом"},
			{"name": "Разгибания рук с гантелями в наклоне сидя с суперсетом", "video_url": "https://youtu.be/triceps_pro_20", "description": "Разгибания рук с гантелями в наклоне сидя с суперсетом"}
		]
	},
	"shoulders": {
		"beginner": [
			{"name": "Жим гантелей стоя", "video_url": "https://youtu.be/shoulders_beginner_1", "description": "Жим гантелей стоя"},
			{"name": "Разведение гантелей в стороны", "video_url": "https://youtu.be/shoulders_beginner_2", "description": "Разведение гантелей в стороны стоя"},
			{"name": "Разведение гантелей в наклоне", "video_url": "https://youtu.be/shoulders_beginner_3", "description": "Разведение гантелей в наклоне"},
			{"name": "Жим штанги стоя", "video_url": "https://youtu.be/shoulders_beginner_4", "description": "Жим штанги стоя"},
			{"name": "Разведение гантелей лежа", "video_url": "https://youtu.be/shoulders_beginner_5", "description": "Разведение гантелей лежа на животе"},
			{"name": "Жим гантелей сидя", "video_url": "https://youtu.be/shoulders_beginner_6", "description": "Жим гантелей сидя"},
			{"name": "Разведение гантелей с резинкой", "video_url": "https://youtu.be/shoulders_beginner_7", "description": "Разведение гантелей с резиновой лентой"},
			{"name": "Жим в тренажере", "video_url": "https://youtu.be/shoulders_beginner_8", "description": "Жим в тренажере для плеч"},
			{"name": "Разведение гантелей одной рукой", "video_url": "https://youtu.be/shoulders_beginner_9", "description": "Разведение гантелей одной рукой"},
			{"name": "Жим гантелей с резинкой", "video_url": "https://youtu.be/shoulders_beginner_10", "description": "Жим гантелей с резиновой лентой"}
		],
		"novice": [
			{"name": "Жим гантелей стоя с паузой", "video_url": "https://youtu.be/shoulders_novice_1", "description": "Жим гантелей стоя с паузой"},
			{"name": "Разведение гантелей в стороны с паузой", "video_url": "https://youtu.be/shoulders_novice_2", "description": "Разведение гантелей в стороны стоя с паузой"},
			{"name": "Разведение гантелей в наклоне с паузой", "video_url": "https://youtu.be/shoulders_novice_3", "description": "Разведение гантелей в наклоне с паузой"},
			{"name": "Жим штанги стоя с паузой", "video_url": "https://youtu.be/shoulders_novice_4", "description": "Жим штанги стоя с паузой"},
			{"name": "Разведение гантелей лежа с паузой", "video_url": "https://youtu.be/shoulders_novice_5", "description": "Разведение гантелей лежа на животе с паузой"},
			{"name": "Жим гантелей сидя с паузой", "video_url": "https://youtu.be/shoulders_novice_6", "description": "Жим гантелей сидя с паузой"},
			{"name": "Разведение гантелей с резинкой с паузой", "video_url": "https://youtu.be/shoulders_novice_7", "description": "Разведение гантелей с резиновой лентой с паузой"},
			{"name": "Жим в тренажере с паузой", "video_url": "https://youtu.be/shoulders_novice_8", "description": "Жим в тренажере для плеч с паузой"},
			{"name": "Разведение гантелей одной рукой с паузой", "video_url": "https://youtu.be/shoulders_novice_9", "description": "Разведение гантелей одной рукой с паузой"},
			{"name": "Жим гантелей с резинкой с паузой", "video_url": "https://youtu.be/shoulders_novice_10", "description": "Жим гантелей с резиновой лентой с паузой"}
		],
		"advanced": [
			{"name": "Жим гантелей стоя с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_1", "description": "Жим гантелей стоя с дроп-сетом"},
			{"name": "Разведение гантелей в стороны с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_2", "description": "Разведение гантелей в стороны стоя с дроп-сетом"},
			{"name": "Разведение гантелей в наклоне с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_3", "description": "Разведение гантелей в наклоне с дроп-сетом"},
			{"name": "Жим штанги стоя с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_4", "description": "Жим штанги стоя с дроп-сетом"},
			{"name": "Разведение гантелей лежа с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_5", "description": "Разведение гантелей лежа на животе с дроп-сетом"},
			{"name": "Жим гантелей сидя с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_6", "description": "Жим гантелей сидя с дроп-сетом"},
			{"name": "Разведение гантелей с резинкой с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_7", "description": "Разведение гантелей с резиновой лентой с дроп-сетом"},
			{"name": "Жим в тренажере с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_8", "description": "Жим в тренажере для плеч с дроп-сетом"},
			{"name": "Разведение гантелей одной рукой с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_9", "description": "Разведение гантелей одной рукой с дроп-сетом"},
			{"name": "Жим гантелей с резинкой с дроп-сетом", "video_url": "https://youtu.be/shoulders_advanced_10", "description": "Жим гантелей с резиновой лентой с дроп-сетом"},
			{"name": "Жим гантелей стоя с суперсетом", "video_url": "https://youtu.be/shoulders_advanced_11", "description": "Жим гантелей стоя с суперсетом"},
			{"name": "Разведение гантелей в стороны с суперсетом", "video_url": "https://youtu.be/shoulders_advanced_12", "description": "Разведение гантелей в стороны стоя с суперсетом"},
			{"name": "Разведение гантелей в наклоне с суперсетом", "video_url": "https://youtu.be/shoulders_advanced_13", "description": "Разведение гантелей в наклоне с суперсетом"},
			{"name": "Жим штанги стоя с суперсетом", "video_url": "https://youtu.be/shoulders_advanced_14", "description": "Жим штанги стоя с суперсетом"},
			{"name": "Разведение гантелей лежа с суперсетом", "video_url": "https://youtu.be/shoulders_advanced_15", "description": "Разведение гантелей лежа на животе с суперсетом"}
		],
		"pro": [
			{"name": "Жим гантелей стоя с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_1", "description": "Жим гантелей стоя с дроп-сетом и паузами"},
			{"name": "Разведение гантелей в стороны с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_2", "description": "Разведение гантелей в стороны стоя с дроп-сетом"},
			{"name": "Разведение гантелей в наклоне с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_3", "description": "Разведение гантелей в наклоне с дроп-сетом"},
			{"name": "Жим штанги стоя с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_4", "description": "Жим штанги стоя с дроп-сетом"},
			{"name": "Разведение гантелей лежа с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_5", "description": "Разведение гантелей лежа на животе с дроп-сетом"},
			{"name": "Жим гантелей сидя с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_6", "description": "Жим гантелей сидя с дроп-сетом"},
			{"name": "Разведение гантелей с резинкой с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_7", "description": "Разведение гантелей с резиновой лентой с дроп-сетом"},
			{"name": "Жим в тренажере с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_8", "description": "Жим в тренажере для плеч с дроп-сетом"},
			{"name": "Разведение гантелей одной рукой с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_9", "description": "Разведение гантелей одной рукой с дроп-сетом"},
			{"name": "Жим гантелей с резинкой с дроп-сетом", "video_url": "https://youtu.be/shoulders_pro_10", "description": "Жим гантелей с резиновой лентой с дроп-сетом"},
			{"name": "Жим гантелей стоя с суперсетом", "video_url": "https://youtu.be/shoulders_pro_11", "description": "Жим гантелей стоя с суперсетом"},
			{"name": "Разведение гантелей в стороны с суперсетом", "video_url": "https://youtu.be/shoulders_pro_12", "description": "Разведение гантелей в стороны стоя с суперсетом"},
			{"name": "Разведение гантелей в наклоне с суперсетом", "video_url": "https://youtu.be/shoulders_pro_13", "description": "Разведение гантелей в наклоне с суперсетом"},
			{"name": "Жим штанги стоя с суперсетом", "video_url": "https://youtu.be/shoulders_pro_14", "description": "Жим штанги стоя с суперсетом"},
			{"name": "Разведение гантелей лежа с суперсетом", "video_url": "https://youtu.be/shoulders_pro_15", "description": "Разведение гантелей лежа на животе с суперсетом"},
			{"name": "Жим гантелей сидя с суперсетом", "video_url": "https://youtu.be/shoulders_pro_16", "description": "Жим гантелей сидя с суперсетом"},
			{"name": "Разведение гантелей с резинкой с суперсетом", "video_url": "https://youtu.be/shoulders_pro_17", "description": "Разведение гантелей с резиновой лентой с суперсетом"},
			{"name": "Жим в тренажере с суперсетом", "video_url": "https://youtu.be/shoulders_pro_18", "description": "Жим в тренажере для плеч с суперсетом"},
			{"name": "Разведение гантелей одной рукой с суперсетом", "video_url": "https://youtu.be/shoulders_pro_19", "description": "Разведение гантелей одной рукой с суперсетом"},
			{"name": "Жим гантелей с резинкой с суперсетом", "video_url": "https://youtu.be/shoulders_pro_20", "description": "Жим гантелей с резиновой лентой с суперсетом"}
		]
	},
	"legs": {
		"beginner": [
			{"name": "Приседания с гантелями", "video_url": "https://youtu.be/legs_beginner_1", "description": "Приседания с гантелями"},
			{"name": "Выпады с гантелями", "video_url": "https://youtu.be/legs_beginner_2", "description": "Выпады с гантелями"},
			{"name": "Жим ногами", "video_url": "https://youtu.be/legs_beginner_3", "description": "Жим ногами в тренажере"},
			{"name": "Разгибания ног", "video_url": "https://youtu.be/legs_beginner_4", "description": "Разгибания ног в тренажере"},
			{"name": "Сгибания ног", "video_url": "https://youtu.be/legs_beginner_5", "description": "Сгибания ног в тренажере"},
			{"name": "Подъемы на носки", "video_url": "https://youtu.be/legs_beginner_6", "description": "Подъемы на носки стоя"},
			{"name": "Приседания с резинкой", "video_url": "https://youtu.be/legs_beginner_7", "description": "Приседания с резиновой лентой"},
			{"name": "Выпады с резинкой", "video_url": "https://youtu.be/legs_beginner_8", "description": "Выпады с резиновой лентой"},
			{"name": "Приседания с одной ногой", "video_url": "https://youtu.be/legs_beginner_9", "description": "Приседания на одной ноге"},
			{"name": "Подъемы на носки сидя", "video_url": "https://youtu.be/legs_beginner_10", "description": "Подъемы на носки сидя"}
		],
		"novice": [
			{"name": "Приседания со штангой", "video_url": "https://youtu.be/legs_novice_1", "description": "Приседания со штангой"},
			{"name": "Выпады со штангой", "video_url": "https://youtu.be/legs_novice_2", "description": "Выпады со штангой"},
			{"name": "Жим ногами с паузой", "video_url": "https://youtu.be/legs_novice_3", "description": "Жим ногами в тренажере с паузой"},
			{"name": "Разгибания ног с паузой", "video_url": "https://youtu.be/legs_novice_4", "description": "Разгибания ног в тренажере с паузой"},
			{"name": "Сгибания ног с паузой", "video_url": "https://youtu.be/legs_novice_5", "description": "Сгибания ног в тренажере с паузой"},
			{"name": "Подъемы на носки с паузой", "video_url": "https://youtu.be/legs_novice_6", "description": "Подъемы на носки стоя с паузой"},
			{"name": "Приседания с резинкой с паузой", "video_url": "https://youtu.be/legs_novice_7", "description": "Приседания с резиновой лентой с паузой"},
			{"name": "Выпады с резинкой с паузой", "video_url": "https://youtu.be/legs_novice_8", "description": "Выпады с резиновой лентой с паузой"},
			{"name": "Приседания с одной ногой с паузой", "video_url": "https://youtu.be/legs_novice_9", "description": "Приседания на одной ноге с паузой"},
			{"name": "Подъемы на носки сидя с паузой", "video_url": "https://youtu.be/legs_novice_10", "description": "Подъемы на носки сидя с паузой"}
		],
		"advanced": [
			{"name": "Приседания со штангой с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_1", "description": "Приседания со штангой с дроп-сетом"},
			{"name": "Выпады со штангой с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_2", "description": "Выпады со штангой с дроп-сетом"},
			{"name": "Жим ногами с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_3", "description": "Жим ногами в тренажере с дроп-сетом"},
			{"name": "Разгибания ног с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_4", "description": "Разгибания ног в тренажере с дроп-сетом"},
			{"name": "Сгибания ног с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_5", "description": "Сгибания ног в тренажере с дроп-сетом"},
			{"name": "Подъемы на носки с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_6", "description": "Подъемы на носки стоя с дроп-сетом"},
			{"name": "Приседания с резинкой с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_7", "description": "Приседания с резиновой лентой с дроп-сетом"},
			{"name": "Выпады с резинкой с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_8", "description": "Выпады с резиновой лентой с дроп-сетом"},
			{"name": "Приседания с одной ногой с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_9", "description": "Приседания на одной ноге с дроп-сетом"},
			{"name": "Подъемы на носки сидя с дроп-сетом", "video_url": "https://youtu.be/legs_advanced_10", "description": "Подъемы на носки сидя с дроп-сетом"},
			{"name": "Приседания со штангой с суперсетом", "video_url": "https://youtu.be/legs_advanced_11", "description": "Приседания со штангой с суперсетом"},
			{"name": "Выпады со штангой с суперсетом", "video_url": "https://youtu.be/legs_advanced_12", "description": "Выпады со штангой с суперсетом"},
			{"name": "Жим ногами с суперсетом", "video_url": "https://youtu.be/legs_advanced_13", "description": "Жим ногами в тренажере с суперсетом"},
			{"name": "Разгибания ног с суперсетом", "video_url": "https://youtu.be/legs_advanced_14", "description": "Разгибания ног в тренажере с суперсетом"},
			{"name": "Сгибания ног с суперсетом", "video_url": "https://youtu.be/legs_advanced_15", "description": "Сгибания ног в тренажере с суперсетом"}
		],
		"pro": [
			{"name": "Приседания со штангой с дроп-сетом", "video_url": "https://youtu.be/legs_pro_1", "description": "Приседания со штангой с дроп-сетом и паузами"},
			{"name": "Выпады со штангой с дроп-сетом", "video_url": "https://youtu.be/legs_pro_2", "description": "Выпады со штангой с дроп-сетом"},
			{"name": "Жим ногами с дроп-сетом", "video_url": "https://youtu.be/legs_pro_3", "description": "Жим ногами в тренажере с дроп-сетом"},
			{"name": "Разгибания ног с дроп-сетом", "video_url": "https://youtu.be/legs_pro_4", "description": "Разгибания ног в тренажере с дроп-сетом"},
			{"name": "Сгибания ног с дроп-сетом", "video_url": "https://youtu.be/legs_pro_5", "description": "Сгибания ног в тренажере с дроп-сетом"},
			{"name": "Подъемы на носки с дроп-сетом", "video_url": "https://youtu.be/legs_pro_6", "description": "Подъемы на носки стоя с дроп-сетом"},
			{"name": "Приседания с резинкой с дроп-сетом", "video_url": "https://youtu.be/legs_pro_7", "description": "Приседания с резиновой лентой с дроп-сетом"},
			{"name": "Выпады с резинкой с дроп-сетом", "video_url": "https://youtu.be/legs_pro_8", "description": "Выпады с резиновой лентой с дроп-сетом"},
			{"name": "Приседания с одной ногой с дроп-сетом", "video_url": "https://youtu.be/legs_pro_9", "description": "Приседания на одной ноге с дроп-сетом"},
			{"name": "Подъемы на носки сидя с дроп-сетом", "video_url": "https://youtu.be/legs_pro_10", "description": "Подъемы на носки сидя с дроп-сетом"},
			{"name": "Приседания со штангой с суперсетом", "video_url": "https://youtu.be/legs_pro_11", "description": "Приседания со штангой с суперсетом"},
			{"name": "Выпады со штангой с суперсетом", "video_url": "https://youtu.be/legs_pro_12", "description": "Выпады со штангой с суперсетом"},
			{"name": "Жим ногами с суперсетом", "video_url": "https://youtu.be/legs_pro_13", "description": "Жим ногами в тренажере с суперсетом"},
			{"name": "Разгибания ног с суперсетом", "video_url": "https://youtu.be/legs_pro_14", "description": "Разгибания ног в тренажере с суперсетом"},
			{"name": "Сгибания ног с суперсетом", "video_url": "https://youtu.be/legs_pro_15", "description": "Сгибания ног в тренажере с суперсетом"},
			{"name": "Подъемы на носки с суперсетом", "video_url": "https://youtu.be/legs_pro_16", "description": "Подъемы на носки стоя с суперсетом"},
			{"name": "Приседания с резинкой с суперсетом", "video_url": "https://youtu.be/legs_pro_17", "description": "Приседания с резиновой лентой с суперсетом"},
			{"name": "Выпады с резинкой с суперсетом", "video_url": "https://youtu.be/legs_pro_18", "description": "Выпады с резиновой лентой с суперсетом"},
			{"name": "Приседания с одной ногой с суперсетом", "video_url": "https://youtu.be/legs_pro_19", "description": "Приседания на одной ноге с суперсетом"},
			{"name": "Подъемы на носки сидя с суперсетом", "video_url": "https://youtu.be/legs_pro_20", "description": "Подъемы на носки сидя с суперсетом"}
		]
	},
	"abs": {
		"beginner": [
			{"name": "Скручивания", "video_url": "https://youtu.be/abs_beginner_1", "description": "Классические скручивания"},
			{"name": "Планка", "video_url": "https://youtu.be/abs_beginner_2", "description": "Планка на локтях"},
			{"name": "Подъемы ног лежа", "video_url": "https://youtu.be/abs_beginner_3", "description": "Подъемы ног лежа на спине"},
			{"name": "Боковая планка", "video_url": "https://youtu.be/abs_beginner_4", "description": "Боковая планка"},
			{"name": "Скручивания с поворотом", "video_url": "https://youtu.be/abs_beginner_5", "description": "Скручивания с поворотом корпуса"},
			{"name": "Планка с подъемом ноги", "video_url": "https://youtu.be/abs_beginner_6", "description": "Планка с подъемом ноги"},
			{"name": "Подъемы ног сидя", "video_url": "https://youtu.be/abs_beginner_7", "description": "Подъемы ног сидя на полу"},
			{"name": "Скручивания с резинкой", "video_url": "https://youtu.be/abs_beginner_8", "description": "Скручивания с резиновой лентой"},
			{"name": "Планка с подъемом руки", "video_url": "https://youtu.be/abs_beginner_9", "description": "Планка с подъемом руки"},
			{"name": "Подъемы ног на турнике", "video_url": "https://youtu.be/abs_beginner_10", "description": "Подъемы ног на турнике"}
		],
		"novice": [
			{"name": "Скручивания с паузой", "video_url": "https://youtu.be/abs_novice_1", "description": "Скручивания с паузой в верхней точке"},
			{"name": "Планка с паузой", "video_url": "https://youtu.be/abs_novice_2", "description": "Планка на локтях с паузой"},
			{"name": "Подъемы ног лежа с паузой", "video_url": "https://youtu.be/abs_novice_3", "description": "Подъемы ног лежа на спине с паузой"},
			{"name": "Боковая планка с паузой", "video_url": "https://youtu.be/abs_novice_4", "description": "Боковая планка с паузой"},
			{"name": "Скручивания с поворотом и паузой", "video_url": "https://youtu.be/abs_novice_5", "description": "Скручивания с поворотом корпуса и паузой"},
			{"name": "Планка с подъемом ноги и паузой", "video_url": "https://youtu.be/abs_novice_6", "description": "Планка с подъемом ноги и паузой"},
			{"name": "Подъемы ног сидя с паузой", "video_url": "https://youtu.be/abs_novice_7", "description": "Подъемы ног сидя на полу с паузой"},
			{"name": "Скручивания с резинкой и паузой", "video_url": "https://youtu.be/abs_novice_8", "description": "Скручивания с резиновой лентой и паузой"},
			{"name": "Планка с подъемом руки и паузой", "video_url": "https://youtu.be/abs_novice_9", "description": "Планка с подъемом руки и паузой"},
			{"name": "Подъемы ног на турнике с паузой", "video_url": "https://youtu.be/abs_novice_10", "description": "Подъемы ног на турнике с паузой"}
		],
		"advanced": [
			{"name": "Скручивания с дроп-сетом", "video_url": "https://youtu.be/abs_advanced_1", "description": "Скручивания с дроп-сетом"},
			{"name": "Планка с дроп-сетом", "video_url": "https://youtu.be/abs_advanced_2", "description": "Планка на локтях с дроп-сетом"},
			{"name": "Подъемы ног лежа с дроп-сетом", "video_url": "https://youtu.be/abs_advanced_3", "description": "Подъемы ног лежа на спине с дроп-сетом"},
			{"name": "Боковая планка с дроп-сетом", "video_url": "https://youtu.be/abs_advanced_4", "description": "Боковая планка с дроп-сетом"},
			{"name": "Скручивания с поворотом и дроп-сетом", "video_url": "https://youtu.be/abs_advanced_5", "description": "Скручивания с поворотом корпуса и дроп-сетом"},
			{"name": "Планка с подъемом ноги и дроп-сетом", "video_url": "https://youtu.be/abs_advanced_6", "description": "Планка с подъемом ноги и дроп-сетом"},
			{"name": "Подъемы ног сидя с дроп-сетом", "video_url": "https://youtu.be/abs_advanced_7", "description": "Подъемы ног сидя на полу с дроп-сетом"},
			{"name": "Скручивания с резинкой и дроп-сетом", "video_url": "https://youtu.be/abs_advanced_8", "description": "Скручивания с резиновой лентой и дроп-сетом"},
			{"name": "Планка с подъемом руки и дроп-сетом", "video_url": "https://youtu.be/abs_advanced_9", "description": "Планка с подъемом руки и дроп-сетом"},
			{"name": "Подъемы ног на турнике с дроп-сетом", "video_url": "https://youtu.be/abs_advanced_10", "description": "Подъемы ног на турнике с дроп-сетом"},
			{"name": "Скручивания с суперсетом", "video_url": "https://youtu.be/abs_advanced_11", "description": "Скручивания с суперсетом"},
			{"name": "Планка с суперсетом", "video_url": "https://youtu.be/abs_advanced_12", "description": "Планка на локтях с суперсетом"},
			{"name": "Подъемы ног лежа с суперсетом", "video_url": "https://youtu.be/abs_advanced_13", "description": "Подъемы ног лежа на спине с суперсетом"},
			{"name": "Боковая планка с суперсетом", "video_url": "https://youtu.be/abs_advanced_14", "description": "Боковая планка с суперсетом"},
			{"name": "Скручивания с поворотом и суперсетом", "video_url": "https://youtu.be/abs_advanced_15", "description": "Скручивания с поворотом корпуса и суперсетом"}
		],
		"pro": [
			{"name": "Скручивания с дроп-сетом", "video_url": "https://youtu.be/abs_pro_1", "description": "Скручивания с дроп-сетом и паузами"},
			{"name": "Планка с дроп-сетом", "video_url": "https://youtu.be/abs_pro_2", "description": "Планка на локтях с дроп-сетом"},
			{"name": "Подъемы ног лежа с дроп-сетом", "video_url": "https://youtu.be/abs_pro_3", "description": "Подъемы ног лежа на спине с дроп-сетом"},
			{"name": "Боковая планка с дроп-сетом", "video_url": "https://youtu.be/abs_pro_4", "description": "Боковая планка с дроп-сетом"},
			{"name": "Скручивания с поворотом и дроп-сетом", "video_url": "https://youtu.be/abs_pro_5", "description": "Скручивания с поворотом корпуса и дроп-сетом"},
			{"name": "Планка с подъемом ноги и дроп-сетом", "video_url": "https://youtu.be/abs_pro_6", "description": "Планка с подъемом ноги и дроп-сетом"},
			{"name": "Подъемы ног сидя с дроп-сетом", "video_url": "https://youtu.be/abs_pro_7", "description": "Подъемы ног сидя на полу с дроп-сетом"},
			{"name": "Скручивания с резинкой и дроп-сетом", "video_url": "https://youtu.be/abs_pro_8", "description": "Скручивания с резиновой лентой и дроп-сетом"},
			{"name": "Планка с подъемом руки и дроп-сетом", "video_url": "https://youtu.be/abs_pro_9", "description": "Планка с подъемом руки и дроп-сетом"},
			{"name": "Подъемы ног на турнике с дроп-сетом", "video_url": "https://youtu.be/abs_pro_10", "description": "Подъемы ног на турнике с дроп-сетом"},
			{"name": "Скручивания с суперсетом", "video_url": "https://youtu.be/abs_pro_11", "description": "Скручивания с суперсетом"},
			{"name": "Планка с суперсетом", "video_url": "https://youtu.be/abs_pro_12", "description": "Планка на локтях с суперсетом"},
			{"name": "Подъемы ног лежа с суперсетом", "video_url": "https://youtu.be/abs_pro_13", "description": "Подъемы ног лежа на спине с суперсетом"},
			{"name": "Боковая планка с суперсетом", "video_url": "https://youtu.be/abs_pro_14", "description": "Боковая планка с суперсетом"},
			{"name": "Скручивания с поворотом и суперсетом", "video_url": "https://youtu.be/abs_pro_15", "description": "Скручивания с поворотом корпуса и суперсетом"},
			{"name": "Планка с подъемом ноги и суперсетом", "video_url": "https://youtu.be/abs_pro_16", "description": "Планка с подъемом ноги и суперсетом"},
			{"name": "Подъемы ног сидя с суперсетом", "video_url": "https://youtu.be/abs_pro_17", "description": "Подъемы ног сидя на полу с суперсетом"},
			{"name": "Скручивания с резинкой и суперсетом", "video_url": "https://youtu.be/abs_pro_18", "description": "Скручивания с резиновой лентой и суперсетом"},
			{"name": "Планка с подъемом руки и суперсетом", "video_url": "https://youtu.be/abs_pro_19", "description": "Планка с подъемом руки и суперсетом"},
			{"name": "Подъемы ног на турнике с суперсетом", "video_url": "https://youtu.be/abs_pro_20", "description": "Подъемы ног на турнике с суперсетом"}
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