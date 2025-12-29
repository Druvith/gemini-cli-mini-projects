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
        to_sell = max(0, self.inventory[self.crop] - 2) # Keep some for seeds/self if applicable
        if to_sell > 0:
            revenue = to_sell * market_state.prices[self.crop]
            self.cash += revenue
            self.inventory[self.crop] -= to_sell
            return f"{self.name} harvested {yield_amt} {self.crop.value} and sold {to_sell} for ₹{revenue:.2f}"
            
        return f"{self.name} harvested {yield_amt} {self.crop.value}"

class DarshiniOwner(Agent):
    def __init__(self, name: str):
        super().__init__(name, Region.BENGALURU, {Resource.IDLI_SET: 0, Resource.RICE: 10, Resource.COFFEE: 5}, cash=2000.0)

    def act(self, market_state: MarketState) -> str:
        # Production Recipe: 1 Rice + 0.2 Coffee -> 5 Idli Sets
        
        # 1. Buy Raw Materials if low
        if self.inventory[Resource.RICE] < 5:
            cost = market_state.prices[Resource.RICE] * 10
            if self.cash >= cost:
                self.cash -= cost
                self.inventory[Resource.RICE] += 10
        
        if self.inventory[Resource.COFFEE] < 2:
            cost = market_state.prices[Resource.COFFEE] * 5
            if self.cash >= cost:
                self.cash -= cost
                self.inventory[Resource.COFFEE] += 5

        # 2. Produce
        produced = 0
        if self.inventory[Resource.RICE] >= 1 and self.inventory[Resource.COFFEE] >= 0.2:
            self.inventory[Resource.RICE] -= 1
            self.inventory[Resource.COFFEE] -= 0.2
            produced = 5
            self.inventory[Resource.IDLI_SET] += produced

        return f"{self.name} cooked {produced} Idli Sets."

class Techie(Agent):
    def __init__(self, name: str):
        super().__init__(name, Region.BENGALURU, {Resource.CODE: 0, Resource.IDLI_SET: 0, Resource.FLOWERS: 0}, cash=5000.0)
    
    def act(self, market_state: MarketState) -> str:
        # 1. Work (Earn Salary)
        salary = 2000 # Daily wage
        self.cash += salary
        
        # 2. SURVIVAL: Buy Idli Set (Breakfast)
        idli_price = market_state.prices[Resource.IDLI_SET]
        bought_food = False
        if self.cash >= idli_price:
            self.cash -= idli_price
            self.inventory[Resource.IDLI_SET] += 1
            bought_food = True
        
        # 3. LUXURY: Buy Flowers (Only if rich enough)
        # The Ripple Effect: If Idli was expensive, they might skip this.
        flower_price = market_state.prices[Resource.FLOWERS]
        bought_flowers = 0
        
        # Techie feels "Rich" if they have > ₹5000 cash
        if bought_food and self.cash > 5000: 
            # Buy flowers for the festival or just decor
            if self.cash >= flower_price:
                self.cash -= flower_price
                self.inventory[Resource.FLOWERS] += 1
                bought_flowers = 1
                
        action_log = f"{self.name} ate Idli (₹{idli_price:.0f})."
        if bought_flowers:
            action_log += f" Bought Flowers (₹{flower_price:.0f})."
        else:
            action_log += " Too broke for Flowers!"
            
        return action_log
