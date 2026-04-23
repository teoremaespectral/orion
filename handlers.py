from bot import my_bot
from Message import Message as M
from controller import Game, ActionDispatcher, MenuManager
import constants as c
from telepot.namedtuple import ReplyKeyboardRemove
import display as txt

# --- FUNCIONALIDADES ---

send_message = my_bot.sendMessage
send_sticker = my_bot.sendSticker
send_audio = my_bot.sendVoice
send_music = my_bot.sendAudio
send_video_note = my_bot.sendVideoNote

def send_message(chat_id, text, reply_markup=None):
    return my_bot.sendMessage(chat_id, text, reply_markup=reply_markup, parse_mode='Markdown')

# --- GAME SETUP ---

user_setup = {}
handlers = []

@handlers.append
def start_game(m: M):
    if m.command == "/start":
        user_setup[m.user_id] = {"step": "choosing_player_civ"}
        menu = MenuManager(Game(m.user_id, m.user_name))
        res = menu.setup_player_civ_menu()
        
        send_message(m.chat_id, res["text"], reply_markup=res["markup"])

@handlers.append
def handle_setup_flow(m: M):
    state = user_setup.get(m.user_id, {}).get("step")
    if not state: return
    
    game = Game(m.user_id, m.user_name)
    menu = MenuManager(game)

    # Estágio 1: Escolha da Civilização do Jogador
    if state == "choosing_player_civ":
        chosen = next((k for k, v in c.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_setup[m.user_id].update({"player_civ": chosen, "step": "choosing_ai_civ"})
            res = menu.setup_ai_civ_menu()
            send_message(m.chat_id, res["text"], reply_markup=res["markup"])

    # Estágio 2: Escolha da Civilização do Inimigo
    elif state == "choosing_ai_civ":
        chosen = next((k for k, v in c.CIVS.items() if v["label"] in m.text), None)
        if chosen:
            user_setup[m.user_id].update({"ai_civ": chosen, "step": "choosing_strategy"})
            res = menu.setup_strategy_menu()
            send_message(m.chat_id, res["text"], reply_markup=res["markup"])

    # Estágio 3: Escolha da Estratégia do Oponente
    elif state == "choosing_strategy":
        strategies = ["Dumb", "Rusher", "Turtle", "Greedy", "Aleatório"]
        if m.text in strategies:
            setup_data = user_setup[m.user_id]
            game.setup(player_civ=setup_data["player_civ"], 
                       ai_civ=setup_data["ai_civ"], 
                       strategy=m.text.lower())
            del user_setup[m.user_id]
            
            # Mensagem de início de guerra
            texto = txt.WAR_START(setup_data["player_civ"], setup_data["ai_civ"], m.text)
            send_message(m.chat_id, texto, reply_markup=menu._get_main_keyboard())

# --- ACTIONS ---

@handlers.append
def handle_menu_navigation(m: M):
    game = Game(m.user_id, m.user_name)
    menu = MenuManager(game)
    
    # Dicionário de despacho para evitar if/elif
    NAVEGACAO = {
        "🏗️ Construções": menu.build_menu,
        "🔬 Pesquisar": menu.research_menu,
        "📊 Status": menu.status_menu,
        "ℹ️ Info": menu.info_menu,
        "⬅️ Voltar": menu.main_menu
    }

    if m.text in NAVEGACAO:
        res = NAVEGACAO[m.text]()
        send_message(m.chat_id, res["text"], reply_markup=res["markup"])
        return True

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
            menu = MenuManager(game)
            res = menu.main_menu()
            markup = res["markup"]
        # 6. Envia a mensagem final com o teclado atualizado (ou removido)
        send_message(m.chat_id, full_report, reply_markup=markup)