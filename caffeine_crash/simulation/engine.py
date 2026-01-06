from typing import List
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
        
        # Coorg Planters - Now producing COMMERCIAL_COFFEE
        for i in range(3):
            agents.append(Farmer(f"Planter-{i}", Region.COORG, Resource.COMMERCIAL_COFFEE))
            
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
        
        # --- 1. RENT SHOCK LOGIC ---
        # 2% chance of a Rent Hike (Landlord Greed)
        if random.random() < 0.02:
            hike = random.choice([100, 200, 500])
            self.state.rent += hike
            headlines.append(f"RENT HIKE! Landlords demand ₹{self.state.rent:.0f}/day.")
        
        # --- 2. COST-PUSH INFLATION (Idli) ---
        # Cost = 1.5 * RICE + 0.5 * Commercial_Coffee + 10
        coffee_cost = self.state.prices[Resource.COMMERCIAL_COFFEE]
        cost_basis = (self.state.prices[Resource.RICE] * 1.5) + (coffee_cost * 0.1) + 10
        target_idli_price = cost_basis * 1.2
        current_idli = self.state.prices[Resource.IDLI_SET]
        self.state.prices[Resource.IDLI_SET] = current_idli + (target_idli_price - current_idli) * 0.2
        
        for res in Resource:
            if res == Resource.INR or res == Resource.IDLI_SET:
                continue
            
            volatility = 0.02
            change = random.uniform(1 - volatility, 1 + volatility)
            
            # --- Specific Resource Logic ---
            
            # ARTISAN COFFEE (The Luxury Index)
            if res == Resource.ARTISAN_COFFEE:
                # 1. Cost-Push Factor: Linked to raw bean prices
                raw_bean_price = self.state.prices[Resource.COMMERCIAL_COFFEE]
                # If raw beans are expensive (> 260), cafes raise prices
                if raw_bean_price > 260:
                    change += 0.01
                
                # 2. Demand Factor: Rent Squeeze
                # Instead of a crash, demand softens gently
                if self.state.rent > 3000:
                    change -= 0.015 # Recessionary drag
                    if random.random() < 0.1: headlines.append("Cafes reporting lower footfall.")
                elif self.state.rent > 2500:
                    change -= 0.005 # Mild slowing
                else:
                    change += 0.005 # Healthy growth
                
                # Ensure it doesn't decouple completely from reality
                if self.state.prices[res] > 500: change -= 0.02 # Ceiling correction
            
            # COMMERCIAL COFFEE (Raw Material)
            if res == Resource.COMMERCIAL_COFFEE:
                if self.state.weather == "Drought":
                    change += 0.04
                    if random.random() < 0.2: headlines.append("Coffee crop failure in Coorg!")

            # RICE/RAGI
            if (res == Resource.RAGI or res == Resource.RICE) and self.state.weather == "Drought":
                change += 0.05
                if random.random() < 0.2: headlines.append(f"{res.value} shortage due to drought.")

            # CODE
            if res == Resource.CODE:
                # Slight upward bias to simulate industry growth
                change += 0.001
                
                if random.random() < 0.05: 
                    # Reduced volatility: +/- 5% instead of 10%
                    shift = random.choice([-0.05, 0.05])
                    change += shift

            self.state.prices[res] *= change
            if self.state.prices[res] < 5: self.state.prices[res] = 5
            self.state.history[res].append(self.state.prices[res])
        
        # History for Idli
        self.state.history[Resource.IDLI_SET].append(self.state.prices[Resource.IDLI_SET])
        
        # History for Rent
        self.state.rent_history.append(self.state.rent)
            
        if headlines:
            self.state.headline = headlines[0]

    def step(self):
        self.state.date += timedelta(days=1)
        self.update_season_and_weather()
        self.update_prices()
        
        daily_logs = []
        total_techie_cash = 0
        techie_count = 0
        
        for agent in self.agents:
            log = agent.act(self.state)
            daily_logs.append(log)
            if isinstance(agent, Techie):
                total_techie_cash += agent.cash
                techie_count += 1
        
        # Update Aggregate Stats
        if techie_count > 0:
            self.state.avg_techie_cash = total_techie_cash / techie_count
            
        # Determine Mood based on savings vs rent
        savings_ratio = self.state.avg_techie_cash / self.state.rent
        if savings_ratio < 5:
            self.state.market_mood = "Panic"
        elif savings_ratio < 15:
            self.state.market_mood = "Anxious"
        else:
            self.state.market_mood = "Optimistic"
        
        self.logs = daily_logs + self.logs 
        self.logs = self.logs[:50]
