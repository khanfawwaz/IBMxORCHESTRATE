# 🤖 Agentic AI Warehouse Forecasting System

## Overview
A production-ready **Agentic AI system** powered by **IBM watsonx Orchestrate ADK** that combines ML-powered inventory forecasting, social media trend analysis, supply chain optimization, risk analysis, and sustainability metrics.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         IBM watsonx Orchestrate ADK (Core Engine)           │
│  - Autonomous Agent Orchestration                           │
│  - Multi-Agent Coordination                                 │
│  - Knowledge Graph Integration                              │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Social Agent │   │Forecast Agent│   │ Supply Agent │
│  (Port 8001) │   │  (Port 8004) │   │  (Port 8005) │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                ┌───────────────────────┐
                │  Unified Orchestrator │
                │     (Port 9000)       │
                └───────────────────────┘
```

## 🚀 Key Features

### Agentic AI Capabilities
- **Autonomous Decision Making**: Agents make decisions based on ML predictions
- **Multi-Agent Collaboration**: Agents communicate and coordinate actions
- **Adaptive Learning**: System learns from historical decisions
- **Goal-Oriented Planning**: Agents plan multi-step actions to achieve objectives

### ML Models
- **Prophet**: Time series forecasting with seasonality
- **SHAP**: Explainable AI for decision transparency
- **Anomaly Detection**: Statistical outlier identification
- **Sentiment Analysis**: Social media trend scoring

### Data Sources
- **Synthetic Warehouse Data**: 500 products, 2.9M sales records
- **Real-time APIs**: Google Trends, Reddit, YouTube
- **Custom Upload**: Support for external company data

## 📁 Project Structure

```
WarehouseFUll/
├── adk/                          # IBM watsonx Orchestrate ADK
│   ├── agents/                   # Agent definitions
│   ├── skills/                   # Agent skills/capabilities
│   ├── workflows/                # Orchestration workflows
│   └── config/                   # ADK configuration
├── backend/
│   ├── agents/                   # 8 Specialized agents
│   │   ├── social_agent/         # Port 8001
│   │   ├── sales_agent/          # Port 8002
│   │   ├── signal_agent/         # Port 8003
│   │   ├── forecast_agent/       # Port 8004
│   │   ├── supply_agent/         # Port 8005
│   │   ├── risk_agent/           # Port 8006
│   │   ├── sustainability_agent/ # Port 8007
│   │   └── xai_agent/            # Port 8008
│   ├── orchestrator/             # Unified orchestrator (Port 9000)
│   ├── ml_models/                # Trained ML models
│   └── shared/                   # Shared utilities
├── frontend/                     # React dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── agents/               # Agent UI components
│   │   └── pages/
│   └── public/
├── data/
│   ├── warehouse/                # Synthetic warehouse data
│   ├── ml_training/              # Training datasets
│   ├── custom_uploads/           # User-uploaded data
│   └── databases/                # SQLite/PostgreSQL
├── ml/
│   ├── training/                 # Model training scripts
│   ├── models/                   # Saved models
│   └── evaluation/               # Model evaluation
├── docker/                       # Docker configurations
├── tests/                        # Comprehensive tests
└── docs/                         # Documentation
```

## 🛠️ Technology Stack

### Core Orchestration
- **IBM watsonx Orchestrate ADK** (Latest version)
- **Python 3.11+**

### Backend
- **FastAPI** - High-performance async API framework
- **Pydantic V2** - Data validation
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL/SQLite** - Databases

### ML/AI
- **Prophet** - Time series forecasting
- **SHAP** - Explainable AI
- **scikit-learn** - ML utilities
- **pandas/numpy** - Data processing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Recharts** - Data visualization

### APIs
- **SerpAPI** - Google Trends (optional)
- **Reddit API** - Social trends
- **YouTube API** - Video trends

## 🚦 Quick Start

### Prerequisites
```bash
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
```

### Installation

1. **Clone and setup**
```bash
cd d:\Projects\WarehouseFUll
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

2. **Generate synthetic data**
```bash
python ml/training/generate_warehouse_data.py
```

3. **Train ML models**
```bash
python ml/training/train_forecast_model.py
```

4. **Start backend services**
```bash
# Start all agents
python backend/start_all_agents.py

# Or start unified orchestrator only
uvicorn backend.orchestrator.app:app --reload --port 9000
```

5. **Start frontend**
```bash
cd frontend
npm install
npm run dev
```

6. **Access the system**
- Frontend: http://localhost:5173
- Unified API: http://localhost:9000
- API Docs: http://localhost:9000/docs

## 🤖 Agent Capabilities

### 1. Social Trend Agent (Port 8001)
- Real-time social media monitoring
- Sentiment analysis
- Trend scoring and ranking

### 2. Sales Ingestion Agent (Port 8002)
- Historical data ingestion
- Data validation and cleaning
- Aggregation and metrics

### 3. Signal Filtering Agent (Port 8003)
- Statistical outlier detection
- Signal reliability scoring
- Noise reduction

### 4. Forecast Agent (Port 8004) ⭐ ML
- Prophet-based time series forecasting
- Seasonality detection
- Confidence intervals

### 5. Supply Chain Agent (Port 8005)
- Supplier availability checking
- Lead time calculation
- Stock level monitoring

### 6. Risk Analysis Agent (Port 8006)
- Multi-factor risk scoring
- Volatility assessment
- Recommendation generation

### 7. Sustainability Agent (Port 8007)
- Carbon footprint calculation
- Sustainability scoring
- Green recommendations

### 8. XAI Explainer Agent (Port 8008) ⭐ ML
- SHAP-based explanations
- Feature importance ranking
- Decision transparency

## 📊 API Usage

### Unified Analysis Endpoint

```bash
POST http://localhost:9000/api/v1/analyze
Content-Type: application/json

{
  "sku": "WH-FOOD-0001",
  "location": "New York",
  "forecast_days": 30,
  "quantity": 100,
  "knowledge_context": "Product trending on social media"
}
```

### Response
```json
{
  "sku": "WH-FOOD-0001",
  "location": "New York",
  "timestamp": "2025-11-23T19:37:27+05:30",
  "social_signals": [...],
  "forecast": {
    "total_predicted_demand": 3420,
    "trend": "increasing",
    "confidence": 0.85
  },
  "supply": {...},
  "risk": {...},
  "sustainability": {...},
  "explanation": {...},
  "recommendation": "✅ PROCEED: Order 2736 units",
  "action_items": [...],
  "overall_confidence": 0.79
}
```

## 🎯 Multi-Tenant Support

Upload custom warehouse data:

```bash
POST http://localhost:9000/api/v1/upload-dataset
Content-Type: multipart/form-data

{
  "company_name": "ACME Corp",
  "dataset_file": <CSV/Excel file>,
  "dataset_type": "sales_history"
}
```

The system will:
1. Create a dedicated agent instance
2. Train custom ML models
3. Provide isolated analysis

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific agent
pytest tests/test_forecast_agent.py -v

# Test orchestrator
pytest tests/test_orchestrator.py -v
```

## 🐳 Docker Deployment

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📈 Performance Metrics

- **Response Time**: < 3 seconds (unified analysis)
- **Forecast Accuracy**: 75-90% MAPE
- **Confidence Score**: 0.5-0.99
- **Concurrent Requests**: 100+ (with load balancing)

## 🔐 Security

- API key authentication
- Rate limiting
- Input validation
- SQL injection prevention
- CORS configuration

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ using IBM watsonx Orchestrate ADK**
