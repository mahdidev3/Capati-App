from app.models.project import ProjectType

PRICING = {}

def initiate_prices():
    PRICING["english_subtitle"] = 0.5
    PRICING["persian_dubbing"] = 0.5
    PRICING["persian_dubbing_and_subtitle"] = 0.5

initiate_prices()

def calculate_price(option_id, video_size):
    price_per_mb = PRICING.get(option_id)
    if price_per_mb is None:
        raise ValueError(f"Invalid option_id: {option_id}")
    return video_size * price_per_mb

def get_pricing():
    return [
        {"id": "english_subtitle", "name": "زیرنویس انگلیسی", "price": PRICING["english_subtitle"]},
        {"id": "persian_dubbing", "name": "دوبله فارسی", "price": PRICING["persian_dubbing"]},
        {"id": "persian_dubbing_and_subtitle", "name": "دوبله و زیرنویس فارسی", "price": PRICING["persian_dubbing_and_subtitle"]}
    ]