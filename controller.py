from secrets import choice
from Message import Message as M
from models import Kingdom, Bot, CombatEngine
from db_utils import get_db, save_db
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import constants as c
import display as txt
class Game:
    def __init__(self, user_id, user_name):
        self.user_id = str(user_id)
        self.user_name = user_name
        self.db_data = get_db('games_data')
        
        self._load_game_data()

    def _load_game_data(self):
        '''Método privado para desafogar o init e centralizar o carregamento de dados.'''
        data = self.db_data.get(self.user_id)
        ai_data = self.db_data.get(f"{self.user_id}_ai")

        if not data:
            self._setup_new_game()
        else:
            self.turn_count = data.get('turn_count', 1)
            self.status = data.get('status', 'active')
            
            self.player_kingdom = Kingdom(self.user_id, self.user_name, data=data)
            self.ai_kingdom = Kingdom(f"{self.user_id}_ai", "Inimigo", data=ai_data['kingdom'])
            self.ai_brain = Bot(brain_data= ai_data['brain'])

    def _setup_new_game(self):
        '''Inicializa os valores para um jogo do zero.'''
        self.turn_count = 1
        self.status = "active"
        self.player_kingdom = Kingdom(self.user_id, self.user_name)
        self.ai_kingdom = Kingdom(f"{self.user_id}_ai", "Inimigo")
        self.ai_brain = Bot()
    
    def save(self):
        '''Salva o estado atual do jogo no banco de dados, incluindo os dados do jogador, da IA, o número de turnos, a estratégia da IA e a fila de táticas atual. Garante que todas as informações relevantes sejam armazenadas para que o jogo possa ser retomado posteriormente.'''
        player_data = self.player_kingdom.to_dict()
        player_data['turn_count'] = self.turn_count
        player_data['status'] = self.status

        self.db_data[self.user_id] = player_data
        self.db_data[f"{self.user_id}_ai"] = {
            'kingdom': self.ai_kingdom.to_dict(), 
            'brain': self.ai_brain.to_dict()
            }

        save_db(self.db_data, 'games_data')

    def setup(self, player_civ="Teresópolis", ai_civ="Petrópolis", strategy="aleatório"):
        '''Configura o jogo para um novo usuário, definindo as civilizações do jogador e da IA, bem como a estratégia da IA. Garante que os reinos sejam criados com os bônus e modificadores corretos de acordo com as civilizações escolhidas. Salva o estado inicial do jogo no banco de dados.'''
        # Garante que criamos reinos limpos com a civ correta
        self.player_kingdom = Kingdom(self.user_id, self.user_name)
        self.player_kingdom.civ = player_civ
    
        self.ai_kingdom = Kingdom(f"{self.user_id}_ai", "Bot")
        self.ai_kingdom.civ = ai_civ

        self.ai_brain = Bot()
        self.ai_brain.civ = ai_civ

        if strategy == "aleatório":
            strategy = choice(["dumb", "rusher", "turtle", "greedy"])
    
        self.ai_brain.personality = strategy
        self.turn_count = 1 
        self.status = "active"
        self.save()

    def play_turn(self, action):
        """
        Orquestra o turno:
        1. Executa ação do jogador
        2. Executa ação da IA
        3. Atacar!
        4. Produção para ambos
        """

        #O feedback do que ocorreu no turno

        # 1. Ação do Jogador
        player_action = self.process_player_turn(action)

        # 2. Turno da IA (Lógica simples por enquanto)
        ai_action = self.process_ai_turn()

        # 3. Checa se há combate
        fight_data = self.process_fight(player_action, ai_action)

        # 4. Produção (Turno passa para ambos)
        self.player_kingdom.produce_resources()
        self.ai_kingdom.produce_resources()

        # Salvar
        self.turn_count += 1
        self._check_victory_conditions()
        self.save()

        report = {
            "player_action": player_action,
            "ai_action": ai_action,
            "fight_data": fight_data,
        }
        return report
    
    def process_player_turn(self, action):
        a_type, a_target = action['type'], action['target']

        action['success'] = False

        if a_type == "build":
            if self.player_kingdom.build(a_target):
                action['success'] = True
        elif a_type == "research":
            if self.player_kingdom.research(a_target):
                action['success'] = True
        elif a_type == "army":
            if self.player_kingdom.train_army():
                action['success'] = True
        elif a_type == "attack":
            if self.player_kingdom.army > 0:
                action['success'] = True
        
        return action

    def process_ai_turn(self):
        """
        Gerencia a fila de táticas da IA. Se não houver plano, pede um novo 
        para a AI_logic baseado na estratégia.
        """

        ai_action = self.ai_brain.get_next_action(self.ai_kingdom).copy()
        a_type, a_target = ai_action['type'], ai_action['target']
        ai_action['success'] = False

        # 3. Tenta executar
        if a_type == "build":
            if self.ai_kingdom.build(a_target):
                ai_action['success'] = True
        elif a_type == "research":
            if self.ai_kingdom.research(a_target):
                ai_action['success'] = True
        elif a_type == "army":
            if self.ai_kingdom.train_army():
                ai_action['success'] = True
        elif a_type == "attack":
            if self.ai_kingdom.army > 0:
                ai_action['success'] = True

        return ai_action

    def process_fight(self, player_action, ai_action):
        """Simulação de combate"""
        p_true_attack = player_action['type'] == "attack" and player_action['success']
        ai_true_attack = ai_action['type'] == "attack" and ai_action['success']

        if p_true_attack and ai_true_attack:
            # Caso 1: Ambos atacam -> Campo Aberto
            engine = CombatEngine(self.player_kingdom, self.ai_kingdom)
            return engine.resolve(type="open_field")
            
        elif p_true_attack:
            # Caso 2: Só jogador ataca -> Invasão à IA
            engine = CombatEngine(self.player_kingdom, self.ai_kingdom)
            return engine.resolve(type="invasion")
            
        elif ai_true_attack:
            # Caso 3: Só IA ataca -> Invasão ao Jogador
            engine = CombatEngine(self.ai_kingdom, self.player_kingdom)
            return engine.resolve(type="invasion")

        return None
    
    def _check_victory_conditions(self):
        if self.player_kingdom.life <= 0:
            self.status = "ai_won"
        elif self.ai_kingdom.life <= 0:
            self.status = "player_won"
        return

class ActionDispatcher:
    ''''Classe responsável por interpretar a mensagem do jogador e mapear para a ação correspondente, garantindo que o processo de identificação da intenção do jogador seja centralizado e facilmente gerenciável. Facilita a adição de novas ações no futuro, bastando atualizar o dicionário de triggers e implementar o handler correspondente.'''
    def __init__(self, game: Game, m: M):
        '''Inicializa o dispatcher com a mensagem do jogador e define o mapa de triggers para as ações. O mapa associa cada trigger (como "⚔️" para recrutar exército) a um método específico que processará essa ação.'''
        self.m = m
        self.game = game

        self.trigger_map = {
            txt.ACTION_TRIGGER['army']: self._handle_army,
            txt.ACTION_TRIGGER['attack']: self._handle_attack,
            txt.ACTION_TRIGGER['build']: self._handle_build,
            txt.ACTION_TRIGGER['research']: self._handle_research
        }

    def resolve(self):
        '''Percorre o mapa de triggers para identificar qual ação corresponde à mensagem do jogador. Se a mensagem começar com um dos triggers definidos, o método associado será chamado para processar a ação. Retorna um dicionário com o tipo e alvo da ação, ou None se nenhum trigger for identificado.'''
        for trigger, handler in self.trigger_map.items():
            if self.m.text.startswith(trigger):
                return handler()
        return None
    
    def _handle_army(self):
        '''Processa a ação de recrutar exército, retornando um dicionário indicando que o tipo da ação é "army" e que não há um alvo específico. O sucesso ou falha dessa ação será determinado posteriormente no processo de execução do turno.'''
        return {"type": "army", "target": None}
    
    def _handle_attack(self):
        '''Processa a ação de ataque, retornando um dicionário indicando que o tipo da ação é "attack" e que o alvo é "invasion". O sucesso ou falha dessa ação será determinado posteriormente no processo de execução do turno.'''
        return {"type": "attack", "target": "invasion"}
    
    def _handle_build(self):
        '''Processa a ação de construção, extraindo o nome do edifício da mensagem do jogador e comparando com os rótulos dos edifícios definidos nas constantes. Retorna um dicionário indicando que o tipo da ação é "build" e o alvo é o ID do edifício correspondente. Se nenhum edifício for identificado, retorna None.'''
        clean_text = self.m.text.replace(txt.ACTION_TRIGGER['build'], "").split('(')[0].strip()
        
        for b_id, info in c.BUILDINGS.items():
            if info['label'] == clean_text:
                return {"type": "build", "target": b_id}
        return None

    def _handle_research(self):
        '''Processa a ação de pesquisa, extraindo o nome da tecnologia da mensagem do jogador e comparando com os rótulos das tecnologias definidas nas constantes. Retorna um dicionário indicando que o tipo da ação é "research" e o alvo é o ID da tecnologia correspondente. Se nenhuma tecnologia for identificada, retorna None.'''
        clean_text = self.m.text.replace(txt.ACTION_TRIGGER['research'], "").strip()
        
        for t_id, info in c.TECHNOLOGIES.items():
            if info['label'] == clean_text:
                return {"type": "research", "target": t_id}
        return None

class MenuManager:
    def __init__(self, game):
        self.game = game
        self.player = game.player_kingdom

    def _format(self, text, markup):
        """Padroniza a saída para o handler."""
        return {"text": text, "markup": markup}
    
    # --- Teclados ---
    def _get_civ_keyboard(self):
        '''Gera um teclado com as civilizações disponíveis para escolha.'''
        keys = []
        for text in txt.CIV_BUTTON:
            keys.append([KeyboardButton(text=text)])
        return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True, one_time_keyboard=True)

    def _get_strategy_keyboard(self):
        '''Gera um teclado com as estratégias disponíveis para a IA.'''
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Dumb"), KeyboardButton(text="Rusher")],
            [KeyboardButton(text="Turtle"), KeyboardButton(text="Greedy")],
            [KeyboardButton(text="Aleatório")]
        ], resize_keyboard=True, one_time_keyboard=True)

    def _get_main_keyboard(self):
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="🏗️ Construções"), KeyboardButton(text="🔬 Pesquisar")],
            [KeyboardButton(text=f"{txt.ACTION_TRIGGER['army']} Exército"), KeyboardButton(text=f"{txt.ACTION_TRIGGER['attack']} ATACAR")],
            [KeyboardButton(text="📊 Status"), KeyboardButton(text="ℹ️ Info")]
        ], resize_keyboard=True)
    
    def _get_build_keyboard(self):
        ''''Gera um teclado para o menu de construção, mostrando quais edificações o jogador pode construir com base em seus recursos atuais.'''
        keys = []
        for label in txt.BUILD_BUTTON(self.player):
            keys.append([KeyboardButton(text=label)])
        keys.append([KeyboardButton(text="⬅️ Voltar")])
        return ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True)

    def _get_research_keyboard(self):
        options = txt.RESEARCH_BUTTONS(self.player)
        # Organiza em 2 colunas para não ficar uma lista gigante
        keyboard = [options[i:i + 2] for i in range(0, len(options), 2)]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    # --- MENUS DE SETUP ---

    def setup_player_civ_menu(self):
        """Primeira etapa: Escolha da civilização do jogador."""
        text = txt.PLAYER_CIV_SELECT
        return self._format(text, self._get_civ_keyboard())

    def setup_ai_civ_menu(self):
        """Segunda etapa: Escolha da civilização do inimigo."""
        text = txt.AI_CIV_SELECT
        return self._format(text, self._get_civ_keyboard())

    def setup_strategy_menu(self):
        """Terceira etapa: Escolha da dificuldade/estratégia da IA."""
        text = txt.STRATEGY_SELECT
        return self._format(text, self._get_strategy_keyboard())
    
    # --- MENUS PRINCIPAIS ---

    def main_menu(self):
        text = txt.MAIN_MENU_MSG(self.player)
        return self._format(text, self._get_main_keyboard())

    def build_menu(self):
        text = txt.BUILD_MENU_MSG(self.player)
        return self._format(text, self._get_build_keyboard())

    def research_menu(self):
        text = txt.RESEARCH_MENU_MSG(self.player)
        return self._format(text, self._get_research_keyboard())

    def status_menu(self):
        text = txt.STATUS_MSG(self.player, self.game.turn_count)
        return self._format(text, self._get_main_keyboard())
    
    def info_menu(self):
        text = txt.INFO_MSG()
        return self._format(text, self._get_main_keyboard())