import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)

class Processor:
    def __init__(self) -> None:
        pass

    def run(self, transformed_data: pd.DataFrame, price: str) -> pd.DataFrame:
        try:
            df = transformed_data.copy()
            if df.empty:
                return pd.DataFrame(columns=['url','title','model','color','rating','original_price','discount','price','RAM/ROM','display','camera','battery'])

            budget = int(price)
            logging.info(f'Filtering products under price: {budget}')

            df = df[df['amount'] <= budget]
            if df.empty:
                return pd.DataFrame(columns=['url','title','model','color','rating','original_price','discount','price','RAM/ROM','display','camera','battery'])

            df['score'] = (
                df['amount'].fillna(0).rank(pct=True) * 0.35 +
                df['ram'].fillna(0).rank(pct=True) * 0.25 +
                df['rom'].fillna(0).rank(pct=True) * 0.20 +
                df['battery_power'].fillna(0).rank(pct=True) * 0.12 +
                df['rating'].fillna(0).rank(pct=True) * 0.08
            )

            df = df.sort_values('score', ascending=False).drop_duplicates(subset=['url']).head(10)

            df = df.rename(columns={'ram_rom': 'RAM/ROM'})
            df = df[['url', 'title', 'model', 'color', 'rating',
                      'original_price', 'discount', 'price',
                      'RAM/ROM', 'display', 'camera', 'battery']]

            logging.info(f'Processing complete: {len(df)} results.')
            return df
        except Exception as e:
            logging.error('An Error Occurred while running the Processor: ', exc_info=e)
            raise e