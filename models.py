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
        food_modifier = modifier.get('food_modifier', 1)
        wood_modifier = modifier.get('wood_modifier', 1)
        gold_modifier = modifier.get('gold_modifier', 1)
        cost = {
            'food_cost' : ceil(self.blueprint.food_cost * food_modifier),
            'wood_cost' : ceil(self.blueprint.wood_cost * wood_modifier),
            'gold_cost' : ceil(self.blueprint.gold_cost * gold_modifier)
        }
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

    def __str__(self) -> str:
        return f"{self.icon} {self.label}: {self.quantity}"