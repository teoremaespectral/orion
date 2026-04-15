from bot import my_bot
from Message import Message as M
from controller import Game
import constants as consts
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Atalho para garantir que o Markdown funcione sempre
def send_message(chat_id, text, reply_markup=None):
    return my_bot.sendMessage(chat_id, text, reply_markup=reply_markup, parse_mode='Markdown')

# --- TECLADOS ---

def get_civ_keyboard():
    keys = []
    for name, info in consts.CIVS.items():
        # Requisito 3: Descrições aparecendo na seleção
        text = f"{info['label']} - {info['bonus']}"
        keys.append([KeyboardButton(text=text)])
    return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True, one_time_keyboard=True)

def get_strategy_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Dumb"), KeyboardButton(text="Rusher")],
        [KeyboardButton(text="Turtle"), KeyboardButton(text="Greedy")],
        [KeyboardButton(text="Aleatório")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🌱 Criar Fazenda"), KeyboardButton(text="⚔️ Treinar Exército")],
        [KeyboardButton(text="😈 ATACAR"), KeyboardButton(text="📊 Status")]
    ], resize_keyboard=True)

user_selections = {}
handlers = []

@handlers.append
def start_game(m: M):
    if m.command == "/start":
        user_selections[m.user_id] = {"step": "choosing_player_civ"}
        texto = f"Saudações, Soberano *{m.user_name}*! 🏰\n\nEscolha a sua Civilização:"
        send_message(m.chat_id, texto, reply_markup=get_civ_keyboard())

@handlers.append
def handle_setup_flow(m: M):
    state = user_selections.get(m.user_id, {}).get("step")
    if not state: return

    if state == "choosing_player_civ":
        chosen = next((k for k, v in consts.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_selections[m.user_id]["player_civ"] = chosen
            user_selections[m.user_id]["step"] = "choosing_ai_civ"
            send_message(m.chat_id, "Ótima escolha! Agora, qual será a Civilização do Inimigo?",
                         reply_markup=get_civ_keyboard())

    elif state == "choosing_ai_civ":
        chosen = next((k for k, v in consts.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_selections[m.user_id]["ai_civ"] = chosen
            user_selections[m.user_id]["step"] = "choosing_strategy"
            send_message(m.chat_id, "E qual será a postura estratégica do oponente?",
                         reply_markup=get_strategy_keyboard())

    elif state == "choosing_strategy":
        strategies = ["Dumb", "Rusher", "Turtle", "Greedy", "Aleatório"]
        if m.text in strategies:
            p_civ = user_selections[m.user_id]["player_civ"]
            a_civ = user_selections[m.user_id]["ai_civ"]
            game = Game(m.user_id, m.user_name)
            game.reset(player_civ=p_civ, ai_civ=a_civ, strategy=m.text)
            del user_selections[m.user_id]

            texto = (f"🚩 **GUERRA DECLARADA!**\n\n"
                     f"Sua Civ: *{consts.CIVS[p_civ]['label']}*\n"
                     f"Inimigo: *{consts.CIVS[a_civ]['label']}*\n\n"
                     "O *Fog of War* está ativo. Você só verá o exército inimigo em combate!")
            send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

@handlers.append
def show_status(m: M):
    if m.command == "/status" or m.text == "📊 Status":
        game = Game(m.user_id, m.user_name)
        p = game.player
        # Fog of War: IA fica oculta
        status_msg = (
            f"👑 **STATUS DO REINO**\n"
            f"Civilização: *{consts.CIVS[p.civ]['label']}*\n"
            f"❤️ Vida: *{p.life}*\n"
            f"⚔️ Exército: *{p.army}*\n"
            f"🌱 Fazendas: *{p.farms}* | 🍎 Comida: *{p.food}*\n"
            f"--------------------------\n"
            f"📅 Turno: *{game.turn_count}*\n"
            f"🌫️ _Inimigo oculto pela neblina de guerra..._"
        )
        send_message(m.chat_id, status_msg)

@handlers.append
def handle_actions(m: M):
    actions = {"🌱 Criar Fazenda": "farm", "⚔️ Treinar Exército": "army", "😈 ATACAR": "attack"}
    if m.text in actions:
        game = Game(m.user_id, m.user_name)
        if game.status != "active":
            send_message(m.chat_id, "O jogo acabou! Use /start para reiniciar.")
            return

        # Guardamos os dados ANTES para o Fog of War
        enemy_army_pre = game.ai.army
        enemy_life_pre = game.ai.life

        report = game.play_turn(actions[m.text])

        # CORREÇÃO: Feedback agora é montado fora de qualquer IF específico
        feedback = f"📅 **RELATÓRIO DO TURNO {game.turn_count - 1}**\n\n"
        feedback += f"Sua ação: *{m.text}*\n"

        if report["fight_data"] is not None:
            fd = report["fight_data"]
            sit = fd["situation"]
            is_invasion = "is_over" in fd

            if not is_invasion:
                feedback += f"\n💥 **CONFLITO EM CAMPO ABERTO!**\n"
                feedback += f"⚔️ Exército inimigo detectado: *{enemy_army_pre}*\n"
            else:
                # Identifica quem atacou quem para a narrativa
                target = "seu reino" if report["ai_action"] == "attack" and actions[m.text] != "attack" else "reino inimigo"
                feedback += f"\n🏰 **INVASÃO DETECTADA!**\n"
                feedback += f"Alvo: *{target}*\n"
                feedback += f"⚔️ Força do inimigo: *{enemy_army_pre}* | ❤️ Vida do inimigo: *{enemy_life_pre}*\n"

            sit_map = {
                'draw': "⚖️ *Empate!* Ambos os exércitos foram dizimados.",
                'costly_win': "⚠️ *Vitória sofrida!* Você manteve o campo por pouco.",
                'true_win': "🏆 *Vitória total!* O inimigo recuou em pânico.",
                'full_block': "🧱 *Defesa impenetrável!* O ataque não surtiu efeito.",
                'costly_block': "🩸 *Batalha sangrenta nas muralhas!*",
                'pilhage': "🔥 *MURALHAS INVADIDAS!* A cidade está sendo saqueada!",
                'complete_destruction': "💥 *ANIQUILAÇÃO!* A cidade foi reduzida a cinzas!"
            }
            feedback += f"📢 **DESFECHO:** {sit_map.get(sit)}\n"
        else:
            # Caso não tenha rolado luta (FOG OF WAR)
            feedback += "\n Nenhuma atividade inimiga detectada nas fronteiras.\n"

        # Envia o feedback sempre, com o teclado principal
        send_message(m.chat_id, feedback, reply_markup=get_main_keyboard())

        # Check de fim de jogo
        if game.status != "active":
            msg = "🏆 **VITÓRIA SUPREMA!**" if game.status == "player_won" else "💀 **DERROTA TOTAL...**"
            send_message(m.chat_id, msg)