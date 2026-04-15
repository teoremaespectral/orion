from bot import my_bot
from Message import Message as M
from controller import Game
import constants as consts
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import display as txt

# --- FUNCIONALIDADES ---

send_message = my_bot.sendMessage
send_sticker = my_bot.sendSticker
send_audio = my_bot.sendVoice
send_music = my_bot.sendAudio
send_video_note = my_bot.sendVideoNote

def send_message(chat_id, text, reply_markup=None):
    return my_bot.sendMessage(chat_id, text, reply_markup=reply_markup, parse_mode='Markdown')

# --- TECLADOS DINÂMICOS ---

def get_civ_keyboard():
    keys = []
    for name, info in consts.CIVS.items():
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
        [KeyboardButton(text="🏗️ Construções"), KeyboardButton(text="⚔️ Treinar Exército")],
        [KeyboardButton(text="😈 ATACAR"), KeyboardButton(text="📊 Status")]
    ], resize_keyboard=True)

def get_build_keyboard(player):
    keys = []
    for b_id, info in consts.BUILDINGS.items():
        # Lógica de "Botão Escuro/Bloqueado"
        can_build = (player.resources['food'] >= info['food_cost'] and 
                     player.resources['wood'] >= info['wood_cost'])
        
        if info.get('slots', 0) > 0 and player.occupied_slots >= player.total_slots:
            can_build = False

        icon = "🔨" if can_build else "🚫"
        label = f"{icon} {info['label']} (🍎{info['food_cost']} 🪵{info['wood_cost']})"
        keys.append([KeyboardButton(text=label)])
    
    keys.append([KeyboardButton(text="🔙 Voltar")])
    return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True)

user_setup = {}
handlers = []

# --- GAME SETUP ---

@handlers.append
def start_game(m: M):
    if m.command == "/start":
        user_setup[m.user_id] = {"step": "choosing_player_civ"}
        texto = txt.PLAYER_CIV_SELECT
        send_message(m.chat_id, texto, reply_markup=get_civ_keyboard())

@handlers.append
def handle_setup_flow(m: M):
    state = user_setup.get(m.user_id, {}).get("step")
    if not state: return

    if state == "choosing_player_civ":
        chosen = next((k for k, v in consts.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_setup[m.user_id]["player_civ"] = chosen
            user_setup[m.user_id]["step"] = "choosing_ai_civ"
            text = txt.AI_CIV_SELECT
            send_message(m.chat_id, text, reply_markup=get_civ_keyboard())

    elif state == "choosing_ai_civ":
        chosen = next((k for k, v in consts.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_setup[m.user_id]["ai_civ"] = chosen
            user_setup[m.user_id]["step"] = "choosing_strategy"
            text = txt.STRATEGY_SELECT
            send_message(m.chat_id, text, reply_markup=get_strategy_keyboard())

    elif state == "choosing_strategy":
        strategies = ["Dumb", "Rusher", "Turtle", "Greedy", "Aleatório"]
        if m.text in strategies:
            p_civ = user_setup[m.user_id]["player_civ"]
            a_civ = user_setup[m.user_id]["ai_civ"]
            strategy = m.text
            game = Game(m.user_id, m.user_name)
            game.setup(player_civ=p_civ, ai_civ=a_civ, strategy=strategy)
            del user_setup[m.user_id]

            texto = (f"{txt.WAR_START(p_civ, a_civ, strategy)}")
            send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

# --- ACTIONS ---

@handlers.append
def handle_menu_navigation(m: M):
    game = Game(m.user_id, m.user_name)
    
    # 1. ENTRAR NO MENU DE CONSTRUÇÃO
    if m.text == "🏗️ Construções":
        texto = txt.BUILD_MENU_MSG(game.player)
        send_message(m.chat_id, texto, reply_markup=get_build_keyboard(game.player))
        return True

    # 2. VOLTAR AO MENU PRINCIPAL
    if m.text == "🔙 Voltar":
        send_message(m.chat_id, "Retornando ao conselho real...", reply_markup=get_main_keyboard())
        return True

@handlers.append
def show_status(m: M):
    if m.command == "/status" or m.text == "📊 Status":
        game = Game(m.user_id, m.user_name)
        player = game.player
        
        texto = txt.STATUS_MSG(player, game.turn_count)
        send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

@handlers.append
def handle_actions(m: M):
    game = Game(m.user_id, m.user_name)
    if game.status != "active": return

    action = {"type": None, "target": None}

    # IDENTIFICAR AÇÃO POR DICIONÁRIO
    if "Treinar Exército" in m.text:
        action = {"type": "army", "target": None}
    elif "ATACAR" in m.text:
        action = {"type": "attack", "target": "invasion"} # Padrão v1.2
    elif "🔨" in m.text or "🚫" in m.text:
        # Extrair o nome da construção do texto do botão
        for b_id, info in consts.BUILDINGS.items():
            if info['label'] in m.text:
                action = {"type": "build", "target": b_id}
                break

    if action["type"]:
        report = game.play_turn(action) # Enviando o dicionário!
        
        # Feedback visual
        feedback = txt.ACTION_FEEDBACK(report)
        # Se houve luta, anexa o relatório de combate
        if report.get("fight_data"):
            feedback += txt.COMBAT_REPORT(report["fight_data"], report)
            
        send_message(m.chat_id, feedback, reply_markup=get_main_keyboard())