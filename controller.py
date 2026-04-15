from models import Kingdom, CombatEngine
from db_utils import get_db, save_db
import constants as consts
import AI_logic
from random import choice

class Game:
    '''Controla o estado do jogo para um usuário específico, incluindo os reinos do jogador e da IA, o número de turnos, a estratégia da IA e o status do jogo. Fornece métodos para configurar o jogo, processar os turnos e verificar condições de vitória.'''
    def __init__(self, user_id, user_name):
        '''Inicializa o jogo para um usuário, carregando o estado do jogo do banco de dados se existir, ou criando um novo estado se for um novo jogador. Garante que os reinos sejam corretamente configurados com base nas civilizações escolhidas e que a estratégia da IA seja definida.'''
        self.user_id = str(user_id)
        self.user_name = user_name
        self.db_data = get_db('games_data')

        user_data = self.db_data.get(self.user_id)
        ai_data = self.db_data.get(f"{self.user_id}_ai")

        if not user_data:
            self.turn_count = 1
            self.status = "active"
            self.ai_strategy = choice(['dumb', 'rusher', 'turtle', 'greedy'])
            # NOVA FILA DE TÁTICAS
            self.ai_current_plan = [] 
            
            self.player = Kingdom(self.user_id, user_name)
            self.ai = Kingdom(f"{self.user_id}_ai", f"IA ({self.ai_strategy})")
            self.ai.civ = choice(list(consts.CIVS.keys()))
        else:
            self.turn_count = user_data.get('turn_count', 1)
            self.status = user_data.get('status', 'active')
            self.ai_strategy = user_data.get('ai_strategy', 'dumb')
            # RECUPERA A FILA DO BANCO
            self.ai_current_plan = user_data.get('ai_current_plan', [])
            
            self.player = Kingdom(self.user_id, user_name, data=user_data)
            self.ai = Kingdom(f"{self.user_id}_ai", f"IA ({self.ai_strategy})", data=ai_data)

    def save(self):
        '''Salva o estado atual do jogo no banco de dados, incluindo os dados do jogador, da IA, o número de turnos, a estratégia da IA e a fila de táticas atual. Garante que todas as informações relevantes sejam armazenadas para que o jogo possa ser retomado posteriormente.'''
        player_data = self.player.to_dict()
        player_data['turn_count'] = self.turn_count
        player_data['status'] = self.status
        player_data['ai_strategy'] = self.ai_strategy
        # SALVA A FILA ATUAL
        player_data['ai_current_plan'] = self.ai_current_plan

        self.db_data[self.user_id] = player_data
        self.db_data[f"{self.user_id}_ai"] = self.ai.to_dict()
        save_db('games_data', self.db_data)

    def setup(self, player_civ="Teresópolis", ai_civ="Petrópolis", strategy="Aleatório"):
        '''Configura o jogo para um novo usuário, definindo as civilizações do jogador e da IA, bem como a estratégia da IA. Garante que os reinos sejam criados com os bônus e modificadores corretos de acordo com as civilizações escolhidas. Salva o estado inicial do jogo no banco de dados.'''
        # Garante que criamos reinos limpos com a civ correta
        self.player = Kingdom(self.user_id, self.user_name)
        self.player.civ = player_civ
    
        self.ai = Kingdom(f"{self.user_id}_ai", "Bot")
        self.ai.civ = ai_civ
    
        self.turn_count = 1
        self.status = "active"
    
        # Tratamento da estratégia
        if strategy == "Aleatório":
            self.ai_strategy = choice(['dumb', 'rusher', 'turtle', 'greedy'])
        else:
            self.ai_strategy = strategy.lower()
        
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
        self.player.produce_resources()
        self.ai.produce_resources()

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
            if self.player.build(a_target):
                action['success'] = True
        elif a_type == "army":
            if self.player.train_army():
                action['success'] = True
        elif a_type == "attack":
            if self.player.army > 0:
                action['success'] = True
        
        return action

    def process_ai_turn(self):
        """
        Gerencia a fila de táticas da IA. Se não houver plano, pede um novo 
        para a AI_logic baseado na estratégia.
        """
        # 1. Se não há plano, consulta a estratégia para gerar uma sequência (lista)
        if not self.ai_current_plan:
            # Chama a função principal do AI_logic que redireciona para a estratégia correta
            new_sequence = AI_logic.get_ai_tactic(self.ai_strategy, self.ai)
            self.ai_current_plan = new_sequence

        # 2. Retira a primeira ação da fila (FIFO)
        # Cada item da sequência é algo como: ['build', 'casa'] ou ['army', 'train_army']
        current_step = self.ai_current_plan.pop(0)
        
        a_type = current_step[0]
        a_target = current_step[1] if len(current_step) > 1 else None

        ai_action = {
            'type': a_type, 
            'target': a_target, 
            'success': False,
            'plan_remaining': len(self.ai_current_plan) # Para debug/log se quiser
        }

        # 3. Tenta executar
        if a_type == "build":
            if self.ai.build(a_target):
                ai_action['success'] = True
        elif a_type == "army":
            if self.ai.train_army():
                ai_action['success'] = True
        elif a_type == "attack":
            # A IA só gasta o turno de ataque se tiver exército
            if self.ai.army > 0:
                ai_action['success'] = True
        
        # 4. Se a ação falhou (falta de recurso), podemos devolver ela para o topo da fila
        # para a IA tentar novamente no próximo turno.
        if not ai_action['success'] and a_type != "attack":
            self.ai_current_plan.insert(0, current_step)

        return ai_action

    def process_fight(self, player_action, ai_action):
        """Simulação de combate"""
        p_true_attack = player_action['type'] == "attack" and player_action['success']
        ai_true_attack = ai_action['type'] == "attack" and ai_action['success']

        if p_true_attack and ai_true_attack:
            # Caso 1: Ambos atacam -> Campo Aberto
            engine = CombatEngine(self.player, self.ai)
            return engine.resolve(type="open_field")
            
        elif p_true_attack:
            # Caso 2: Só jogador ataca -> Invasão à IA
            engine = CombatEngine(self.player, self.ai)
            return engine.resolve(type="invasion")
            
        elif ai_true_attack:
            # Caso 3: Só IA ataca -> Invasão ao Jogador
            engine = CombatEngine(self.ai, self.player)
            return engine.resolve(type="invasion")

        return None
    
    def _check_victory_conditions(self):
        if self.player.life <= 0:
            self.status = "ai_won"
        elif self.ai.life <= 0:
            self.status = "player_won"
        return
