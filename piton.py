from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime, date
import matplotlib.pyplot as plt
from io import BytesIO

# Функция для расчета количества недель
def calculate_weeks(start_date, end_date):
    delta = end_date - start_date
    return delta.days // 7

# Функция для создания таблицы жизни
def create_life_table(birth_date):
    today = date.today()
    weeks_lived = calculate_weeks(birth_date, today)
    end_date = date(birth_date.year + 90, birth_date.month, birth_date.day)
    weeks_remaining = calculate_weeks(today, end_date)

    # Создаем таблицу жизни
    life_table = []
    for i in range(90):
        year = birth_date.year + i
        weeks_in_year = 52
        if i == 0:
            weeks_in_year = calculate_weeks(birth_date, date(year + 1, birth_date.month, birth_date.day))
        elif i == 89:
            weeks_in_year = calculate_weeks(date(year, birth_date.month, birth_date.day), end_date)
        life_table.append((year, weeks_in_year))

    return life_table, weeks_lived, weeks_remaining

# Функция для создания изображения таблицы жизни
def create_life_image(life_table, weeks_lived):
    # Создаем изображение
    fig, ax = plt.subplots(figsize=(10, 10))

    # Рисуем таблицу
    for i, (year, weeks) in enumerate(life_table):
        for j in range(weeks):
            if (i * 52 + j) < weeks_lived:
                # Прожитые недели: черный квадрат с белой рамкой
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor='black', edgecolor='white', linewidth=0.5))
            else:
                # Оставшиеся недели: белый квадрат с черной рамкой
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor='white', edgecolor='black', linewidth=0.5))

    # Настройки графика
    ax.set_xlim(0, 52)
    ax.set_ylim(0, 90)
    ax.set_aspect('equal')
    ax.axis('off')  # Скрываем оси

    # Сохраняем изображение в буфер
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    return buf

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Пожалуйста, введите вашу дату рождения в формате ГГГГ-ММ-ДД:")

# Обработчик ввода даты рождения
async def handle_birth_date(update: Update, context: CallbackContext):
    try:
        birth_date = datetime.strptime(update.message.text, "%Y-%m-%d").date()
        life_table, weeks_lived, weeks_remaining = create_life_table(birth_date)

        # Создаем изображение таблицы жизни
        image_buf = create_life_image(life_table, weeks_lived)

        # Отправляем изображение пользователю
        await update.message.reply_photo(photo=image_buf, caption=f"Прожито недель: {weeks_lived}\nОсталось недель до 90 лет: {weeks_remaining}")

    except ValueError:
        await update.message.reply_text("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")

def main():
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token("7753161451:AAGxDZFa5vcdefU5bdW89RBXJiXUOencyk4").build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_birth_date))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()