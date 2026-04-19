# Phone-Matchup - Backend

FastAPI Backend For Phone-Matchup. Runs An ETL Pipeline To Extract, Standardize, And Filter Smartphone Data Based On Brand And Budget.

## How It Works

Send A Request With Your Brand And Budget Preferences, And The Pipeline Scrapes Live Listings Across Major Indian Retail Platforms, Standardizes The Data, And Returns Filtered Results Matching Your Criteria.

## Setup

1. Install Dependencies:

```bash
pip install -r requirements.txt
```

2. Add Your Tavily API Key To `.env`:

```env
TAVILY_API_KEY="<YOUR_TAVILY_API_KEY>"
```

3. Run The Server:

```bash
uvicorn ETLPipe_API:app --reload --port 8000
```

Server Starts At `http://localhost:8000`.

## API

**`GET /`** — Health Check.

**`POST /ETLPipe`** — Run The ETL Pipeline For A Given Brand And Budget.

Request Body:

```json
{
  "brand": "Samsung",
  "price": "20000"
}
```

Response:

```json
{
  "response": {
    "Model": { "0": "Samsung Galaxy A35", ... },
    "Price": { "0": 19999, ... },
    ...
  }
}
```

## Dependencies

| Package       | Version  |
| ------------- | -------- |
| fastapi       | 0.115.12 |
| uvicorn       | 0.34.0   |
| python-dotenv | 1.0.1    |
| tavily-python | 0.7.12   |
| requests      | 2.32.5   |
| pandas        | 3.0.1    |
| pydantic      | 2.9.2    |

## Project Structure

```
Phone-Matchup-Backend/
├── ETLPipe_API.py         — Routes, ETL Pipeline Orchestration
├── Scraper/
│   └── Scraper.py         — Multi-Platform Web Scraping Via Tavily
├── Standardizer/
│   └── Standardizer.py    — Data Standardization Logic
├── Processor/
│   └── Processor.py       — Filtering And Processing Logic
├── .env                   — Environment Config
├── requirements.txt       — Dependencies
├── vercel.json            — Vercel Deployment Config
└── .gitignore
```

## Supported Platforms

Scrapes Smartphone Listings From:

- Flipkart
- Amazon India
- Croma
- Reliance Digital
- Vijay Sales
- Tata Cliq
- Poorvika
- Samsung Shop

## Deployment

Deployed On **Vercel**. Set `TAVILY_API_KEY` As An Environment Variable In Your Vercel Project Settings Before Deploying.

## Contribution

- Create A Branch Using The Format `Phone-Matchup_<YourUsername>` When Contributing.
- Add The Label `Contributor` To Your Contributions To Distinguish Them Within The Project.