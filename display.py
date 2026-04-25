import constants as c

# --- MENSAGENS DE INTERFACE ---

ACTION_TRIGGER = {
            'army': "⚔️",
            'attack': "🚩",
            'build': "🔨",
            'research': "🧪",
        }

PLAYER_CIV_SELECT = f"Saudações, Soberano! 🏰\n\nEscolha a sua Civilização:"
AI_CIV_SELECT = "Ótima escolha! Agora, qual será a Civilização do Inimigo?"
STRATEGY_SELECT = "E qual será a postura estratégica do oponente?"

CIV_BUTTON = [f"{info['label']} - {info['bonus']}" for name, info in c.CIVS.items()]

def BUILD_BUTTON(player):
    '''Gera os botões de construção com ícones de disponibilidade'''
    button = []
    for building_name, info in c.BUILDINGS.items():

        icon = "🔨" if player.can_build(building_name) else "🚫"
        text = f"{icon} {info['label']} (🍎{info['food_cost']} 🪵{info['wood_cost']})"
        button.append(text)
    return button

def RESEARCH_BUTTONS(player):
    '''Gera os botões de pesquisa com ícones de disponibilidade'''
    buttons = []
    for t_id, info in c.TECHNOLOGIES.items():

        if t_id not in player.searched_techs:
            has_root = player.buildings.get(info['root_building'], 0) > 0
            has_reqs = all(r in player.searched_techs for r in info.get('requisities', []))
            
            if has_root and has_reqs:
                icon = "🧪" if player.resources.get('gold', 0) >= info['gold_cost'] else "🚫"
                buttons.append(f"{icon} {info['label']}")
    
    buttons.append("⬅️ Voltar")
    return buttons

def WAR_START(p_civ, a_civ, strategy):
    '''Gera a mensagem de início de guerra com detalhes da configuração escolhida'''
    texto = (
        "🚩 **GUERRA DECLARADA!**\n\n"
        f"Sua Civ: *{c.CIVS[p_civ]['label']}*\n"
        f"Inimigo: *{c.CIVS[a_civ]['label']}*\n"
    )
    return texto

def MAIN_MENU_MSG(player):
    '''Gera a mensagem do menu principal com detalhes dos recursos e opções disponíveis'''
    texto = (
        "🏰 **MENU PRINCIPAL**\n\n"
        f"Recursos: 🍎 {player.resources['food']} | 🪵 {player.resources['wood']} | 💰 {player.resources.get('gold', 0)}\n"
        f"Espaço: 🏘️ {player.occupied_slots}/{player.total_slots}\n"
        "────────────────────\n"
        "O que deseja fazer?"
    )
    return texto

def BUILD_MENU_MSG(player):
    '''Gera a mensagem do menu de construção com detalhes dos recursos e espaço'''
    texto = (
        "🏗️ **CANTEIRO DE OBRAS**\n\n"
        f"Recursos: 🍎 {player.resources['food']} | 🪵 {player.resources['wood']} | 💰 {player.resources.get('gold', 0)}\n"
        f"Espaço: 🏘️ {player.occupied_slots}/{player.total_slots}\n"
        "────────────────────\n"
    )

    texto += "Escolha o que deseja edificar:"
    return texto

def RESEARCH_MENU_MSG(player):
    '''Gera a mensagem do menu de pesquisa com detalhes dos recursos e tecnologias disponíveis'''
    texto = (
        "🔬 **CENTRO DE PESQUISAS**\n\n"
        f"Tesouro: 💰 {player.resources.get('gold', 0)} ouro\n"
        "────────────────────\n"
    )
    
    for t_id, info in c.TECHNOLOGIES.items():
        if player.can_research(t_id) or (t_id not in player.searched_techs and 
            player.buildings.get(info['root_building'], 0) > 0):
            status = "✅ Já pesquisado" if t_id in player.searched_techs else f"💰 Custo: {info['gold_cost']}"
            texto += f"*{info['label']}*\n└ {info['description']}\n_{status}_\n\n"
            
    return texto + "O que deseja descobrir?"

def STATUS_MSG(player, turn):
    '''Gera a mensagem de status do reino com detalhes dos recursos, exército e construções'''
    texto = (
        f"👑 **REINO DE {player.user_name}**\n"
        f"🏛️ Civilização: *{c.CIVS[player.civ]['label']}*\n"
        f"📅 Turno: {turn}\n"
        f"────────────────────\n"
        f"❤️ Integridade: {player.life}/{c.INITIAL_LIFE}\n"
        f"⚔️ Força Militar: {player.army} soldados\n"
        f"────────────────────\n"
        f"🍎 Comida: {player.resources['food']}\n"
        f"🪵 Madeira: {player.resources['wood']}\n"
        f"💰 Ouro: {player.resources.get('gold', 0)}\n"
        f"🏘️ Slots: {player.occupied_slots}/{player.total_slots}\n"
        f"────────────────────\n"
        f"🏠 Casas: {player.buildings.get('casa', 0)} | "
        f"🧱 Muros: {player.buildings.get('muro', 0)}\n"
        f"────────────────────\n"
        f"🌱 Fazendas: {player.buildings.get('fazenda', 0)} | "
        f"🪚 Serrarias: {player.buildings.get('serraria', 0)} |"
        f"🛒 Mercado: {player.buildings.get('mercado', 0)} |\n "
        f"🛖 Quarteis: {player.buildings.get('quartel', 0)} |\n"
        f"\n────────────────────\n"
        f"Arsenal: {player.buildings.get('arsenal', 0)} |"
        f"Moinho: {player.buildings.get('moinho', 0)} |" 
        f"Casa de construção: {player.buildings.get('casa de construção', 0)}\n"
        f"🔬 Tecnologias Pesquisadas: {', '.join([c.TECHNOLOGIES[t]['label'] for t in player.searched_techs]) or 'Nenhuma'}\n"
    )
    return texto

def INFO_MSG():
    '''Gera a mensagem de informações gerais sobre o jogo, incluindo detalhes das civilizações, construções e tecnologias disponíveis.'''
    texto = "📚 **SOBRE AS CONSTRUÇÕES**\n\n"

    for b_id, info in c.BUILDINGS.items():
        texto += f"*{info['label']}*\n"
        texto += f"└ {info['description']}\n\n"

    texto += "📖 **SOBRE AS TECNOLOGIAS**\n\n"

    for t_id, info in c.TECHNOLOGIES.items():
        texto += f"*{info['label']}*\n"
        texto += f"└ {info['description']}\n\n"
        texto += f"_Requisitos: {', '.join(c.TECHNOLOGIES[t_id].get('requisities', [])) or 'Nenhum'}_\n\n"
        texto += f"_Construção raiz: {c.BUILDINGS[info['root_building']]['label']}}}_\n\n"

    return texto
NO_ACTIVE_GAME = "⚠️ Não há um jogo ativo. Use /start para iniciar uma nova partida."

# --- RELATÓRIOS DE TURNO ---

def TURN_REPORT_INTRODUCTION(turn):
    '''Gera a introdução do relatório de turno, destacando o número do turno e preparando o jogador para os detalhes que virão a seguir, com um formato claro e visualmente atraente.'''
    return f"📅 **RELATÓRIO DO TURNO {turn}**\n\n"

def ACTION_FEEDBACK(report):
    '''Gera o feedback detalhado da ação do jogador, incluindo o resultado da construção, recrutamento ou ataque, com ícones e mensagens claras para cada tipo de ação e seu sucesso ou falha.'''
    p_act = report.get('player_action', {})
    if not p_act: return ""
    
    feedback = ""
    if p_act.get('type') == 'build':
        target = p_act.get('target')
        label = c.BUILDINGS.get(target, {}).get('label', target)
        if p_act.get('success'):
            feedback = f"✅ **Sucesso!** A construção de *{label}* foi concluída."
        else:
            feedback = f"❌ **Falha!** Recursos ou Slots insuficientes para *{label}*."
            
    elif p_act.get('type') == 'army':
        if p_act.get('success'):
            feedback = "⚔️ **Recrutamento:** Novos soldados se juntaram às suas fileiras."
        else:
            feedback = "🍎 **Falha!** Impossível treinar soldados."
            
    elif p_act.get('type') == 'attack':
        if p_act.get('success'):
            feedback = "🏹 **Ofensiva:** Suas tropas marcharam para o combate!"
        else:
            feedback = "🚫 **Cancelado:** Você não tem soldados para atacar."

    return feedback

def AI_ACTION_FEEDBACK(report):
    '''Gera o feedback detalhado da ação da IA, interpretando as ações tomadas pelo inimigo durante o turno e fornecendo ao jogador informações claras sobre o que a IA fez, como construções, recrutamentos ou ataques, para que ele possa entender melhor a situação do jogo.'''
    ai_act = report.get('ai_action', {})
    if not ai_act: return ""
    
    feedback = ""
    if ai_act.get('type') == 'build':
        if ai_act.get('success'):
            target = ai_act.get('target')
            label = c.BUILDINGS.get(target, {}).get('label', target)
            feedback = f"🏗️ **Inimigo construiu:** O oponente erigiu um *{label}*."
        else:
            feedback = "🚫 **Inimigo falhou na construção:** O inimigo tentou construir algo, mas não conseguiu."

    elif ai_act.get('type') == 'army':
        if ai_act.get('success'):
            feedback = "⚔️ **Inimigo recrutou:** O inimigo reforçou suas tropas!"
        else:
            feedback = "🍎 **Inimigo falhou no recrutamento:** Parece que o inimigo teve dificuldades para recrutar soldados."
        
    elif ai_act.get('type') == 'attack':
        if ai_act.get('success'):
            feedback = "⚠️ **Inimigo atacou!** Prepare-se para a batalha!"
        else:
            feedback = "🚫 **Inimigo falhou no ataque:** O inimigo tentou atacar, mas não conseguiu."

    return feedback

def FIGHT_FEEDBACK(report):
    fd = report.get("fight_data")
    if not fd: return ""

    sit = fd.get("situation")
    
    # Lógica corrigida para identificar quem atacou quem
    p_atk = report['player_action'].get('type') == 'attack' and report['player_action'].get('success')
    ai_atk = report['ai_action'].get('type') == 'attack' and report['ai_action'].get('success')

    feedback = ""

    if p_atk and ai_atk:
        feedback += f"\n💥 **CONFLITO EM CAMPO ABERTO!**\n"
        feedback += f"⚔️ Seu exército: {fd.get('attacker_start_army')}\n"
        feedback += f"⚔️ Exército inimigo: {fd.get('defender_start_army')}\n"
    elif p_atk:
        feedback += f"\n🏰 **VOCÊ INVADIU O INIMIGO!**\n"
        feedback += f"⚔️ Seu exército: {fd.get('attacker_start_army')}\n"
        feedback += f"🛡️ Defesa deles: {fd.get('defender_start_army')} soldados + Muros\n"
    else:
        feedback += f"\n🏰 **SEU REINO FOI INVADIDO!**\n"
        feedback += f"⚔️ Atacantes: {fd.get('attacker_start_army')}\n"
        feedback += f"🛡️ Sua defesa: {fd.get('defender_start_army')} soldados + Muros\n"

    sit_map = {
        'draw': "⚖️ *Empate!* Ambos os exércitos foram dizimados.",
        'costly_win': "⚠️ *Vitória sofrida!* Você manteve o campo por pouco.",
        'true_win': "🏆 *Vitória total!* O inimigo recuou em pânico.",
        'costly_defeat': "❌ *Derrota amarga!* Suas tropas recuaram pesadamente.",
        'total_defeat': "💀 *Massacre!* Seu exército foi aniquilado em campo.",
        'full_block': "🛡️ *Defesa impenetrável!* O ataque foi repelido sem baixas no reino.",
        'costly_block': "🩸 *Batalha sangrenta nas muralhas!* O muro segurou, mas houve perdas.",
        'pilhage': "🔥 *MURALHAS INVADIDAS!* A cidade está sendo saqueada!",
        'complete_destruction': "💥 *ANIQUILAÇÃO!* A cidade foi reduzida a cinzas!"
    }
    
    res_text = sit_map.get(sit, "O combate terminou de forma incerta...")
    feedback += f"📢 **DESFECHO:** {res_text}\n"
    feedback += f"📉 Perdas: O atacante perdeu {int(fd['attacker_loss']*fd['attacker_start_army'])} soldados. O defensor perdeu {int(fd['defender_loss']*fd['defender_start_army'])} soldados.\n"
    if fd['is_invasion']:
        feedback += f"🏚️ Dano à cidade: {fd.get('defender_damage_taken', 0)}\n"
    
    if fd.get('defender_damage_taken', 0) > 0:
        alvo = "Inimigo" if p_atk else "Seu reino"
        feedback += f"🏚️ **Dano:** {alvo} perdeu {fd['defender_damage_taken']} de integridade.\n"
        
    return feedback

VICTORY = "🏆 **VITÓRIA SUPREMA!** O reino inimigo caiu!"
FAILURE = "💀 **DERROTA TOTAL...** Seu povo foi subjugado."