import re
import logging
import pandas as pd
from typing import Optional
from pydantic import BaseModel, model_validator

logging.basicConfig(level=logging.INFO)

class PhoneProduct(BaseModel):
    url: str
    title: str
    platform: str
    content: str = ""

    model: Optional[str] = None
    color: Optional[str] = None
    rating: Optional[float] = None
    original_price: Optional[str] = None
    discount: Optional[str] = None
    price: Optional[int] = None
    amount: Optional[int] = None
    ram_rom: Optional[str] = None
    ram: Optional[int] = None
    rom: Optional[int] = None
    display: Optional[str] = None
    dimension: Optional[float] = None
    camera: Optional[str] = None
    battery: Optional[str] = None
    battery_power: Optional[int] = None

    @model_validator(mode='after')
    def ExtractFromContent(self):
        text = f"{self.title} {self.content}"

        if '(' in self.title:
            self.model = self.title[:self.title.index('(')].strip()
        else:
            self.model = self.title.split(',')[0].strip()

        color_match = re.search(r'\(([^,)]+)', self.title)
        if color_match:
            self.color = color_match.group(1).strip()

        rating_match = re.search(r'\b([4-5]\.\d)\b', text)
        if rating_match:
            self.rating = float(rating_match.group(1))

        emi_patterns = [
            r'(?:no[\s\-]*cost\s+)?emi\s+(?:of\s+|from\s+|starts?\s+(?:at\s+)?)?₹?\s*[\d,]+',
            r'₹\s*[\d,]+\s*/\s*(?:mo\.?|month)',
            r'₹\s*[\d,]+\s*per\s+month',
            r'₹\s*[\d,]+\s*x\s*\d+\s*(?:months?|mos?\.?)',
            r'(?:monthly|weekly)\s+(?:emi|installment)[^\n]{0,40}₹\s*[\d,]+',
            r'₹\s*[\d,]+[^\n]{0,20}(?:\/mo|per\s+mo|monthly\s+emi)',
        ]
        clean_text = re.sub(
            '|'.join(f'(?:{p})' for p in emi_patterns),
            '', text, flags=re.IGNORECASE
        )

        price_matches = re.findall(r'₹\s*([\d,]+)', clean_text)
        if not price_matches:
            price_matches = re.findall(r'(?:Rs\.?|INR)\s*([\d,]+)', clean_text, re.IGNORECASE)
        if not price_matches:
            price_matches = re.findall(
                r'(?:price|cost|offer\s*price|mrp|selling\s*price|buy\s*at|now\s*at)'
                r'[:\s₹]*(\d{1,3}(?:,\d{3})+)',
                clean_text, re.IGNORECASE
            )
        if price_matches:
            prices = sorted([int(p.replace(',', '')) for p in price_matches if p.replace(',', '').isdigit()])
            prices = [p for p in prices if 5000 <= p <= 300000]
            if prices:
                if len(prices) == 1:
                    self.price = prices[0]
                else:
                    median = prices[len(prices) // 2]
                    cluster = [p for p in prices if abs(p - median) / median <= 0.4]
                    self.price = min(cluster) if cluster else median
                self.amount = self.price
                self.original_price = f"₹{self.price:,}"

        discount_match = re.search(r'\b([1-9]\d?)\s*%\s*off\b', text, re.IGNORECASE)
        if discount_match:
            val = int(discount_match.group(1))
            if 1 <= val <= 90:
                self.discount = str(val)

        ram_rom_match = re.search(
            r'(\d+)\s*GB\s*(?:RAM)?\s*[|/+]\s*(\d+)\s*GB', text, re.IGNORECASE
        )
        if ram_rom_match:
            self.ram = int(ram_rom_match.group(1))
            self.rom = int(ram_rom_match.group(2))
        else:
            ram_match = re.search(
                r'(?:RAM[:\s]+(\d+)\s*GB|(\d+)\s*GB\s*RAM)', text, re.IGNORECASE
            )
            rom_match = re.search(r'(\d+)\s*GB\s*(?:ROM|storage|internal)', text, re.IGNORECASE)
            if ram_match:
                self.ram = int(ram_match.group(1) or ram_match.group(2))
            if rom_match:
                self.rom = int(rom_match.group(1))
        if self.ram and self.rom:
            self.ram_rom = f"{self.ram}GB | {self.rom}GB"

        display_match = re.search(r'(\d+\.?\d*)\s*(?:inch|")', text, re.IGNORECASE)
        if display_match:
            dim = float(display_match.group(1))
            if 4.0 <= dim <= 8.0:
                self.dimension = dim
                self.display = f"{self.dimension} inch"

        battery_match = re.search(r'(\d{3,5})\s*mAh', text, re.IGNORECASE)
        if battery_match:
            self.battery_power = int(battery_match.group(1))
            self.battery = f"{self.battery_power} mAh"

        camera_match = re.search(r'(\d+\s*MP(?:\s*\+\s*\d+\s*MP)*)', text, re.IGNORECASE)
        if camera_match:
            self.camera = camera_match.group(1)

        return self

NON_PRODUCT_URL_PATTERNS = re.compile(
    r'(/blog|/blog-listing|/category|/collection/|search\?q=|[?&]sort=|/c/[a-z]|'
    r'all[-_]smartphones|best[-_]smartphones|[-_]phones[-_]under[-_]|'
    r'[-_]mobiles[-_]under|[-_]mobile[-_]under|upcoming[-_]mobile)',
    re.IGNORECASE
)

NON_PRODUCT_TITLE_PATTERNS = re.compile(
    r'(^best\s+mobile|^top\s+\d+|^upcoming\s+mobile|^shop\s+\w+\s+mobile\s+phone|'
    r'mobile\s+phones?\s+online|phones?\s+online\s+at\s+best|mobiles\s+online|'
    r'buy\s+\w+\s+mobiles\s+online)',
    re.IGNORECASE
)

BRAND_MATCH_ALIASES = {
    'xiaomi':   ['xiaomi', 'redmi', 'poco'],
    'apple':    ['apple', 'iphone'],
    'motorola': ['motorola', 'moto'],
}

class Standardizer:
    def IsProductPage(self, title: str, url: str) -> bool:
        if NON_PRODUCT_URL_PATTERNS.search(url):
            return False
        if NON_PRODUCT_TITLE_PATTERNS.search(title):
            return False
        return True

    def MatchesBrand(self, title: str, brand: str) -> bool:
        core = brand.lower().replace(' smartphones', '').replace(' smartphone', '').strip()
        aliases = BRAND_MATCH_ALIASES.get(core, [core])
        return any(a in title.lower() for a in aliases)

    def Run(self, raw_results: list, brand: str = '') -> pd.DataFrame:
        products = []
        for item in raw_results:
            try:
                title = item.get('title', '')
                url = item.get('url', '')
                content = item.get('content', '')
                if not self.IsProductPage(title, url):
                    continue
                if brand and not self.MatchesBrand(title, brand):
                    continue
                phone = PhoneProduct(**item)
                if phone.price and phone.ram:
                    products.append(phone.model_dump())
            except Exception as e:
                logging.warning(f"Skipping item: {e}")

        if not products:
            logging.warning("No valid products extracted from search results.")
            return pd.DataFrame()

        df = pd.DataFrame(products)
        df = df.dropna(subset=['price', 'ram'])
        logging.info(f"Standardization complete: {len(df)} valid products.")
        return df
