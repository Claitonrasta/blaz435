import random
import re
import telebot
import threading
import time
import sqlite3

bot = telebot.TeleBot('6142935832:AAFVueVryNIQtwWUa6KczAqqEhSeFc4P1I0')

bot.delete_webhook()

active_codes = set()
user_last_interaction = {}

# Define uma função que remove o código da lista de códigos ativos
def remove_code(code):
    active_codes.remove(code)

# Define uma função que verifica se o tempo de espera para o código expirou
def check_code_timeout(code, timeout=600):
    time.sleep(timeout)
    remove_code(code)

# Define uma função que cria uma nova conexão com o banco de dados para cada thread
def get_conn():
    return sqlite3.connect('minesblaze.db')

# Lista de IDs permitidos
allowed_ids = [5754319114, 987654321]

# Tratador de mensagem para o comando /minesblaze
@bot.message_handler(commands=['minesblaze'])
def jogar(message):
    global active_codes

    # Verifica se o ID do chat está na lista de IDs permitidos
    if message.chat.id not in allowed_ids:
        bot.send_message(message.chat.id, "*Você não tem permissão para usar este comando.*", parse_mode="Markdown")
        return

    user_id = message.from_user.id
    current_time = time.time()
    last_interaction_time = user_last_interaction.get(user_id)

    if last_interaction_time and (current_time - last_interaction_time) < 600:
        remaining_time = int(600 - (current_time - last_interaction_time))
        bot.send_message(message.chat.id, f"*Aguarde mais {remaining_time} segundos antes de jogar novamente.*", parse_mode="Markdown")
        return

    code = message.text.split()[1] if len(message.text.split()) > 1 else None

    if code and len(code) == 33 and re.match("^[a-zA-Z0-9]*$", code):
        if code in active_codes:
            bot.send_message(message.chat.id, "*Por favor, aguarde 10 minutos antes de jogar novamente.*", parse_mode="Markdown")
            return

        # Adiciona o código à lista de códigos ativos
        active_codes.add(code)

        # Cria um novo thread para verificar o tempo de espera do código
        threading.Thread(target=check_code_timeout, args=(code,), daemon=True).start()

        # Atualiza o horário da última interação do usuário
        user_last_interaction[user_id] = current_time

        # Cria uma nova conexão com o banco de dados para essa thread
        with get_conn() as conn:
            c = conn.cursor()

            # Verifica se o código já foi enviado antes
            c.execute("SELECT message FROM messages WHERE code=?", (code,))
            result = c.fetchone()

            if result:
                # Se o código já foi enviado, envia a mensagem armazenada no banco de dados
                bot.send_message(message.chat.id, result[0], parse_mode="Markdown")
            else:
                # Se o código ainda não foi enviado, gera uma nova mensagem
                welcome_message = "*Bem-vindo Ao DescryptoBlaze!*"

                board = [
                    ["💣", "💣", "💣", "💣", "💣"],
                    ["💣", "💣", "💣", "💣", "💣"],
                    ["💣", "💣", "💣", "💣", "💣"],
                    ["💣", "💣", "💣", "💣", "💣"],
                    ["💣", "💣", "💣", "💣", "💣"]
                ]

                selected_cells = random.sample(range(25), 4)

                for cell in selected_cells:
                    row = cell // 5
                    col = cell % 5
                    board[row][col] = "💎"

                text = f"{welcome_message}\n\n"
                for row in range(5):
                    text += "|"
                    for col in range(5):
                        if board[row][col] == "💣":
                            text += "💣|"
                        else:
                            text += "💎|"
                    text += "\n"
                    if row != 4:
                        text += "                   \n"
                text += "                   "

                percent = round(random.uniform(60, 94), 2)
                text += f"\n\n*A TAXA DE ACERTO DESSA DESCRIPTOGRAFIA É *{percent}*, COM O MÁXIMO DE 2 GALES!!!*"

                # Armazena a mensagem no banco de dados
                c.execute("INSERT INTO messages (code, message) VALUES (?, ?)", (code, text))
                conn.commit()

                # Envia a mensagem para o usuário
                bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "*ID INVALIDO!! VERIFIQUE SE COPIOU O CÓDIGO CERTO, OBSERVE SE O ID TEM 33 CARACTERS, E SE O MESMO POSSUI SOMENTE NÚMEROS E LETRAS.*", parse_mode="Markdown")

bot.polling()
