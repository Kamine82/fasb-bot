import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# 🔐 Токен из переменных окружения Railway
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== ТОЧНЫЕ ДАННЫЕ КАК НА ВАШЕМ САЙТЕ ==========
COATINGS = [
    {
        "id": 1,
        "name": "Окрасочное полимерное покрытие для лёгких нагрузок, толщина ~0,5мм",
        "layers": [
            {"name": "Грунт", "material": "Эпоксидный высокопроникающий грунт", "consumption": 0.5, "package": 20},
            {"name": "Основной слой", "material": "Базовый наливной слой", "consumption": 0.6, "package": 25},
            {"name": "Финишное покрытие", "material": "Матовый УФ стойкий прозрачный лак", "consumption": 0.2, "package": 10, "optional": True}
        ]
    },
    {
        "id": 2,
        "name": "Наливное эпоксидное гладкое покрытие для средних нагрузок, толщина ~2мм",
        "layers": [
            {"name": "Грунт", "material": "Эпоксидный высокопроникающий грунт", "consumption": 0.5, "package": 20},
            {"name": "Присыпка", "material": "Прокаленный минеральный заполнитель фр. 0,1-0,4", "consumption": 1.5, "package": 25},
            {"name": "Основной слой", "material": "Базовый наливной слой", "consumption": 2.4, "package": 25},
            {"name": "Финишное покрытие", "material": "Матовый УФ стойкий прозрачный лак", "consumption": 0.2, "package": 10, "optional": True}
        ]
    },
    {
        "id": 3,
        "name": "Антискользящее эпоксидное покрытие для паркинга толщиной ~3,5-4мм",
        "layers": [
            {"name": "Грунт", "material": "Эпоксидный высокопроникающий грунт", "consumption": 0.45, "package": 25},
            {"name": "Присыпка", "material": "Прокаленный минеральный заполнитель фр. 0,4-0,8", "consumption": 8, "package": 25},
            {"name": "Основной слой", "material": "Базовый наливной слой", "consumption": 2.40, "package": 25},
            {"name": "Финишное покрытие", "material": "Матовый УФ стойкий прозрачный лак", "consumption": 0.12, "package": 10, "optional": True}
        ]
    },
    {
        "id": 4,
        "name": "Декоративное покрытие 'чипсовый ковёр' толщиной ~3,5-4мм",
        "layers": [
            {"name": "Грунт", "material": "Эпоксидный высокопроникающий грунт", "consumption": 0.6, "package": 25},
            {"name": "Основной слой", "material": "Базовый наливной слой", "consumption": 2, "package": 25},
            {"name": "Микс чипсов", "material": "Специально подобранный микс полимерных флоков", "consumption": 0.2, "package": 1},
            {"name": "Укрывающий прозрачный слой", "material": "Матовый УФ стойкий прозрачный лак", "consumption": 1, "package": 10}
        ]
    },
    {
        "id": 5,
        "name": "Полиуретанцементное гладкое покрытие для пищевых производств толщиной ~4мм",
        "layers": [
            {"name": "Грунт", "material": "Специальный трёхкомпонентный полиуретанцементный грунт", "consumption": 0.6, "package": 12.0},
            {"name": "Адгезионная присыпка", "material": "Прокаленный минеральный заполнитель фр. 0,4-0,8", "consumption": 0.5, "package": 25},
            {"name": "Основной слой", "material": "Термохимстойкий трёхкомпонентный полиуретанцементный состав", "consumption": 8.5, "package": 40}
        ]
    },
    {
        "id": 6,
        "name": "Полиуретанцементное антискользящее покрытие для пищевых производств толщиной ~6мм",
        "layers": [
            {"name": "Грунт", "material": "Специальный трёхкомпонентный полиуретанцементный грунт", "consumption": 0.6, "package": 12.0},
            {"name": "Основной слой", "material": "Термохимстойкий трёхкомпонентный полиуретанцементный состав", "consumption": 8.5, "package": 40},
            {"name": "Засыпка 'под шубу'", "material": "Прокаленный минеральный заполнитель фр. 0,4-0,8", "consumption": 6, "package": 25},
            {"name": "Запечатывающий слой", "material": "Специальный оксаочный трёхкомпонентный состав", "consumption": 0.8, "package": 10.8}
        ]
    }
]

# Состояния диалога
CHOOSING, TYPING_AREA = range(2)

def format_weight(weight):
    """Форматирование веса упаковки"""
    return str(weight) if weight % 1 == 0 else f"{weight:.1f}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Команда /start"""
    # Создаем кнопки
    buttons = []
    for coating in COATINGS:
        short_name = coating["name"]
        if len(short_name) > 40:
            short_name = short_name[:37] + "..."
        buttons.append([f"{coating['id']}. {short_name}"])
    
    await update.message.reply_text(
        "🏗️ *Калькулятор расхода материалов для наливных полов*\n"
        "*Компания ФАСБ*\n\n"
        "✅ *Бесплатно, без регистрации, мгновенный расчет!*\n\n"
        "👇 *Выберите тип покрытия:*",
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return CHOOSING

async def choose_coating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора покрытия"""
    text = update.message.text
    try:
        coating_id = int(text.split(".")[0])
        for coating in COATINGS:
            if coating["id"] == coating_id:
                context.user_data["coating"] = coating
                await update.message.reply_text(
                    f"✅ *{coating['name']}*\n\n"
                    "📐 *Введите площадь покрытия в м²:*\n"
                    "Например: 100, 250.5, 75\n\n"
                    "_Можно использовать дробные числа_",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="Markdown"
                )
                return TYPING_AREA
    except:
        pass
    
    await update.message.reply_text("❌ Выберите вариант из списка!")
    return CHOOSING

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Расчет материалов"""
    try:
        area_text = update.message.text.replace(",", ".")
        area = float(area_text)
        
        if area <= 0:
            await update.message.reply_text("❌ Площадь должна быть больше 0!")
            return TYPING_AREA
        
        coating = context.user_data.get("coating", COATINGS[0])
        
        # Выполняем расчет как на сайте
        result = "🏗️ *РАСЧЕТ МАТЕРИАЛОВ*\n\n"
        result += f"*Тип покрытия:* {coating['name']}\n"
        result += f"*Площадь:* {area} м²\n\n"
        result += "*РАСХОД МАТЕРИАЛОВ:*\n\n"
        
        total_cost = 0
        
        for layer in coating["layers"]:
            # Расчет как в JavaScript
            total_kg = area * layer["consumption"]
            packages = (total_kg // layer["package"]) + (1 if total_kg % layer["package"] > 0 else 0)
            
            layer_name = layer["name"]
            if layer.get("optional"):
                layer_name += " (опция)"
            
            result += f"🔹 *{layer_name}*\n"
            result += f"   Материал: {layer['material']}\n"
            result += f"   Расход: {total_kg:.1f} кг\n"
            result += f"   Упаковок: {packages} шт.\n"
            result += f"   (фасовка по {format_weight(layer['package'])} кг)\n\n"
            
            # Примерная стоимость
            material_cost = total_kg * 350  # 350 руб/кг
            total_cost += material_cost
        
        result += "---\n"
        result += f"*Примерная стоимость материалов:* ~{total_cost:.0f} ₽\n\n"
        result += "📞 *Контакты ФАСБ:*\n"
        result += "+7 (981) 746-93-54\n"
        result += "fasb_ik@vk.com\n\n"
        result += "*Внимание:* Расчет предварительный. Для точного КП обратитесь к специалистам.\n"
        result += "_Данный расчет не является офертой._"
        
        await update.message.reply_text(result, parse_mode="Markdown")
        await update.message.reply_text("🔄 Новый расчет: /start")
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Введите число для площади!")
        return TYPING_AREA

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help"""
    help_text = """
📖 *Помощь по боту калькулятора ФАСБ*

*Команды:*
/start - начать новый расчет
/help - показать эту справку

*Как работает:*
1. Выберите один из 6 типов покрытий
2. Введите площадь помещения
3. Получите детальный расчет материалов

*Типы покрытий:*
1. Окрасочное полимерное (0.5мм)
2. Наливное эпоксидное (2мм)
3. Антискользящее для паркинга (4мм)
4. Декоративное "чипсовый ковёр" (4мм)
5. Полиуретанцементное гладкое (4мм)
6. Полиуретанцементное антискользящее (6мм)

*Контакты:*
📞 +7 (981) 746-93-54
✉️ fasb_ik@vk.com

✅ Бесплатный расчет от профессионалов!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена"""
    await update.message.reply_text(
        "Операция отменена. /start - начать заново",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ Ошибка: BOT_TOKEN не установлен!")
        print("\n" + "="*60)
        print("Добавьте BOT_TOKEN в Variables на Railway!")
        print("="*60)
        return
    print(f"bot{BOT_TOKEN}")
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Настраиваем диалог
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_coating)],
            TYPING_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("help", help_cmd)
        ]
    )
    
    # Добавляем обработчики
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_cmd))
    
    # Запускаем
    logger.info("🤖 Бот ФАСБ запущен на Railway!")
    print("\n" + "="*60)
    print("✅ FASB FLOOR CALCULATOR BOT")
    print("🤖 Ищите: @FasbFloorCalculator_bot")
    print("📱 Тестируйте в Telegram!")
    print("="*60)
    
    app.run_polling()

if __name__ == "__main__":
    main()
