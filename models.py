import constants as consts

class Kingdom:
    def __init__(self, user_id, user_name, data=None):
        self.user_id = user_id
        self.user_name = user_name

        if data:
            self.life = data['life']
            self.farms = data['farms']
            self.food = data['food']
            self.army = data['army']
            self.civ = data['civ']

        else:
            self.life = consts.INITIAL_LIFE
            self.farms = consts.INITIAL_FARMS
            self.food = consts.INITIAL_FOOD
            self.army = consts.INITIAL_ARMY
            self.civ = 'Teresópolis'

    def to_dict(self):
        """Transforma as informações contidas na instância em um dicionário"""
        return {
            "user_name": self.user_name,
            "life": self.life,
            "farms": self.farms,
            "food": self.food,
            "army": self.army,
            "civ": self.civ,
        }
    
    def produce_resources(self):
        """O Recurso aumenta += Farms"""
        mod = consts.CIVS.get(self.civ, {}).get('mods', {}).get('food_production', 1.0)
        self.food += int(self.farms*consts.FARM_PROD_BONUS*mod)

    def build_farm(self):
        if self.food >= consts.FARM_COST:
            self.food -= consts.FARM_COST
            self.farms += consts.FARM_PROD_BONUS
            return True
        return False

    def train_army(self):
        """Converte todos os recursos em exército"""
        if self.food > 0:
            mod = consts.CIVS.get(self.civ, {}).get('mods', {}).get('army_cost', 1.0)
            self.army += int(self.food*mod)
            self.food = 0
            return True
        return False