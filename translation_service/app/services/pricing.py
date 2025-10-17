import math

from app.models.project import ProjectType

PRICING = {}

def initiate_prices():
    PRICING["english_subtitle"] = 4000
    PRICING["persian_subtitle"] = 4000
    PRICING["persian_dubbing"] = 5000
    PRICING["persian_dubbing_english_subtitle"] = 6000
    PRICING["persian_dubbing_persian_subtitle"] = 6000

initiate_prices()

def calculate_price(option_id, width, height, duration):
    minutes = max(1, math.ceil(duration / 60))  # Convert to minutes
    multiplier = 1.0
    if height * width > (3840 * 2160):  # 4K
        multiplier = 4.0
        video_type = '4K'
    elif height * width > (2560 * 1440):  # 2K
        multiplier = 3.0
        video_type = '2K'
    elif height * width > (1920 * 1080):  # Full HD
        multiplier = 2.0
        video_type = 'Full HD'
    elif height * width > (1280 * 720):  # HD
        multiplier = 1.5
        video_type = 'HD'
    else:
        video_type = 'SD'  # Standard Definition for lower resolutions

    price = math.ceil(minutes * PRICING[option_id] * multiplier)
    return price, multiplier, video_type

def calculate_prices(width, height, duration):
    prices = {
        op: {
            'price': calculate_price(op, width, height, duration)[0],
            'multiplier': calculate_price(op, width, height, duration)[1],
            'cost_per_minute': calculate_price(op, width, height, duration)[0] / max(1, math.ceil(duration / 60)),
            'video_type': calculate_price(op, width, height, duration)[2]
        }
        for op in PRICING
    }
    return prices

def get_pricing():
    return [
        {"id": "english_subtitle", "name": "زیرنویس انگلیسی", "price": PRICING["english_subtitle"]},
        {"id": "persian_dubbing", "name": "دوبله فارسی", "price": PRICING["persian_dubbing"]},
        {"id": "persian_dubbing_and_subtitle", "name": "دوبله و زیرنویس فارسی", "price": PRICING["persian_dubbing_and_subtitle"]}
    ]