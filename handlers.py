from bot import my_bot
from Message import Message as M
from controller import Game
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

send_message = my_bot.sendMessage

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🌱 Criar Fazenda"), KeyboardButton(text="⚔️ Treinar Exército")],
        [KeyboardButton(text="😈 ATACAR"), KeyboardButton(text="📊 Status")]
    ], resize_keyboard=True)

handlers = []

@handlers.append
def start_game(m: M):
    if m.command == "/start":
        game = Game(m.user_id, m.user_name)
        game.reset()
        texto = (f"Saudações, Soberano {m.user_name}! 🏰\n\n"
                 "Seu reino foi fundado. O inimigo está à espreita.\n"
                 "Prepare-se para a guerra!")
        send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

@handlers.append
def show_status(m: M):
    if m.command == "/status" or m.text == "📊 Status":
        game = Game(m.user_id, m.user_name)
        p = game.player
        status_msg = (
            f"👑 **{p.user_name.upper()}** | Turno: {game.turn_count}\n"
            f"❤️ Vida: {p.life} | 🌾 Fazendas: {p.farms}\n"
            f"🍎 Comida: {p.food} | 🗡️ Exército: {p.army}\n"
            "--------------------------"
        )
        send_message(m.chat_id, status_msg, parse_mode="Markdown")

@handlers.append
def handle_actions(m: M):
    actions = {"🌱 Criar Fazenda": "farm", "⚔️ Treinar Exército": "army", "😈 ATACAR": "attack"}
    
    if m.text in actions:
        game = Game(m.user_id, m.user_name)

        if game.status != "active":
            res = "VITÓRIA! 🎉" if game.status == "player_won" else "DERROTA... ⚰️"
            send_message(m.chat_id, f"O jogo acabou! {res}\nUse /start para reiniciar.")
            return

        report = game.play_turn(actions[m.text])

        # 1. Feedback Básico de Ação
        txt_map = {"farm": "🌱 Nova fazenda!", "army": "⚔️ Recrutamento concluído!", "attack": "🔥 Marcha iniciada!", "fail": "⚠️ Falha (recursos/exército)!"}
        
        feedback = (f"📅 **TURNO {game.turn_count - 1}**\n"
                    f"{txt_map.get(report['player_result'], 'Ocioso')}\n"
                    "--------------------------\n")

        # 2. Feedback de Combate (Se houver)
        if report["fight_data"]:
            fd = report["fight_data"]
            sit = fd["situation"]
            
            # Traduções das situações que criamos
            sit_map = {
                'draw': "⚔️ Empate sangrento no campo!",
                'costly_win': "⚠️ Vitória custosa em campo aberto!",
                'true_win': "🏆 Massacre! Você dominou o campo!",
                'full_block': "🛡️ O cerco foi repelido pelas muralhas!",
                'costly_block': "🧱 Batalha brutal nos muros da cidade!",
                'pilhage': "🔥 AS MURALHAS CAÍRAM! Pilhagem iniciada!",
                'complete_destruction': "💥 ANIQUILAÇÃO TOTAL DA CIDADE!"
            }
            
            feedback += f"📢 **COMBATE:** {sit_map.get(sit, 'Confronto inesperado!')}\n"
            
            # Se for invasão, mostra dano ou sobrevivência
            if "is_over" in fd:
                feedback += f"📉 Perdas Atacante: {int(fd['attacker_loss']*100)}%\n"
                feedback += f"📉 Perdas Defensor: {int(fd['defender_loss']*100)}%\n"

        # 3. Check Final de Vitória/Derrota
        if game.status != "active":
            if game.status == "player_won":
                feedback += "\n🌟 **O REINO INIMIGO CAIU! VOCÊ VENCEU!** 👑"
            else:
                feedback += "\n🔥 **SEU REINO FOI ARRASADO... DERROTA.** 💀"
            send_message(m.chat_id, feedback, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        else:
            p = game.player
            feedback += f"\n🍎 {p.food} | 🗡️ {p.army}"
            send_message(m.chat_id, feedback, parse_mode="Markdown")