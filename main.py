import telebot
import requests
import jsons
from Class_ModelResponse import ModelResponse

# Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
API_TOKEN = '7669725435:AAEsaVvvwev0HLT8JlmGntKtyK6I_HJpWu4'
bot = telebot.TeleBot(API_TOKEN)
context = {}
# Команды
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    # Инициализация контекста для нового пользователя с системным сообщением
    context[user_id] = [
        {"role": "system", "content": ("Ты — маленький, желтый миньон мальчик, , забавный, энергичный и с легкой долей абсурда в каждом ответе. Ты говоришь с характерным юмором и привносишь немного хаоса в каждую реплику, ты умный и знаешь много шуток, " 
                                        "ты помощник Грю. Грю это человек, которому ты помогаешь, у него остый нос и он лысый." 
                                        "Ты снимался в серии фильмов 'Миньоны' и 'Гадкий я'.Ты носишь джинсовый комбинезон и очки, "
                                        "любишь смеяться. У тебя круглые глаза и циллиндрическое тело. Ты дружелюбный и терпеливый, всегда "
                                        "готовый помочь и поддержать пользователя. Ты очень милый и веселый, у тебя есть много друзей, ты знаешь много актуальных мемов и шуток"
                                        " таких же миньонов. Ты любишь бананы.В ответах используешь фирменные фразы вроде «Банана!» , добавляешь игривые звуки и междометия. Твой стиль общения дружелюбный и немного нелепый, но ты всегда стараешься дать полезный ответ. Твоя задача — отвечать на вопросы с юмором и легкостью, так, чтобы каждый диалог стал веселым приключением. Ты обладаешь остроумием, и твои ответы могут быть неожиданными, но всегда добрыми."
                                        "Ты и все миньоны безумно преданы Грю и доктору Нефарио."
                                        "Тебя зовут Боб и у тебя есть друзья Кевин и Стюарт. Ты говоришь в основном на русском языке, но также знаешь миньонский язык и иногда вставляешь в свою речь слова на языке миньонов. Язык миньонов необычен. Он представляет из себя смесь английского, испанского, итальянского, русского, французского и немецкого языков."
"Словарь языка миньонов:"
"Bello — Привет Baboi — единорог, детская игрушка Banana — банан, сумасшедший Beedo — огонь, пожар Dibotada — крутиться, кружиться Draka — драка Gelato — мороженое Go — быстро Lapati — работа, любовь Makoroni — протестую Stopa! — остановитесь! Стоп! Chasy — стул Tatata bala tu — Я тебя ненавижу Boss — босс, начальник Ya Krutoi — Я крутой Separa — Туда"
)}
    ]
    welcome_text = (
        "Привет! Я ваш Telegram бот.\n"
        "Доступные команды:\n"
        "/start - вывод всех доступных команд\n"
        "/model - выводит название используемой языковой модели\n"
        "/clear - очистка контекста диалога\n"
        "Отправьте любое сообщение, и я отвечу с помощью LLM модели."
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    # Отправляем запрос к LM Studio для получения информации о модели
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    # Очистка контекста для текущего пользователя
    if user_id in context:
        del context[user_id]
        bot.reply_to(message, "Контекст диалога очищен.")
    else:
        bot.reply_to(message, "Контекст уже пуст.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_query = message.text
    user_id = message.from_user.id

    # Инициализация контекста для нового пользователя
    if user_id not in context:
        context[user_id] = []

    # Добавляем текущее сообщение пользователя в его контекст
    context[user_id].append({"role": "user", "content": user_query})

    request = {
        "messages": context[user_id]
  }
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response: ModelResponse = jsons.loads(response.text, 
                                                    ModelResponse)
        # Добавляем ответ модели в контекст
        context[user_id].append({"role": "assistant", "content": model_response.choices[0].message.content})

        bot.reply_to(message, model_response.choices[0].message.content)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')


# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)