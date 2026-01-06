from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Static, Log, Label
from textual.reactive import reactive
from textual.binding import Binding

import plotext as plt
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

from ..simulation.engine import MarketEngine
from ..simulation.models import Resource

class TitleBanner(Static):
    """A stylish title banner."""
    def render(self):
        return Align.center(Text("CAFFEINE CRASH: BENGALURU EDITION 📉", style="bold gold1"), vertical="middle")

class PriceChart(Static):
    """A widget to display a single price chart using plotext."""
    
    def __init__(self, label: str, color: str, get_data_func, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.color = color
        self.get_data_func = get_data_func
        self.interval_handle = None

    def on_mount(self):
        # Don't start interval immediately - wait for app to signal it's ready
        pass

    def start_updates(self):
        """Start the chart update interval."""
        if self.interval_handle is None:
            self.interval_handle = self.app.set_interval(0.5, self.update_chart)

    def on_resize(self, event):
        self.update_chart()

    def update_chart(self):
        # Prevent updates if app is paused (e.g. disclaimer is open)
        if getattr(self.app, "paused", False):
            return

        # 1. Clear State (Crucial for Plotext in loops)
        plt.clf()
        plt.clear_data()
        plt.clear_figure()
        
        # 2. Get Data
        data = self.get_data_func()
        if not data:
            return
            
        # 3. Size Check
        width, height = self.content_size
        if width <= 0 or height <= 0:
            return
            
        # 4. Plot
        plt.plotsize(width, height)
        plt.theme("pro") 
        plt.title(self.label)
        plt.plot(data, color=self.color, marker=None)
        plt.frame(True)
        plt.grid(True, True)

        # 5. Render
        self.update(Text.from_ansi(plt.build()))

class NewsTicker(Static):
    """Displays the latest market news."""
    
    news = reactive("Market opens...")
    
    def render(self) -> str:
        return Panel(
            Text(f"{self.news}", style="bold white", justify="center"),
            title="🗞️ BREAKING NEWS",
            border_style="red",
            padding=(1, 2)
        )

class MarketStats(Static):
    """Displays current market stats."""
    
    current_weather = reactive("Sunny")
    current_date = reactive("Jan 01")
    current_season = reactive("Summer")
    market_mood = reactive("Stable")
    
    def compose(self) -> ComposeResult:
        yield Label("ECONOMIC INDICATORS", id="stats-header")
        yield Label(f"Date: {self.current_date}", id="date-label")
        yield Label(f"Season: {self.current_season}", id="season-label")
        yield Label(f"Weather: {self.current_weather}", id="weather-label")
        yield Label(" ", id="spacer-1")
        yield Label(f"Mood: {self.market_mood}", id="mood-label") 
        yield Label(" ", id="spacer-2")
        yield Label("COMMODITY PRICES", id="prices-header")
        self.price_labels = {}
        for res in Resource:
            if res != Resource.INR:
                lbl = Label(f"{res.value}: ₹0.00", classes="price-label")
                self.price_labels[res] = lbl
                yield lbl

    def update_stats(self, state):
        self.current_date = state.date.strftime("%d %b %Y")
        self.current_season = state.season.value
        self.current_weather = state.weather
        self.market_mood = state.market_mood
        
        self.query_one("#date-label", Label).update(f"DATE:    {self.current_date}")
        self.query_one("#season-label", Label).update(f"SEASON:  {self.current_season}")
        self.query_one("#weather-label", Label).update(f"WEATHER: {self.current_weather}")
        
        mood_color = "green" if self.market_mood == "Optimistic" else "yellow" if self.market_mood == "Anxious" else "red"
        self.query_one("#mood-label", Label).update(f"MOOD:    [{mood_color}]{self.market_mood}[/]")
        
        # Color Map for Resource Names
        res_colors = {
            Resource.COMMERCIAL_COFFEE: "sandybrown",
            Resource.ARTISAN_COFFEE: "magenta",
            Resource.RAGI: "wheat",
            Resource.RICE: "white",
            Resource.IDLI_SET: "white",
            Resource.CODE: "springgreen"
        }

        for res, price in state.prices.items():
            if res in self.price_labels:
                name_color = res_colors.get(res, "white")
                self.price_labels[res].update(f"[{name_color}]{res.value:<15}[/] ₹{price:7.2f}")



class NammaMarketApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-columns: 2fr 2fr 1.2fr;
        grid-rows: 3 6fr 3fr;
        background: #1e1e1e;
    }

    TitleBanner {
        column-span: 3;
        height: 3;
        content-align: center middle;
        background: #1e1e1e;
        color: gold;
        text-style: bold;
    }

    #chart-grid {
        column-span: 2;
        row-span: 1;
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr;
        border: round #6272a4; 
        background: #282a36;
    }

    #stats-container {
        row-span: 1;
        column-span: 1;
        border: round #bd93f9;
        background: #282a36;
        padding: 1 2;
    }
    
    #log-container {
        column-span: 2;
        row-span: 1;
        border: round #f1fa8c;
        background: #282a36;
        color: #f8f8f2;
    }

    #news-container {
        row-span: 1;
        column-span: 1;
        height: 100%;
        padding: 0;
        border: round #ff5555;
        background: #282a36;
    }
    
    PriceChart {
        height: 100%;
        width: 100%;
        padding: 1;
        border: none;
    }

    Label {
        color: #f8f8f2;
    }
    
    #stats-header, #prices-header {
        text-style: bold;
        color: #50fa7b;
        margin-bottom: 1;
        border-bottom: solid #44475a;
    }
    
    #mood-label {
        text-style: bold;
        color: #8be9fd;
        margin-top: 1;
    }
    
    .price-label {
        color: #f8f8f2;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "toggle_pause", "Pause/Resume"),
    ]

    def __init__(self):
        super().__init__()
        self.engine = MarketEngine()
        self.paused = False

    def compose(self) -> ComposeResult:
        yield TitleBanner()
        
        with Container(id="chart-grid"):
            yield PriceChart("AVG RENT (₹)", "red", lambda: self.engine.state.rent_history)
            yield PriceChart("Artisan Coffee", "magenta", lambda: self.engine.state.history.get(Resource.ARTISAN_COFFEE, []))
            yield PriceChart("Idli Set", "white", lambda: self.engine.state.history.get(Resource.IDLI_SET, []))
            yield PriceChart("Code Value", "springgreen", lambda: self.engine.state.history.get(Resource.CODE, []))
            
        with Container(id="stats-container"):
            yield MarketStats(id="market-stats")
            
        with Container(id="log-container"):
            yield Log(id="activity-log")
            
        with Container(id="news-container"):
            yield NewsTicker(id="news-ticker")
            
        yield Footer()

    def on_mount(self):
        self.query_one("#chart-grid").border_title = "Market Trends"
        self.paused = False
        self.set_interval(0.5, self.run_simulation_step)
        # Start chart updates 
        for chart in self.query(PriceChart).results():
            chart.start_updates()

    def run_simulation_step(self):
        if self.paused:
            return
            
        self.engine.step()
        
        self.query_one(MarketStats).update_stats(self.engine.state)
        self.query_one(NewsTicker).news = self.engine.state.headline
        
        log_widget = self.query_one("#activity-log", Log)
        for entry in self.engine.logs[:5]: 
            log_widget.write_line(entry)

    def action_toggle_pause(self):
        self.paused = not self.paused
