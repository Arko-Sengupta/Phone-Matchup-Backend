import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from Tools.Scraper.Scraper import Scraper
from Tools.Processor.Processor import Processor
from Tools.Standardizer.Standardizer import Standardizer

logging.basicConfig(level=logging.INFO)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class ETLPipeline:

    def __init__(self) -> None:
        self.scraper = Scraper()
        self.standardizer = Standardizer()
        self.processor = Processor()

    def ExtractData(self, query: str, budget: int) -> list:
        try:
            return self.scraper.Run(query, budget)
        except Exception as e:
            logging.error('An Error Occurred while Extracting Data: ', exc_info=e)
            raise e

    def TransformData(self, raw_data: list, brand: str) -> pd.DataFrame:
        try:
            return self.standardizer.Run(raw_data, brand)
        except Exception as e:
            logging.error('An Error Occurred while Transforming Data: ', exc_info=e)
            raise e

    def FilterData(self, transformed_data: pd.DataFrame, price: str) -> pd.DataFrame:
        try:
            return self.processor.Run(transformed_data, price)
        except Exception as e:
            logging.error('An Error Occurred while Filtering Data: ', exc_info=e)
            raise e

    def Run(self, brand: str, price: str) -> pd.DataFrame:
        try:
            raw_data = self.ExtractData(brand, int(price))
            transformed_data = self.TransformData(raw_data, brand)
            filtered_data = self.FilterData(transformed_data, price)
            return filtered_data
        except Exception as e:
            logging.error('An Error Occurred during the ETL Pipeline Execution: ', exc_info=e)
            raise e

class ETLPipeRequest(BaseModel):
    brand: str
    price: str

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

etl_pipeline = ETLPipeline()

@app.get("/")
def ServerStarted():
    return {"response": 200, "SERVER STARTED": True}

@app.post("/ETLPipe")
def ETLPipe(body: ETLPipeRequest):
    try:
        response = etl_pipeline.Run(body.brand, body.price)
        return {"response": json.loads(response.to_json())}
    except Exception as e:
        logging.error('An Error Occurred during the ETL Process: ', exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':

    uvicorn.run(app, host="0.0.0.0", port=8000)
