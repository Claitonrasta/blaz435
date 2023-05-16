import random
import re
import telebot
import time

# Criar uma instância do bot usando o token de acesso
bot = telebot.TeleBot('6052245829:AAFbs55v_Y0-C2XvloyaprHjpOJhQ0orzs8')

# Deletar o webhook ativo
bot.delete_webhook()

# Dicionário para armazenar o último horário de envio de mensagem por cada usuário
last_message_time = {}

# Definir um manipulador de mensagens para o comando /minesblaze
@bot.message_handler(commands=['minesblaze'])
def jogar(message):
    code = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if code and len(code) >= 10 and re.match("^[a-zA-Z0-9]*$", code):
        user_id = message.from_user.id
        current_time = time.time()
        
        if user_id in last_message_time and current_time - last_message_time[user_id] < 600:
            bot.send_message(message.chat.id, "Você só pode enviar uma mensagem a cada 10 minutos.")
        else:
            last_message_time[user_id] = current_time
            
            # Representação do tabuleiro
            board = [
                ["🟥", "🟥", "🟥", "🟥", "🟥"],
                ["🟥", "🟥", "🟥", "🟥", "🟥"],
                ["🟥", "🟥", "🟥", "🟥", "🟥"],
                ["🟥", "🟥", "🟥", "🟥", "🟥"],
                ["🟥", "🟥", "🟥", "🟥", "🟥"]
            ]

            # Sortear 3 casas aleatórias
            selected_cells = random.sample(range(25), 3)

            # Marcar as casas sorteadas no tabuleiro
            for cell in selected_cells:
                row = cell // 5
                col = cell % 5
                board[row][col] = "✅"

            # Criar uma string com a representação do tabuleiro com as casas selecionadas marcadas
            text = "┌─────────────────────┐\n"
            for row in range(5):
                text += "│"
                for col in range(5):
                    if board[row][col] == "🟥":
                        text += "🟥"
                    else:
                        text += " ✅ │"
                text += "\n"
                if row != 4:
                    text += "├─────────────────────┤\n"
            text += "└─────────────────────┘"

            # Adicionar porcentagem aleatória entre 60% e 94%
            percent = round(random.uniform(60, 94), 2)
            text += f"\n\nA TAXA DE ACERTO DESSA DESCRIPTOGRAFIA É {percent}%, COM O MÁXIMO DE 2 GALES!!!"

            # Enviar a mensagem com o tabuleiro e a porcentagem para o chat que iniciou o bot
            bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "ERRO AO TENTAR DESCRIPTOGRAFAR O PADRÃO DESSE TOKEN")

# Iniciar o bot
bot.polling()

