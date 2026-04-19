import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS

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

class ETLPipe_API:

    def __init__(self) -> None:
        self.app = Flask(__name__)
        CORS(self.app)
        self.etl_pipeline_blueprint = Blueprint('etl_pipeline', __name__)

        self.etl_pipeline_blueprint.add_url_rule('/', 'server_started', self.server_started, methods=['GET'])
        self.etl_pipeline_blueprint.add_url_rule('/ETLPipe', 'etl_pipe', self.etl_pipe, methods=['POST'])

        self.etl_pipeline = ETLPipeline()

    def server_started(self) -> jsonify:
        try:
            return jsonify({'response': 200, 'SERVER STARTED': True}), 200
        except Exception as e:
            logging.error('An Error Occurred while Starting the Server: ', exc_info=e)
            raise e

    def etl_pipe(self) -> jsonify:
        try:
            data = request.get_json()
            brand, price = data['brand'], data['price']
            response = self.etl_pipeline.run(brand, price)
            return jsonify({'response': json.loads(response.to_json())}), 200
        except Exception as e:
            logging.error('An Error Occurred during the ETL Process: ', exc_info=e)
            return jsonify({'Error': str(e)}), 400

server = ETLPipe_API()
server.app.register_blueprint(server.etl_pipeline_blueprint)

app = server.app

if __name__ == '__main__':
    
    app.run(debug=True)