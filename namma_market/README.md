# Namma Market: A Karnataka Economic Simulation 🇮🇳

An interactive, Terminal-based (TUI) economic simulation of the Karnataka ecosystem. It models the intricate dance between Agriculture, Technology, and Culture.

## 🌟 The "Rice-Idli-Flower" Cycle
This isn't just random numbers. The simulation models a real economic ripple effect:
1.  **Supply Shock:** A drought in Mandya spikes the price of **Rice** & **Coffee**.
2.  **Cost-Push Inflation:** Local **Darshinis** (restaurants) are forced to raise the price of **Idli Sets** to cover costs.
3.  **The Squeeze:** **Techies** in Bengaluru, who *must* eat breakfast, spend their disposable income on expensive food.
4.  **Recession:** With empty wallets, Techies stop buying luxury goods like **Flowers**, causing the Flower market to crash even during festival season.

## 🚀 How to Run
1.  **Install Dependencies:**
    ```bash
    uv venv .venv
    source .venv/bin/activate
    uv pip install -r namma_market/requirements.txt
    ```
2.  **Run the Simulation:**
    ```bash
    ./.venv/bin/python -m namma_market.main
    ```

## 🎮 Controls
*   `Space`: Pause/Resume the simulation.
*   `q`: Quit.

## 🛠️ Technology Stack
*   **Textual:** For the beautiful TUI dashboard.
*   **Plotext:** For rendering charts directly in the terminal.
*   **Rich:** For stylish text and layouts.
*   **Python:** The brain behind the economy.

## 🏗️ Project Structure
*   `simulation/`: Contains the Agents (`Techie`, `Farmer`, `DarshiniOwner`) and the Market Engine.
*   `ui/`: The Textual application code.
