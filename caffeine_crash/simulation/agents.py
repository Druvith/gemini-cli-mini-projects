import random
from abc import ABC, abstractmethod
from typing import Dict
from .models import Resource, Region, MarketState

class Agent(ABC):
    def __init__(self, name: str, region: Region, inventory: Dict[Resource, float], cash: float = 1000.0):
        self.name = name
        self.region = region
        self.inventory = inventory
        self.cash = cash
    
    @abstractmethod
    def act(self, market_state: MarketState) -> str:
        """Perform daily actions: produce, consume, trade."""
        pass

class Farmer(Agent):
    def __init__(self, name: str, region: Region, crop: Resource):
        super().__init__(name, region, {crop: 0, Resource.RAGI: 10}, cash=500.0)
        self.crop = crop

    def act(self, market_state: MarketState) -> str:
        # Production Logic
        yield_amt = 10 if market_state.weather == "Sunny" else 5
        if market_state.weather == "Drought":
            yield_amt = 1
        
        self.inventory[self.crop] = self.inventory.get(self.crop, 0) + yield_amt
        
        # Consumption (Eat Ragi)
        if self.inventory.get(Resource.RAGI, 0) > 0:
            self.inventory[Resource.RAGI] -= 1
        else:
            # Buy Ragi if hungry
            cost = market_state.prices[Resource.RAGI]
            if self.cash >= cost:
                self.cash -= cost
                self.inventory[Resource.RAGI] = self.inventory.get(Resource.RAGI, 0) + 1
        
        # Sell excess crop
        to_sell = max(0, self.inventory[self.crop] - 2) 
        if to_sell > 0:
            revenue = to_sell * market_state.prices[self.crop]
            self.cash += revenue
            self.inventory[self.crop] -= to_sell
            return f"{self.name} harvested {yield_amt} {self.crop.value}."
            
        return f"{self.name} harvested {yield_amt} {self.crop.value}."

class DarshiniOwner(Agent):
    def __init__(self, name: str):
        super().__init__(name, Region.BENGALURU, {Resource.IDLI_SET: 0, Resource.RICE: 10, Resource.COMMERCIAL_COFFEE: 5}, cash=2000.0)

    def act(self, market_state: MarketState) -> str:
        # Production: 1 Rice + 0.2 Coffee -> 5 Idli Sets
        if self.inventory[Resource.RICE] < 5:
            cost = market_state.prices[Resource.RICE] * 10
            if self.cash >= cost:
                self.cash -= cost
                self.inventory[Resource.RICE] += 10
        
        if self.inventory[Resource.COMMERCIAL_COFFEE] < 2:
            cost = market_state.prices[Resource.COMMERCIAL_COFFEE] * 5
            if self.cash >= cost:
                self.cash -= cost
                self.inventory[Resource.COMMERCIAL_COFFEE] += 5

        produced = 0
        if self.inventory[Resource.RICE] >= 1 and self.inventory[Resource.COMMERCIAL_COFFEE] >= 0.2:
            self.inventory[Resource.RICE] -= 1
            self.inventory[Resource.COMMERCIAL_COFFEE] -= 0.2
            produced = 5
            self.inventory[Resource.IDLI_SET] += produced

        return f"{self.name} cooked {produced} Idli Sets."

class Techie(Agent):
    def __init__(self, name: str):
        # Starts with 'Safety Net' amount to simulate an established techie
        super().__init__(name, Region.BENGALURU, {Resource.CODE: 0, Resource.IDLI_SET: 0, Resource.ARTISAN_COFFEE: 0}, cash=40000.0)
        self.savings_target = 50000.0 # The "Sleep well at night" number
    
    def act(self, market_state: MarketState) -> str:
        # 1. Earn Salary (Fixed High Income)
        salary = 3000 
        self.cash += salary
        
        # 2. PAY RENT (First Priority, Inelastic)
        rent = market_state.rent
        self.cash -= rent
        
        # 3. SURVIVAL: Buy Idli Set
        idli_price = market_state.prices[Resource.IDLI_SET]
        bought_food = False
        if self.cash >= idli_price:
            self.cash -= idli_price
            self.inventory[Resource.IDLI_SET] += 1
            bought_food = True
        
        # 4. LUXURY: Artisan Coffee (The "Good Life" Indicator)
        # ONLY bought if cash > Savings Target
        coffee_price = market_state.prices[Resource.ARTISAN_COFFEE]
        bought_coffee = False
        
        if bought_food and self.cash > self.savings_target: 
            if self.cash >= coffee_price:
                self.cash -= coffee_price
                self.inventory[Resource.ARTISAN_COFFEE] += 1
                bought_coffee = True
                
        action_log = f"{self.name}: Paid Rent ₹{rent:.0f}. Ate Idli."
        if bought_coffee:
            action_log += " Sipped Artisan Coffee ☕."
        else:
            action_log += " SAVING MODE (No Coffee)."
            
        return action_log
