from typing import List
import math
from datetime import timedelta
import random
from .models import MarketState, Resource, Region, Season
from .agents import Agent, Farmer, Techie, DarshiniOwner

class MarketEngine:
    def __init__(self):
        self.state = MarketState()
        self.agents: List[Agent] = self._init_agents()
        self.logs: List[str] = []

    def _init_agents(self) -> List[Agent]:
        agents = []
        # Mandya Farmers
        for i in range(5):
            agents.append(Farmer(f"Raitha-{i}", Region.MANDYA, Resource.RAGI))
        
        # Coorg Planters
        for i in range(3):
            agents.append(Farmer(f"Planter-{i}", Region.COORG, Resource.COFFEE))
            
        # Bengaluru Techies
        for i in range(5):
            agents.append(Techie(f"Dev-{i}"))

        # Darshinis
        for i in range(3):
            agents.append(DarshiniOwner(f"Darshini-{i}"))
            
        return agents

    def update_season_and_weather(self):
        month = self.state.date.month
        
        # Determine Season based on Month
        new_season = Season.WINTER
        if 3 <= month <= 5:
            new_season = Season.SUMMER
        elif 6 <= month <= 9:
            new_season = Season.MONSOON
        elif 10 <= month <= 12:
            new_season = Season.POST_MONSOON
        
        if new_season != self.state.season:
            self.state.season = new_season
            self.state.headline = f"SEASON CHANGE: {new_season.value} has arrived!"

        # Determine Weather based on Season
        weights = []
        if self.state.season == Season.MONSOON:
            weights = ["Rainy"] * 70 + ["Cloudy"] * 20 + ["Sunny"] * 10
        elif self.state.season == Season.SUMMER:
            weights = ["Sunny"] * 80 + ["Drought"] * 15 + ["Rainy"] * 5
        elif self.state.season == Season.WINTER:
            weights = ["Sunny"] * 60 + ["Cloudy"] * 30 + ["Rainy"] * 10
        else: # Post-Monsoon
            weights = ["Cloudy"] * 40 + ["Sunny"] * 40 + ["Rainy"] * 20
        
        new_weather = random.choice(weights)
        if new_weather != self.state.weather and new_weather == "Drought":
             self.state.headline = "ALERT: Severe drought conditions reported!"
        elif new_weather == "Rainy" and self.state.season != Season.MONSOON:
             self.state.headline = "Unexpected rains surprise citizens."
             
        self.state.weather = new_weather

    def update_prices(self):
        headlines = []
        
        # 1. Update IDLI Price first (Cost-Push Logic)
        # Cost = 1.5 * RICE + 0.5 * Coffee + 10 (Overhead)
        # Using Rice price (defaulting to Ragi price proxy if Rice not tracked, but we added Rice to Models)
        # Actually in models.py RICE is now tracked.
        
        cost_basis = (self.state.prices[Resource.RICE] * 1.5) + (self.state.prices[Resource.COFFEE] * 0.1) + 10
        target_idli_price = cost_basis * 1.2 # 20% Margin
        
        # Smooth transition to target price
        current_idli = self.state.prices[Resource.IDLI_SET]
        self.state.prices[Resource.IDLI_SET] = current_idli + (target_idli_price - current_idli) * 0.2
        
        for res in Resource:
            if res == Resource.INR or res == Resource.IDLI_SET:
                continue
            
            volatility = 0.02
            change = random.uniform(1 - volatility, 1 + volatility)
            
            # --- Seasonal & Weather Effects ---
            
            # 1. Flowers: Festival Spike in Post-Monsoon (Dasara/Deepavali)
            if res == Resource.FLOWERS:
                seasonal_boost = 0
                if self.state.season == Season.POST_MONSOON:
                    seasonal_boost = random.uniform(0.05, 0.15)
                
                # DEMAND LOGIC: If Techies are broke (Idli is expensive), Demand drops
                # We simulate this by checking if Idli price > 60
                if self.state.prices[Resource.IDLI_SET] > 60:
                    demand_drag = -0.05 
                    change += demand_drag
                    if random.random() < 0.1: headlines.append("Flower market slump: 'People spending on food, not flowers'")
                else:
                    change += seasonal_boost

            # 2. Coffee: Drought kills supply -> Price up
            if res == Resource.COFFEE:
                if self.state.weather == "Drought":
                    change += 0.03
                    if random.random() < 0.2: headlines.append("Planters worry as drought hits coffee estates.")
                elif self.state.season == Season.WINTER:
                    change -= 0.01

            # 3. Rice & Ragi: Staple food
            if (res == Resource.RAGI or res == Resource.RICE) and self.state.weather == "Drought":
                change += 0.05 # Stronger effect to force Idli price up
                if random.random() < 0.2: headlines.append(f"{res.value} prices soar due to lack of rain.")

            # 4. Code: Tech boom/bust cycles
            if res == Resource.CODE:
                if random.random() < 0.05: 
                    shift = random.choice([-0.1, 0.1])
                    change += shift
                    if shift > 0: headlines.append("Tech Boom! Global startups hiring in Bengaluru.")
                    else: headlines.append("Recession fears: Tech stocks take a hit.")

            self.state.prices[res] *= change
            
            # Soft caps
            if self.state.prices[res] < 5: self.state.prices[res] = 5
            
            self.state.history[res].append(self.state.prices[res])
            
        # Add history for Idli too
        self.state.history[Resource.IDLI_SET].append(self.state.prices[Resource.IDLI_SET])
            
        if headlines:
            self.state.headline = headlines[0] # Show the most impactful news

    def step(self):
        self.state.date += timedelta(days=1)
        self.update_season_and_weather()
        self.update_prices()
        
        daily_logs = []
        for agent in self.agents:
            log = agent.act(self.state)
            daily_logs.append(log)
        
        self.logs = daily_logs + self.logs 
        self.logs = self.logs[:50]