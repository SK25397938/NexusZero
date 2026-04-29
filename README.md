# NexusZero: Intelligent Route Orchestrator

NexusZero is a state-of-the-art logistics platform designed to optimize global supply chain routing using multi-agent artificial intelligence. It balances complex trade-offs between speed, cost, and environmental impact to provide Pareto-optimal solutions for modern trade lanes.

## Key Features

- **Multi-Agent AI Decision System**: A collaborative AI environment featuring specialized agents (Operations, Finance, and Sustainability) that negotiate to reach the most balanced routing decisions.
- **Dynamic Route Optimization**: Real-time pathfinding across global maritime, air, and land networks using advanced heuristics.
- **Live Disruption Simulator**: Ability to simulate and respond to real-world events such as Suez Canal blockages, fuel price spikes, or severe weather conditions.
- **Pareto Trade-off Analysis**: Interactive visualization of the Pareto front, allowing users to understand the mathematical compromise between cost and carbon emissions.
- **Executive Reporting**: Automated generation of professional logistics summaries for stakeholders.

## Technical Architecture

- **Backend**: Python with FastAPI for high-performance API services.
- **AI Engine**: Powered by Gemini 1.5 Flash for intelligent reasoning and multi-agent simulation.
- **Frontend**: Responsive web interface using Vanilla JS, Leaflet.js for interactive mapping, and Chart.js for data visualization.
- **Graph Engine**: Custom graph theory implementation for global route calculations.

## Getting Started

### Prerequisites

- Python 3.8+
- Google AI API Key (for Gemini agent features)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SK25397938/NexusZero.git
   cd NexusZero
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r ../requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the `backend` directory and add your API keys:
   ```env
   GEMINI_API_KEY="your_google_ai_key"
   ORS_API_KEY="your_open_route_service_key"
   ```

4. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

5. Open the frontend:
   Open `Frontend/1.html` in your web browser.

## Project Structure

- `backend/`: FastAPI application, AI agent logic, and graph data.
- `Frontend/`: Web interface and visualization components.
- `scratch/`: Utility scripts for dataset generation.

## License

This project is licensed under the MIT License.
