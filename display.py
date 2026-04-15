import constants as c

PLAYER_CIV_SELECT = f"Saudações, Soberano! 🏰\n\nEscolha a sua Civilização:"
AI_CIV_SELECT = "Ótima escolha! Agora, qual será a Civilização do Inimigo?"
STRATEGY_SELECT = "E qual será a postura estratégica do oponente?"
def WAR_START(p_civ, a_civ, strategy):
    texto = (
        "🚩 **GUERRA DECLARADA!**\n\n"
        f"Sua Civ: *{c.CIVS[p_civ]['label']}*\n"
        f"Inimigo: *{c.CIVS[a_civ]['label']}*\n"
        f"Estratégia: *{strategy}*\n"
    )
    return texto

def STATUS_MSG(player, turn):
    texto = (
        f"👑 **STATUS DO REINO DE {player.user_name}**\n" # Kingdom usa user_name
        f"Civilização: *{c.CIVS[player.civ]['label']}*\n"
        f"❤️ Vida: {player.life}\n" # Kingdom usa life, não recursos
        f"🍎 Comida: {player.food}\n"
        f"⚔️ Exército: {player.army}\n"
        f"🌱 Fazendas: {player.farms}\n"
        f"📅 Turno: {turn}\n"
    )
    return texto

NO_ACTIVE_GAME = "⚠️ Não há um jogo ativo. Use /start para iniciar uma nova partida."

def TURN_REPORT_INTRODUCTION(turn):
    return f"📅 **RELATÓRIO DO TURNO {turn}**\n\n"

def ACTION_FEEDBACK(report):
    return  f"Sua ação: *{report['player_action']}*\n"

def FIGHT_FEEDBACK(report):
    fd = report["fight_data"]
    sit = fd["situation"]
    is_invasion = "is_over" in fd
    
    # RESOLUÇÃO: Inicializar a variável antes de concatenar
    feedback = ""

    if not is_invasion:
        feedback += f"\n💥 **CONFLITO EM CAMPO ABERTO!**\n"
        # Mostrando dados do inimigo (Requisito anterior)
        feedback += f"⚔️ Força inimiga: {fd.get('weak_start_army') or 'Desconhecida'}\n"
    else:
        target = "seu reino" if report["ai_action"] == "attack" and report['player_action'] != "attack" else "reino inimigo"
        feedback += f"\n🏰 **INVASÃO DETECTADA!**\n"
        feedback += f"Alvo: *{target}*\n"
        # Mostrando dados de exército e vida no cerco
        feedback += f"⚔️ Força atacante: {fd.get('attacker_start_army')}\n"
        feedback += f"🛡️ Força defensora: {fd.get('defender_start_army')}\n"

    sit_map = {
        'draw': "⚖️ *Empate!* Ambos os exércitos foram dizimados.",
        'costly_win': "⚠️ *Vitória sofrida!* Você manteve o campo por pouco.",
        'true_win': "🏆 *Vitória total!* O inimigo recuou em pânico.",
        'full_block': "🛡️ *Defesa impenetrável!* O ataque não surtiu efeito.",
        'costly_block': "🩸 *Batalha sangrenta nas muralhas!*",
        'pilhage': "🔥 *MURALHAS INVADIDAS!* A cidade está sendo saqueada!",
        'complete_destruction': "💥 *ANIQUILAÇÃO!* A cidade foi reduzida a cinzas!"
    }
    feedback += f"📢 **DESFECHO:** {sit_map.get(sit)}\n"
    return feedback # Não esqueça de retornar a string!

VICTORY = "🏆 **VITÓRIA SUPREMA!**"
FAILURE = "💀 **DERROTA TOTAL...**"