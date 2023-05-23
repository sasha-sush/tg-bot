from telegram.ext import CommandHandler, Updater, Job
from telegram import ParseMode
import openai
import random
import datetime
import argparse
import json

settings = None
with open('settings.json') as file:
    settings = json.load(file)

tg_bot_token = settings['tg-bot-token']
openai.api_key = settings['openai-api-key']

def datetime_string():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d.%m.%Y | %H:%M:%S")
    return formatted_datetime

def log(str):
    text = datetime_string() + ' ' + str
    with open('log.txt', 'a') as file:
        file.write(text + '\n')
    print(text)


def generate_gpt_response(prompt):
    response = openai.Completion.create(
        engine='text-davinci-003',  # Використання моделі ChatGPT
        prompt=prompt,
        max_tokens=1000,  # Максимальна кількість токенів в відповіді
        temperature=1,  # Параметр, що контролює "творчість" відповідей (від 0 до 1)
        n=1,  # Кількість варіантів відповідей для генерації
        stop=None,  # Рядок, що вказує, коли зупинити генерацію тексту
    )
    return response.choices[0].text.strip()

# Функція, що обробляє команду /start
def start(update, context):
    user_name = update.message.from_user.username
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ей блять @{user_name} тут дохуя стартує сука.")


def gpt(update, context):
    message = update.message
    username = message.from_user.username
    text = None
    if context.args:
        text = ' '.join(context.args)

    query = ''

    if message.reply_to_message:
        query = message.reply_to_message.text
    elif text is not None:
        query = text
    else:
        query = "Я відправив порожній текст"

    log(f'[{update.effective_chat.title}] {username} : {message.text}')

    sent_message = context.bot.send_message(chat_id=message.chat_id, text='_Дай подумати_', reply_to_message_id=message.message_id, parse_mode="MarkdownV2")

    # Pass the sent_message object to the job's context
    context.job_queue.run_once(generate_gpt_response_job, when=0, context=(sent_message, query))

def generate_gpt_response_job(context):
    sent_message, query = context.job.context  # Retrieve the sent_message and query from the context
    reply_text = generate_gpt_response(query)
    log(f'reply to \'{query}\' : {reply_text}')
    context.bot.edit_message_text(chat_id=sent_message.chat_id, message_id=sent_message.message_id, text=reply_text)

def how_many_percent(update, context):
    message = update.message
    username = message.from_user.username
    percent = random.randint(0,100)

    if len(context.args) < 2:
        return
    
    target_username = context.args[0]
    target_role = ' '.join(context.args[1:])

    log(f'[{update.effective_chat.title}] {username} : {message.text}')

    if target_username == '@'+context.bot.username:
        context.bot.send_message(chat_id=message.chat_id, text=f'Ахуєл?', reply_to_message_id=message.message_id)
        context.bot.send_message(chat_id=message.chat_id, text=f'@{username} на 100% {target_role}')
    else:
        context.bot.send_message(chat_id=message.chat_id, text=f'{target_username} на {percent}% {target_role}')


def test(update, context):
    message = update.message

    #if message.from_user.username != 'sasha_sush':
    #    return
    
    log(f'[{update.effective_chat.title}] {message.from_user.username} : {message.text}')

    context.bot.send_message(chat_id=message.chat_id, text=f'Я жевий', parse_mode = 'MarkdownV2')

def givnorant_roll_info():
    maps = []
    with open('val\\maps.txt', 'r') as file:
        text = file.read()
        maps = text.split(' ')
    res = f'''
Ролить гравців і карту для кастомних пососалок в гівноранті

`/vroll --players \(-p\) <хуєсос1> <хуєсос2>` \- ролить із заданим списком гравців
`/vroll --only \(-o\) <карта1> <карта2>` \- ролить із заданим списком карт
`/vroll --except \(-e\) <карта1> <карта2>` \- ролить із всіма картами окрім заданих
`/vroll --last-maps \(-lm\)` \- ролить із останніми картами

доступні карти:
*{' '.join(maps)}*
'''
    return res

def givnorant_roll(update, context):
    message = update.message
    
    log(f'[{update.effective_chat.title}] {message.from_user.username} : {message.text}')

    args = context.args

    if len(args) == 0:
        args.append('-l')
    

    # Створення парсера аргументів
    parser = argparse.ArgumentParser()
    #parser.add_argument('--help', action='help')
    parser.add_argument('--last-maps', '-lm', action='store_true')
    parser.add_argument('--players', '-p', nargs='+')
    parser.add_argument('--exc', '-e', nargs='+')
    parser.add_argument('--only', '-o', nargs='+')

    # Розбір аргументів командного рядка
    try:
        args = parser.parse_args(args)
    except SystemExit as e:
        error_text = f'Шось ти неправильно натикав, запишу тебе в список підарів але поки шо тільки олівцем📝'
        log('INPUT EXCEPTION')
        context.bot.send_message(chat_id=message.chat_id, text=error_text, parse_mode='HTML')
        return

    #if args.help:
        #context.bot.send_message(chat_id=message.chat_id, text=givnorant_roll_info(), parse_mode='MarkdownV2')
        #help_text = '<code>' + args.help + '</code>'
        #context.bot.send_message(chat_id=message.chat_id, text=help_text, parse_mode='HTML')
        #return
    
    players = []
    val_last_players_file = 'val\\last_players.txt'
    if args.players:
            players = args.players
            with open(val_last_players_file, 'w') as file:
                file.write(' '.join(players))
    else:
        with open(val_last_players_file, 'r') as file:
            text = file.read()
            players = text.split(' ')

    maps = []
    val_last_maps_file = 'val\\last_maps.txt'
    if args.last_maps:
        with open(val_last_maps_file, 'r') as file:
            text = file.read()
            maps = text.split(' ')
    else:
        with open('val\\maps.txt', 'r') as file:
            text = file.read()
            maps = text.split(' ')
        if args.exc:
            except_maps = args.exc
            maps = [element for element in maps if element.lower() not in [em.lower() for em in except_maps]]
        elif args.only:
            only_maps = args.only
            maps = [element for element in maps if element.lower() in [em.lower() for em in only_maps]]

        with open(val_last_maps_file, 'w') as file:
                file.write(' '.join(maps))
        

    text_info = f'''
Вибираю із карт:
<i>{' '.join(maps)}</i>

хуєсоси:
<i>{' '.join(players)}</i>

для кастомних пососалок
'''

    context.bot.send_message(chat_id=message.chat_id, text=text_info, parse_mode='HTML')

    rand_map = maps[random.randint(0,len(maps)-1)]
    team_atk = []
    team_def = []
    for i in range(int(len(players)/2)):
        team_def.append(players.pop(random.randint(0,len(players)-1)))
    team_atk = players

    text_team_atk = '♿️' + '\n♿️'.join(team_atk)
    text_team_def = '♿️' + '\n♿️'.join(team_def)
    best_wishes = ['Приємного сосання🍌', 
                   'Обережно не паліть сраки занадто сильно🔥', 
                   'Пам\'ятайте - Мрак не має особистого життя🤓',
                   'Розчехляйте сраки🍑']
    wish = best_wishes[random.randint(0,len(best_wishes)-1)]

    text_result = f'''🍆Сосання відбувається на мапі 
🏞<u>{rand_map}</u>🏞
    
💥<b>Атакери:</b>
<i>{text_team_atk}</i>

🛡<b>Дефендери:</b>
<i>{text_team_def}</i>

{wish}'''

    context.bot.send_message(chat_id=message.chat_id, text=text_result, parse_mode='HTML')
    
def button_callback(update, context):
    query = update.callback_query
    if query.data == 'valorant-reroll':
        context.bot.send_message(chat_id=query.message.chat_id, text='/vroll -l')


def main():
    # Створюємо екземпляр Updater з токеном вашого бота
    updater = Updater(token=tg_bot_token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Додаємо обробник повідомлень
    gtp_handler = CommandHandler('gpt', gpt)
    dispatcher.add_handler(gtp_handler)

    percent_handler = CommandHandler('percent', how_many_percent)
    dispatcher.add_handler(percent_handler)

    dispatcher.add_handler(CommandHandler('vroll', givnorant_roll))
    
    dispatcher.add_handler(CommandHandler('test', test))

    # Запускаємо бота
    log('--Startup--')
    updater.start_polling()

    # Обробляємо преривання бота
    updater.idle()

if __name__ == '__main__':
    main()
