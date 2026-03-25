# Hospital Claim AI

AI-powered claim validation for Thai hospitals. Reduces deny rates across all departments and funds.

## Features

- **9 Departments**: Cath Lab, OR, Chemo, Dialysis, ICU/NICU, ER/UCEP, ODS/MIS, OPD/NCD, Rehab
- **3 Funds**: NHSO (UC), Social Security (SSS), CSMBS
- **8 Validation Checkpoints** per case
- **CC/MCC Optimizer** to maximize DRG weight
- **Auto-appeal Generator** for denied cases
- **Batch Processing** via CSV upload
- **LINE Notification** for issues requiring human review
- **FDH API Integration** for auto-submission

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  HIS/HOSxP  │────▶│  Orchestrator │────▶│  FDH API  │
│  (Hospital) │     │  (FastAPI)    │     │  (NHSO)   │
└─────────────┘     └──────┬───────┘     └───────────┘
                           │
                    ┌──────┴───────┐
                    │  Claude API  │
                    │  (AI Engine) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ LINE OA  │ │ Database │ │Dashboard │
        │ (Alerts) │ │(Postgres)│ │ (React)  │
        └──────────┘ └──────────┘ └──────────┘
```

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn api.main:app --reload

# Test
pytest tests/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/check` | Check single claim |
| POST | `/api/v1/check/batch` | Check multiple claims (CSV) |
| POST | `/api/v1/appeal` | Generate appeal letter |
| GET | `/api/v1/status/{an}` | Check FDH submission status |
| GET | `/api/v1/dashboard/stats` | Get KPI dashboard data |
| POST | `/api/v1/submit` | Submit to FDH |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key |
| `DATABASE_URL` | PostgreSQL connection string |
| `LINE_CHANNEL_TOKEN` | LINE Messaging API token |
| `LINE_CHANNEL_SECRET` | LINE channel secret |
| `FDH_API_URL` | FDH API endpoint |
| `FDH_API_KEY` | FDH authentication key |

## License

Proprietary — Phyathai Sriracha Hospital / MedGuard AI
