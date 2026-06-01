from constants import BUILDING_CATALOG
from typing import Dict, List, Set
from math import ceil

class Building:
    ''''''
    
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
        pass
    
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
        '''Retorna o poder total de interceptação para a Fase de Mergulho.'''
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

