import constants as consts

class Kingdom:
    def __init__(self, user_id, user_name, data=None):
        self.user_id = user_id
        self.user_name = user_name

        if data:
            self.life = data.get('life', consts.INITIAL_LIFE)
            self.civ = data.get('civ', 'Teresópolis')
            
            # AGRUPAMENTO DE RECURSOS
            self.resources = data.get('resources', {
                "food": consts.INITIAL_FOOD,
                "wood": consts.INITIAL_WOOD,
            })
            self.buildings = data.get('buildings', consts.INITIAL_BUILDINGS.copy())
            self.army = data.get('army', consts.INITIAL_ARMY)

        else:
            # Inicialização para novo jogo
            self.life = consts.INITIAL_LIFE
            self.civ = 'Teresópolis'
            self.resources = {
                "food": consts.INITIAL_FOOD, 
                "wood": consts.INITIAL_WOOD,
                }
            self.buildings = consts.INITIAL_BUILDINGS.copy()
            self.army = consts.INITIAL_ARMY

    @property
    def occupied_slots(self):
        return sum(
            self.buildings.get(b, 0) * consts.BUILDINGS.get(b, {}).get('slots', 0) 
            for b in self.buildings
        )

    @property
    def total_slots(self):
        return consts.INITIAL_SLOTS + (self.buildings['casa'] * consts.SLOTS_PER_HOUSE)
    
    @property
    def FARM_PROD_BONUS(self):
        modifier = consts.CIVS.get(self.civ, {}).get('mods', {}).get('food_production', 1.0)
        return consts.BUILDINGS['fazenda']['effect_value'] * modifier
    
    @property
    def WOOD_PROD_BONUS(self):
        modifier = consts.CIVS.get(self.civ, {}).get('mods', {}).get('wood_production', 1.0)
        return consts.BUILDINGS['serraria']['effect_value'] * modifier
    
    @property
    def ARMY_COST(self):
        modifier = consts.CIVS.get(self.civ, {}).get('mods', {}).get('army_cost', 1.0)
        return int(consts.ARMY_COST * modifier)

    def to_dict(self):
        """Transforma as informações contidas na instância em um dicionário"""
        return {
            "user_name": self.user_name,
            "life": self.life,
            "buildings": self.buildings,
            "resources": self.resources,
            "army": self.army,
            "civ": self.civ,
        }
    
    def produce_resources(self):
        """O Recurso aumenta += Farms"""
        self.resources['food']+= int(self.buildings['fazenda'] * self.FARM_PROD_BONUS)
        self.resources['wood'] += int(self.buildings['serraria'] * self.WOOD_PROD_BONUS)

    def build(self, building_type):
        if building_type not in consts.BUILDINGS:
            return False

        cost = consts.BUILDINGS[building_type]

        needs_slot = cost.get('slots', 0) > 0
        if needs_slot and self.occupied_slots >= self.total_slots:
            return False
        
        if (self.resources["food"] >= cost["food_cost"] and
            self.resources["wood"] >= cost["wood_cost"]):

            self.resources["food"] -= cost["food_cost"]
            self.resources["wood"] -= cost["wood_cost"]
            self.buildings[building_type] += 1
            return True
        return False

    def train_army(self):
        # Quantidade máxima que os quarteis aguentam
        capacidade = int(consts.TRAIN_CAP_PER_QUARTEL * self.buildings['quartel'])
        custo_total = capacidade * self.ARMY_COST
    
        if capacidade > 0 and self.resources["food"] >= custo_total:
            self.army += capacidade
            self.resources["food"] -= custo_total
            return True
        return False

class CombatEngine:
    def __init__(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender
        # Cache dos dados ANTES do combate para o relatório
        self.stats_pre = {
            "a_army": attacker.army,
            "d_army": defender.army,
            "d_life": defender.life
        }

    def resolve(self, type="invasion"):
        if type == "open_field":
            return self._open_field_clash()
        return self._invasion_clash()

    def _open_field_clash(self):
        if self.attacker.army >= self.defender.army:
            strong, weak = self.attacker, self.defender
        else:
            strong, weak = self.defender, self.attacker

        R = strong.army / max(1, weak.army)
        
        if R <= consts.OPEN_CRITICALRATIO:
            s_loss = (consts.OPEN_BASELOSS - consts.OPEN_RESIDUALLOSS) * \
                     (consts.OPEN_CRITICALRATIO**2 - R**2) / (consts.OPEN_CRITICALRATIO**2 - 1) + \
                     consts.OPEN_RESIDUALLOSS
            w_loss = (consts.OPEN_BASELOSS - 1) * (consts.OPEN_CRITICALRATIO**2 - R**2) / \
                     (consts.OPEN_CRITICALRATIO**2 - 1) + 1
            sit = 'draw' if R == 1 else 'costly_win'
        else:
            s_loss = max(0, consts.OPEN_RESIDUALLOSS * (consts.OPEN_DOMINANCERATIO - R) / \
                     (consts.OPEN_DOMINANCERATIO - consts.OPEN_CRITICALRATIO))
            w_loss = 1.0
            sit = 'true_win'

        # Aplicar baixas
        strong.army = int(strong.army * (1 - s_loss))
        weak.army = int(weak.army * (1 - w_loss))

        # Identificar perdas específicas para o report (quem é atacante/defensor)
        if strong == self.attacker:
            a_loss, d_loss = s_loss, w_loss
        else:
            a_loss, d_loss = w_loss, s_loss

        return self._generate_report(sit, a_loss, d_loss)

    def _invasion_clash(self):
        mod_wall = consts.CIVS.get(self.defender.civ, {}).get('mods', {}).get('wall_defense', 1.0)
        eff_defense = consts.DEFENSE * mod_wall
        
        low_t = eff_defense + self.defender.army * consts.SIEGE_LOWBLOCKFACTOR
        high_t = eff_defense + self.defender.army * consts.SIEGE_HIGHBLOCKFACTOR
        
        a_loss, d_loss, sit = 0, 0, ""

        if self.attacker.army <= low_t:
            a_loss, d_loss, sit = consts.SIEGE_ATTACKERLOSS, 0, 'full_block'
        elif self.attacker.army < high_t:
            a_loss = consts.SIEGE_ATTACKERLOSS * (high_t - self.attacker.army) / (high_t - low_t)
            d_loss = consts.SIEGE_BLOCKLOSS * (self.attacker.army - low_t) / (high_t - low_t)
            sit = 'costly_block'
        else:
            if self.defender.army > 0 and (self.attacker.army / self.defender.army) < consts.PILHAGE_DOMINANCERATIO:
                a_loss, d_loss = consts.PILHAGE_BASELOSS, consts.PILHAGE_BASELOSS
                mod_dmg = consts.CIVS.get(self.defender.civ, {}).get('mods', {}).get('pilhage_damage', 1.0)
                damage = consts.PILHAGE_DAMAGEFACTOR * self.attacker.army * (1 - a_loss) * mod_dmg
                self.defender.life = int(max(0, self.defender.life - damage))
                sit = 'pilhage'
            else:
                a_loss, d_loss, sit = 0, 1.0, 'complete_destruction'
                self.defender.life = 0

        self.attacker.army = int(self.attacker.army * (1 - a_loss))
        self.defender.army = int(self.defender.army * (1 - d_loss))

        return self._generate_report(sit, a_loss, d_loss, is_invasion=True)

    def _generate_report(self, situation, a_loss, d_loss, is_invasion=False):
        report = {
            "situation": situation,
            "attacker_start_army": self.stats_pre["a_army"],
            "defender_start_army": self.stats_pre["d_army"],
            "defender_start_life": self.stats_pre["d_life"],
            "attacker_loss": a_loss,
            "defender_loss": d_loss
        }
        if is_invasion: 
            report["is_over"] = self.defender.life <= 0
            report["defender_final_life"] = self.defender.life
        return report