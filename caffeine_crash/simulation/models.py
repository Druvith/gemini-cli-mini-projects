from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Region(Enum):
    BENGALURU = "Bengaluru"
    MANDYA = "Mandya"
    COORG = "Coorg"
    MYSORE = "Mysore"

class Resource(Enum):
    RAGI = "Ragi"
    RICE = "Rice"
    COMMERCIAL_COFFEE = "Coffee Beans" # Raw beans
    ARTISAN_COFFEE = "Artisan Coffee"  # The Luxury Product
    CODE = "Code"
    IDLI_SET = "Idli Set"
    INR = "INR"

class Season(Enum):
    SUMMER = "Summer"         # Mar-May
    MONSOON = "Monsoon"       # Jun-Sep
    POST_MONSOON = "Post-Monsoon" # Oct-Dec (Dasara/Deepavali time)
    WINTER = "Winter"         # Jan-Feb

@dataclass
class MarketState:
    date: datetime = field(default_factory=lambda: datetime(2025, 1, 1))
    season: Season = Season.WINTER
    weather: str = "Sunny"
    headline: str = "Market opens: Rents are stable."
    market_mood: str = "Stable"
    avg_techie_cash: float = 40000.0 # Match initial agent cash
    rent: float = 2000.0 # High fixed cost!
    prices: Dict[Resource, float] = field(default_factory=lambda: {
        Resource.RAGI: 35.0,
        Resource.RICE: 50.0,
        Resource.COMMERCIAL_COFFEE: 250.0,
        Resource.ARTISAN_COFFEE: 300.0, # Expensive!
        Resource.CODE: 1000.0,
        Resource.IDLI_SET: 40.0,
    })
    history: Dict[Resource, List[float]] = field(default_factory=dict)
    rent_history: List[float] = field(default_factory=list)

    def __post_init__(self):
        self.rent_history.append(self.rent)
        for res in Resource:
            if res != Resource.INR:
                self.history[res] = [self.prices.get(res, 0.0)]
