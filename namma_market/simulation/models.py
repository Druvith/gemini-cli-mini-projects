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
    COFFEE = "Coffee"
    FLOWERS = "Flowers"
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
    headline: str = "Market opens for the new year!"
    prices: Dict[Resource, float] = field(default_factory=lambda: {
        Resource.RAGI: 35.0,
        Resource.RICE: 50.0,
        Resource.COFFEE: 250.0,
        Resource.FLOWERS: 80.0,
        Resource.CODE: 1000.0,
        Resource.IDLI_SET: 40.0,
    })
    history: Dict[Resource, List[float]] = field(default_factory=dict)

    def __post_init__(self):
        for res in Resource:
            if res != Resource.INR:
                self.history[res] = [self.prices.get(res, 0.0)]