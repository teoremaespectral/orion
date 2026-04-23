from bot import my_bot
from Message import Message as M
from controller import Game, ActionDispatcher
import constants as c
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
    '''Gera um teclado com as civilizações disponíveis para escolha.'''
    keys = []
    for text in txt.CIV_BUTTON:
        keys.append([KeyboardButton(text=text)])
    return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True, one_time_keyboard=True)

def get_strategy_keyboard():
    '''Gera um teclado com as estratégias disponíveis para a IA.'''
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Dumb"), KeyboardButton(text="Rusher")],
        [KeyboardButton(text="Turtle"), KeyboardButton(text="Greedy")],
        [KeyboardButton(text="Aleatório")]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_main_keyboard():
    # Teclado principal com Pesquisa e Info inclusos
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏗️ Construções"), KeyboardButton(text="🔬 Pesquisar")],
        [KeyboardButton(text="⚔️ Exército"), KeyboardButton(text="🚩 ATACAR")],
        [KeyboardButton(text="📊 Status"), KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)

def get_build_keyboard(player):
    ''''Gera um teclado para o menu de construção, mostrando quais edificações o jogador pode construir com base em seus recursos atuais.'''
    keys = []
    for label in txt.BUILD_BUTTON(player):
        keys.append([KeyboardButton(text=label)])
    
    keys.append([KeyboardButton(text="⬅️ Voltar")])
    return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True)

def get_research_keyboard(player):
    options = txt.RESEARCH_BUTTONS(player)
    # Organiza em 2 colunas para não ficar uma lista gigante
    keyboard = [options[i:i + 2] for i in range(0, len(options), 2)]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# --- GAME SETUP ---

user_setup = {}
handlers = []

@handlers.append
def start_game(m: M):
    '''Inicia o processo de configuração do jogo, guiando o jogador pela escolha de civilização e estratégia.'''
    if m.command == "/start":
        user_setup[m.user_id] = {"step": "choosing_player_civ"}
        texto = txt.PLAYER_CIV_SELECT
        send_message(m.chat_id, texto, reply_markup=get_civ_keyboard())

@handlers.append
def handle_setup_flow(m: M):
    '''Gerencia o fluxo de configuração do jogo, avançando o jogador pelas etapas de escolha de civilização e estratégia com base em suas respostas.'''
    state = user_setup.get(m.user_id, {}).get("step")
    if not state: return

    # 1. ESCOLHA DA CIVILIZAÇÃO DO JOGADOR
    if state == "choosing_player_civ":
        chosen = next((k for k, v in c.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_setup[m.user_id]["player_civ"] = chosen
            user_setup[m.user_id]["step"] = "choosing_ai_civ"
            text = txt.AI_CIV_SELECT
            send_message(m.chat_id, text, reply_markup=get_civ_keyboard())

    # 2. ESCOLHA DA CIVILIZAÇÃO DO INIMIGO
    elif state == "choosing_ai_civ":
        chosen = next((k for k, v in c.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_setup[m.user_id]["ai_civ"] = chosen
            user_setup[m.user_id]["step"] = "choosing_strategy"
            text = txt.STRATEGY_SELECT
            send_message(m.chat_id, text, reply_markup=get_strategy_keyboard())

    # 3. ESCOLHA DA ESTRATÉGIA DA IA
    elif state == "choosing_strategy":
        strategies = ["Dumb", "Rusher", "Turtle", "Greedy", "Aleatório"]
        if m.text in strategies:
            p_civ = user_setup[m.user_id]["player_civ"]
            a_civ = user_setup[m.user_id]["ai_civ"]
            strategy = m.text.lower()
            game = Game(m.user_id, m.user_name)
            game.setup(player_civ=p_civ, ai_civ=a_civ, strategy=strategy)
            del user_setup[m.user_id]

            texto = (f"{txt.WAR_START(p_civ, a_civ, strategy)}")
            send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

# --- ACTIONS ---

@handlers.append
def handle_menu_navigation(m: M):
    ''''Gerencia a navegação entre os menus do jogo, permitindo que o jogador acesse o menu de construção ou retorne ao menu principal conforme suas escolhas.'''
    game = Game(m.user_id, m.user_name)
    
    if m.text == "🏗️ Construções":
        text = txt.BUILD_MENU_MSG(game.player_kingdom)
        send_message(m.chat_id, text, reply_markup=get_build_keyboard(game.player_kingdom))
        return True
    
    if m.text == "🔬 Pesquisar":
        text = txt.RESEARCH_MENU_MSG(game.player_kingdom)
        send_message(m.chat_id, text, reply_markup=get_research_keyboard(game.player_kingdom))
        return True

    if m.text == "⬅️ Voltar":
        send_message(m.chat_id, "Retornando ao conselho real...", reply_markup=get_main_keyboard())
        return True

@handlers.append
def show_status(m: M):
    '''Exibe o status atual do reino do jogador, incluindo recursos, força militar, integridade e outras informações relevantes para a tomada de decisões estratégicas.'''
    if m.command == "/status" or m.text == "📊 Status":
        game = Game(m.user_id, m.user_name)
        player = game.player_kingdom
        
        texto = txt.STATUS_MSG(player, game.turn_count)
        send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

@handlers.append
def show_info(m: M):
    if m.command == "/info" or m.text == "ℹ️ Info": 
        texto = txt.INFO_MSG()
        send_message(m.chat_id, texto, reply_markup=get_main_keyboard())

@handlers.append
def handle_actions(m: M):
    '''Gerencia as ações do jogador durante o jogo, interpretando suas escolhas e executando os turnos correspondentes, além de fornecer feedback detalhado sobre os resultados de suas ações e as movimentações da IA.'''
    game = Game(m.user_id, m.user_name)
    if game.status != "active": return

    action = ActionDispatcher(game, m).resolve()

    if action:
        report = game.play_turn(action) # Executa o turno completo
        
        # 1. Cabeçalho do Turno
        full_report = txt.TURN_REPORT_INTRODUCTION(game.turn_count - 1)
        # 2. Feedback da sua ação (O que você já tinha)
        full_report += txt.ACTION_FEEDBACK(report) + "\n"
        # 3. Feedback da IA (Opcional: você quer que o jogador saiba o que a IA fez?)
        full_report += txt.AI_ACTION_FEEDBACK(report) + "\n" #Retirar quando acabar o debug
        # 4. Feedback de Combate (Se houve luta)
        if report.get("fight_data"):
            full_report += txt.FIGHT_FEEDBACK(report)
        # 5. Verificar se o jogo acabou para definir o teclado final
        if game.status in ["player_won", "ai_won"]:
            resultado = txt.VICTORY if game.status == "player_won" else txt.FAILURE
            full_report += f"\n\n{resultado}"
            
            markup = ReplyKeyboardRemove()
        else:
            markup = get_main_keyboard()
        # 6. Envia a mensagem final com o teclado atualizado (ou removido)
        send_message(m.chat_id, full_report, reply_markup=markup)