import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# 🔐 Токен бота
BOT_TOKEN = "7634686364:AAHEqI61Ol3jT-yOesf51mqXxNqTbLchxX0"

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
    if isinstance(weight, int):
        return str(weight)
    elif weight.is_integer():
        return str(int(weight))
    else:
        return f"{weight:.1f}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Команда /start"""
    # Очищаем предыдущие данные
    context.user_data.clear()
    
    # Создаем кнопки с ПОЛНЫМИ названиями
    buttons = []
    for coating in COATINGS:
        # Используем полное название без сокращений
        full_name = f"{coating['id']}. {coating['name']}"
        buttons.append([full_name])
    
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
    logger.info(f"Пользователь выбрал: {text}")
    
    try:
        # Извлекаем ID из текста (первый символ до точки)
        coating_id = int(text.split(".")[0].strip())
        
        # Ищем покрытие по ID
        for coating in COATINGS:
            if coating["id"] == coating_id:
                context.user_data["coating"] = coating
                await update.message.reply_text(
                    f"✅ *{coating['name']}*\n\n"
                    "📐 *Введите площадь покрытия в м²:*\n"
                    "Например: 100, 250.5, 75\n\n"
                    "_Можно использовать дробные числа, разделитель - точка или запятая_",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="Markdown"
                )
                return TYPING_AREA
        
        # Если покрытие не найдено
        await update.message.reply_text("❌ Покрытие не найдено. Выберите вариант из списка!")
        return await start(update, context)
        
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка при выборе покрытия: {e}")
        await update.message.reply_text("❌ Ошибка выбора. Пожалуйста, используйте кнопки.")
        return await start(update, context)

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Расчет материалов"""
    try:
        area_text = update.message.text.replace(",", ".").strip()
        area = float(area_text)
        
        if area <= 0:
            await update.message.reply_text("❌ Площадь должна быть больше 0!")
            return TYPING_AREA
        
        if area > 10000:
            await update.message.reply_text("⚠️ Площадь слишком большая. Для точного расчета свяжитесь с нами.")
        
        coating = context.user_data.get("coating")
        if not coating:
            await update.message.reply_text("❌ Ошибка данных. Начните заново: /start")
            return ConversationHandler.END
        
        # Выполняем расчет
        result = "🏗️ *РАСЧЕТ МАТЕРИАЛОВ*\n\n"
        result += f"*Тип покрытия:* {coating['name']}\n"
        result += f"*Площадь:* {area} м²\n\n"
        result += "---\n"
        result += "*РАСХОД МАТЕРИАЛОВ:*\n\n"
        
        for layer in coating["layers"]:
            # Расчет общего расхода материала
            total_kg = area * layer["consumption"]
            
            # Расчет количества упаковок
            packages = total_kg / layer["package"]
            if packages.is_integer():
                packages_needed = int(packages)
            else:
                packages_needed = int(packages) + 1
            
            layer_name = layer["name"]
            if layer.get("optional"):
                layer_name += " (опция)"
            
            result += f"🔹 *{layer_name}*\n"
            result += f"   *Материал:* {layer['material']}\n"
            result += f"   *Расход:* {total_kg:.1f} кг\n"
            result += f"   *Упаковок:* {packages_needed} шт.\n"
            result += f"   (фасовка по {format_weight(layer['package'])} кг)\n\n"
        
        result += "---\n"
        result += "📞 *Контакты ФАСБ:*\n"
        result += "Телефон: +7 (981) 746-93-54\n"
        result += "Email: fasb_ik@vk.com\n\n"
        result += "*Внимание:* Расчет предварительный. Для точного КП обратитесь к специалистам.\n"
        result += "_Данный расчет не является офертой._"
        
        await update.message.reply_text(result, parse_mode="Markdown")
        await update.message.reply_text("🔄 Новый расчет: /start")
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Ошибка! Введите число для площади.\nПример: 100 или 150.5")
        return TYPING_AREA
    except Exception as e:
        logger.error(f"Ошибка при расчете: {e}")
        await update.message.reply_text("❌ Произошла ошибка при расчете. Попробуйте снова: /start")
        return ConversationHandler.END

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help"""
    help_text = """
📖 *Помощь по боту калькулятора ФАСБ*

*Команды:*
/start - начать новый расчет
/help - показать эту справку
/cancel - отменить текущий расчет

*Как работает бот:*
1. Выберите один из 6 типов покрытий
2. Введите площадь помещения в м²
3. Получите детальный расчет материалов

*Типы покрытий:*
1. Окрасочное полимерное покрытие для лёгких нагрузок, толщина ~0,5мм
2. Наливное эпоксидное гладкое покрытие для средних нагрузок, толщина ~2мм
3. Антискользящее эпоксидное покрытие для паркинга толщиной ~3,5-4мм
4. Декоративное покрытие 'чипсовый ковёр' толщиной ~3,5-4мм
5. Полиуретанцементное гладкое покрытие для пищевых производств толщиной ~4мм
6. Полиуретанцементное антискользящее покрытие для пищевых производств толщиной ~6мм

*Контакты компании:*
📞 Телефон: +7 (981) 746-93-54
✉️ Email: fasb_ik@vk.com

✅ Бесплатный расчет от профессионалов!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    await update.message.reply_text(
        "Операция отменена.\nДля нового расчета используйте /start",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ Ошибка: BOT_TOKEN не установлен!")
        return

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
        ],
        allow_reentry=True
    )
    
    # Добавляем обработчики
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # Запускаем
    logger.info("🤖 Бот ФАСБ запущен!")
    print("\n" + "="*60)
    print("✅ FASB FLOOR CALCULATOR BOT")
    print("🤖 Бот успешно запущен!")
    print("📱 Тестируйте в Telegram!")
    print("="*60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()