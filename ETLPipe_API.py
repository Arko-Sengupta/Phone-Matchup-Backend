import os
import logging
import pandas as pd
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from Scraper.Scraper import Scraper
from Processor.Processor import Processor
from Standardizer.Standardizer import Standardizer

logging.basicConfig(level=logging.INFO)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class ETLPipeline:

    def __init__(self) -> None:
        self.scraper = Scraper()
        self.standardizer = Standardizer()
        self.processor = Processor()

    def extract_data(self, query: str, budget: int) -> list:
        try:
            return self.scraper.run(query, budget)
        except Exception as e:
            logging.error('An Error Occurred while Extracting Data: ', exc_info=e)
            raise e

    def transform_data(self, raw_data: list, brand: str) -> pd.DataFrame:
        try:
            return self.standardizer.run(raw_data, brand)
        except Exception as e:
            logging.error('An Error Occurred while Transforming Data: ', exc_info=e)
            raise e

    def filter_data(self, transformed_data: pd.DataFrame, price: str) -> pd.DataFrame:
        try:
            return self.processor.run(transformed_data, price)
        except Exception as e:
            logging.error('An Error Occurred while Filtering Data: ', exc_info=e)
            raise e

    def run(self, brand: str, price: str) -> pd.DataFrame:
        try:
            raw_data = self.extract_data(brand, int(price))
            transformed_data = self.transform_data(raw_data, brand)
            filtered_data = self.filter_data(transformed_data, price)
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
def server_started():
    return {"response": 200, "SERVER STARTED": True}

@app.post("/ETLPipe")
def etl_pipe(body: ETLPipeRequest):
    try:
        response = etl_pipeline.run(body.brand, body.price)
        return {"response": response.to_dict()}
    except Exception as e:
        logging.error('An Error Occurred during the ETL Process: ', exc_info=e)
        return {"Error": str(e)}

if __name__ == '__main__':

    uvicorn.run(app, host="0.0.0.0", port=8000)