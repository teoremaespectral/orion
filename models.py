from constants import BUILDING_CATALOG, UNIT_CATALOG, TECHNOLOGY_CATALOG, CIVS, INITIAL_LIFE
from typing import Dict, List, Set
from math import ceil

class Building:
    '''Classe responsável por representar um conjunto de construções do mesmo tipo no reino'''
    
    def __init__(self, building_id: str, quantity: int = 1):
        self.building_id = building_id
        self.quantity = quantity

    @property
    def blueprint(self):
        return BUILDING_CATALOG[self.building_id]

    @property
    def label(self) -> str:
        return self.blueprint.label

    @property
    def icon(self) -> str:
        return self.blueprint.icon
    
    def get_cost(self, modifier: Dict[str, int]) -> Dict[str, int]:
        cost = {}
        base_cost = self.blueprint.cost

        for res_name, base_cost in base_cost.items():
            cost_modifier = modifier.get(f'{res_name}_cost_multiplier', 1.0)
            cost[res_name] = ceil(base_cost * cost_modifier)

        return cost
        
    
    def get_total_slots_occupied(self) -> int:
        return self.blueprint.slots * self.quantity
    
    def get_total_defense(self, modifier) -> int:
        return self.blueprint.defense * self.quantity * modifier
    
    def get_slots_provided(self) -> int:
        if not self.blueprint.is_house:
            return 0
        else:
            return self.blueprint.house_component.slots_provided * self.quantity
        
    @property
    def is_military(self) -> bool:
        return self.blueprint.is_military
    
    @property
    def searches_techs(self) -> bool:
        return self.blueprint.searches_techs
    
    @property
    def produces_resources(self) -> bool:
        return self.blueprint.produces_resources
    
    def get_production(self, modifier: Dict[str, int]) -> Dict[str, int]:
        production = {}
        
        if not self.produces_resources:
            return production

        base_production = self.blueprint.production_component.resources_per_turn

        for res_name, base_value in base_production.items():
            total_produced = base_value * self.quantity
            res_modifier = modifier.get(f'{res_name}_production_multiplier', 1.0)
            production[res_name] = ceil(total_produced * res_modifier)

        return production
    
    @property
    def is_defensive(self) -> bool:
        return self.blueprint.is_defensive

    def __str__(self) -> str:
        return f"{self.icon} {self.label}: {self.quantity}"
    
class Infrastructure:
    ''''''

    def __init__(self):
        self.buildings: Dict[str, Building] = {}

    def add_building(self, building_id: str) -> None:
        if building_id in self.buildings:
            self.buildings[building_id].quantity += 1
        else:
            self.buildings[building_id] = Building(building_id, quantity=1)

    def get_total_slots_available(self) -> int:
        total = 0
        for building in self.buildings.values():
            total += building.get_slots_provided()
        return total
    
    def get_total_slots_occupied(self) -> int:
        return sum(building.get_total_slots_occupied() for building in self.buildings.values())
    
    @property
    def has_free_slots(self) -> bool:
        return self.get_total_slots_occupied() < self.get_total_slots_available()
    
    def get_all_production(self, modifier: Dict[str, float]) -> Dict[str, int]:
        total_production = {}
        
        for building in self.buildings.values():
            building_prod = building.get_production(modifier)
            for res_name, amount in building_prod.items():
                total_production[res_name] = total_production.get(res_name, 0) + amount 
        return total_production
    
    def get_total_wall_defense(self, modifier) -> int:
        return sum(building.get_total_defense(modifier) for building in self.buildings.values() if building.is_defensive)
    
    def __str__(self) -> str:
        if not self.buildings:
            return "🏚️ Nenhuma construção erguida ainda."
            
        lines = [str(building) for building in self.buildings.values()]
        return "\n".join(lines)
    
class Unit:

    def __init__(self, unit_id: str, quantity: int = 1):
        self.unit_id = unit_id
        self.quantity = quantity

    @property
    def blueprint(self):
        return UNIT_CATALOG[self.unit_id]

    @property
    def label(self) -> str:
        return self.blueprint.label

    @property
    def icon(self) -> str:
        return self.blueprint.icon

    @property
    def line(self) -> str:
        return self.blueprint.line

    @property
    def is_infantry(self) -> bool:
        return self.blueprint.is_infantry
    
    @property
    def is_ranged(self) -> bool:
        return self.blueprint.is_ranged
    
    @property
    def is_cavalry(self) -> bool:
        return self.blueprint.is_cavalry
    
    @property
    def is_anti_cavalry(self) -> bool:
        return self.blueprint.is_anti_cavalry
    
    @property
    def is_siege(self) -> bool:
        return self.blueprint.is_siege

    def get_fire_power(self) -> int:
        if not self.is_ranged:
            return 0
        return self.blueprint.ranged_component.ranged_power * self.quantity

    def get_siege_power(self) -> int:
        if not self.is_siege:
            return 0
        return self.blueprint.siege_component.siege_power * self.quantity

    def get_cavalry_power(self) -> int:
        if not self.is_cavalry:
            return 0
        return self.blueprint.cavalry_component.cavalry_power * self.quantity

    def get_anti_cavalry_power(self) -> int:
        if not self.is_anti_cavalry:
            return 0
        return self.blueprint.anti_cavalry_component.anti_cavalry_power * self.quantity

    def get_infantry_power(self) -> int:
        if not self.is_infantry:
            return 0
        return self.blueprint.infantry_component.infantry_power * self.quantity

    def get_total_defense(self) -> int:
        return self.blueprint.defense * self.quantity

    def __str__(self) -> str:
        return f"{self.icon} {self.label}: {self.quantity}"
    

class Army:
    def __init__(self):
        self.units: Dict[str, Unit] = {}

    def add_units(self, unit_id: str, quantity: int) -> None:
        if quantity <= 0:
            return

        if unit_id in self.units:
            self.units[unit_id].quantity += quantity
        else:
            self.units[unit_id] = Unit(unit_id, quantity)

    def remove_units(self, unit_id: str, quantity: int) -> None:
        if unit_id not in self.units or quantity <= 0:
            return

        unit = self.units[unit_id]
        unit.quantity -= quantity

        if unit.quantity <= 0:
            del self.units[unit_id]

class Tech:

    def __init__(self, tech_id: str):
        self.tech_id = tech_id

    @property
    def blueprint(self):
        '''Busca o DNA imutável da tecnologia no catálogo de constantes.'''
        return TECHNOLOGY_CATALOG[self.tech_id]

    @property
    def label(self) -> str:
        return self.blueprint.label

    @property
    def icon(self) -> str:
        return self.blueprint.icon

    @property
    def description(self) -> str:
        return self.blueprint.description

    @property
    def applies_modifiers(self) -> bool:
        return self.blueprint.applies_modifiers

    @property
    def spawns_units(self) -> bool:
        return self.blueprint.spawns_units

    def get_modifier_value(self, modifier_key: str) -> float:
        if not self.applies_modifiers:
            return 1.0

        mods_dict = self.blueprint.mods_component.mods
        return mods_dict.get(modifier_key, 1.0)

    def get_unit_provisions(self) -> Dict[str, int]:
        if not self.spawns_units:
            return {}

        return self.blueprint.unit_provision_component.units

    def __str__(self) -> str:
        return f"{self.icon} {self.label}"

class TechTree:
    def __init__(self):
        self.researched_techs: Dict[str, Tech] = {}

    def is_researched(self, tech_id: str) -> bool:
        return tech_id in self.researched_techs

    def unlock_technology(self, tech_id: str) -> None:
        if not self.is_researched(tech_id):
            self.researched_techs[tech_id] = Tech(tech_id)

    def get_active_modifier(self, modifier_key: str) -> float:
        multiplier = 1.0
        for tech in self.researched_techs.values():
            multiplier *= tech.get_modifier_value(modifier_key)
        return multiplier

class Treasure:
    
    def __init__(self, food: int = 0, wood: int = 0, gold: int = 0):
        self.food = food
        self.wood = wood
        self.gold = gold

    def can_afford(self, costs: Dict[str, int]) -> bool:
        return (self.food >= costs.get('food_cost', 0) and
                self.wood >= costs.get('wood_cost', 0) and
                self.gold >= costs.get('gold_cost', 0))

    def deduct(self, costs: Dict[str, int]) -> bool:
        if not self.can_afford(costs):
            return False

        self.food -= costs.get('food_cost', 0)
        self.wood -= costs.get('wood_cost', 0)
        self.gold -= costs.get('gold_cost', 0)
        return True

    def add_resources(self, resources: Dict[str, int]) -> None:
        self.food += resources.get('food', 0)
        self.wood += resources.get('wood', 0)
        self.gold += resources.get('gold', 0)

    def __str__(self) -> str:
        return f"🍎 Comida: {self.food} | 🪵 Madeira: {self.wood} | 💰 Ouro: {self.gold}"
        

class Kingdom:
    def __init__(self, user_id: str, user_name: str, civ_name: str = "Teresópolis"):
        self.user_id = user_id
        self.user_name = user_name
        self.civ_name = civ_name
        self.life = INITIAL_LIFE

        self.treasure = Treasure()
        self.infrastructure = Infrastructure()
        self.army = Army()
        self.tech_tree = TechTree()

    def get_modifier(self, modifier_key: str) -> float:
        multiplier = self.tech_tree.get_active_modifier(modifier_key)

        return multiplier

    def build(self, building_id: str) -> bool:
        blueprint = BUILDING_CATALOG.get(building_id)
        if not blueprint:
            return False

        if blueprint.slots > 0 and not self.infrastructure.has_free_slots:
            return False

        temp_building = Building(building_id)
        ctx_modifier = {
            'food_modifier': self.get_modifier('food_cost_multiplier'),
            'wood_modifier': self.get_modifier('wood_cost_multiplier'),
            'gold_modifier': self.get_modifier('gold_cost_multiplier')
        }
        calculated_cost = temp_building.get_cost(ctx_modifier)

        if self.treasure.deduct(calculated_cost):
            self.infrastructure.add_building(building_id)
            return True

        return False

    def research(self, tech_id: str) -> bool:
        blueprint = TECHNOLOGY_CATALOG.get(tech_id)
        if not blueprint:
            return False

        built_ids = set(self.infrastructure.buildings.keys())
        if self.tech_tree.get_tech_status(tech_id, built_ids) != "available":
            return False

        cost_dict = {'gold_cost': blueprint.gold_cost}
        
        if self.treasure.deduct(cost_dict):
            self.tech_tree.unlock_technology(tech_id)

            active_tech = self.tech_tree.researched_techs[tech_id]
            if active_tech.spawns_units:
                for unit_id, quantity in active_tech.get_unit_provisions().items():
                    self.army.add_units(unit_id, quantity)
            
            return True

        return False

    def produce_resources(self) -> None:
        ctx_modifier = {
            'food_production_multiplier': self.get_modifier('food_production_multiplier'),
            'wood_production_multiplier': self.get_modifier('wood_production_multiplier'),
            'gold_production_multiplier': self.get_modifier('gold_production_multiplier')
        }
        
        turn_production = self.infrastructure.get_all_production(ctx_modifier)
        self.treasure.add_resources(turn_production)

    def __str__(self) -> str:
        return (
            f"👑 **Soberano:** {self.user_name}\n"
            f"🏛️ **Civilização:** {self.civ_name}\n"
            f"❤️ **Integridade do Reino:** {self.life} HP\n"
            f"────────────────────\n"
            f"💰 **Tesouro Real:**\n{str(self.treasure)}\n\n"
            f"🏘️ **Uso de Espaço:** {self.infrastructure.get_total_slots_occupied()}/{self.infrastructure.get_total_slots_available()} slots\n"
            f"────────────────────\n"
            f"🏗️ **Canteiro de Obras:**\n{str(self.infrastructure)}\n"
            f"────────────────────\n"
            f"💂 **Guarnição das Forças Armadas:**\n{str(self.army)}"
        )