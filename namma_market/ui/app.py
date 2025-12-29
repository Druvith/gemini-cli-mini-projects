from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.widgets import Header, Footer, Static, Log, Label
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
        return Align.center(Text("✨ NAMMA MARKET ✨", style="bold gold1"), vertical="middle")

class PriceChart(Static):
    """A widget to display the price chart using plotext."""
    
    def __init__(self, resource: Resource, color: str, get_data_func, **kwargs):
        super().__init__(**kwargs)
        self.resource = resource
        self.color = color
        self.get_data_func = get_data_func

    def on_mount(self):
        self.set_interval(1, self.update_chart)

    def on_resize(self, event):
        self.update_chart()

    def update_chart(self):
        data = self.get_data_func(self.resource)
        if not data:
            return
            
        plt.clf()
        
        width, height = self.content_size
        if width == 0 or height == 0:
            return
            
        plt.plotsize(width, height)
        
        # Aesthetic tweaks
        plt.theme("pro") # Clean dark theme
        plt.plot(data, color=self.color, marker=None)
        
        # Clean up axes
        plt.frame(True)
        plt.grid(True, False)
        plt.grid(True, True)
        
        # Remove title inside chart, relying on the border title
        plt.title(f"{self.resource.value}") 

        self.update(Text.from_ansi(plt.build()))

class NewsTicker(Static):
    """Displays the latest market news."""
    
    news = reactive("Market opens...")
    
    def render(self) -> str:
        # Simplified render to avoid potential Rich Panel nesting issues if any
        return Panel(
            Text(f"{self.news}", style="bold white"),
            title="Latest News",
            border_style="red",
            style="on red"
        )

class MarketStats(Static):
    """Displays current market stats."""
    
    current_weather = reactive("Sunny")
    current_date = reactive("Jan 01")
    current_season = reactive("Summer")
    
    def compose(self) -> ComposeResult:
        yield Label("STATS", id="stats-header")
        yield Label(f"Date: {self.current_date}", id="date-label")
        yield Label(f"Season: {self.current_season}", id="season-label")
        yield Label(f"Weather: {self.current_weather}", id="weather-label")
        yield Label(" ", id="spacer")
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
        
        self.query_one("#date-label", Label).update(f"🗓️  {self.current_date}")
        self.query_one("#season-label", Label).update(f"🍂 {self.current_season}")
        self.query_one("#weather-label", Label).update(f"🌡️  {self.current_weather}")
        
        icon_map = {
            Resource.COFFEE: "☕",
            Resource.FLOWERS: "🌸",
            Resource.RAGI: "🌾",
            Resource.RICE: "🍚",
            Resource.IDLI_SET: "🍛",
            Resource.CODE: "💻",
            Resource.INR: "₹"
        }
        
        for res, price in state.prices.items():
            if res in self.price_labels:
                icon = icon_map.get(res, "💰")
                self.price_labels[res].update(f"{icon} {res.value:<8} ₹{price:.2f}")

class NammaMarketApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-columns: 2fr 2fr 1fr;
        grid-rows: 3 4fr 2fr;
        background: #1e1e1e;
    }

    TitleBanner {
        column-span: 3;
        height: 3;
        content-align: center middle;
        background: #1e1e1e;
        color: gold;
    }

    #chart-grid {
        column-span: 2;
        row-span: 1;
        layout: grid;
        grid-size: 2 2;
        border: round #6272a4; /* Dracula purple/blueish */
        background: #282a36;
    }

    #stats-container {
        row-span: 1;
        column-span: 1;
        border: round #bd93f9;
        background: #282a36;
        padding: 1;
    }
    
    #news-container {
        row-span: 1;
        column-span: 1;
        height: auto;
        padding: 0 1;
    }

    #log-container {
        column-span: 3;
        row-span: 1;
        border: round #f1fa8c; /* Yellow */
        background: #282a36;
        height: 100%;
        color: #f8f8f2;
    }
    
    PriceChart {
        height: 100%;
        width: 100%;
        padding: 1;
    }

    Label {
        color: #f8f8f2;
    }
    
    #stats-header {
        text-style: bold;
        color: #50fa7b;
        margin-bottom: 1;
    }
    
    .price-label {
        color: #8be9fd;
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
            yield PriceChart(Resource.COFFEE, "sandybrown", lambda r: self.engine.state.history.get(r, []))
            yield PriceChart(Resource.FLOWERS, "magenta", lambda r: self.engine.state.history.get(r, []))
            yield PriceChart(Resource.IDLI_SET, "white", lambda r: self.engine.state.history.get(r, []))
            yield PriceChart(Resource.CODE, "springgreen", lambda r: self.engine.state.history.get(r, []))
            
        with Container(id="stats-container"):
            yield MarketStats(id="market-stats")
            yield NewsTicker(id="news-ticker")
            
        with Container(id="log-container"):
            yield Log(id="activity-log")
            
        yield Footer()

    def on_mount(self):
        self.query_one("#chart-grid").border_title = "Market Trends"
        self.set_interval(0.5, self.run_simulation_step)

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