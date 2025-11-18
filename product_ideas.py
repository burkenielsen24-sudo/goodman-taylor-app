from dataclasses import dataclass, asdict
from typing import List, Optional
import uuid
import random
import csv
import json
from pathlib import Path

@dataclass
class ProductIdea:
    id: str
    name: str
    category: str
    materials: List[str]
    features: List[str]
    price_estimate_usd: float
    target_markets: List[str]

# Basic building blocks for idea generation
_CATEGORIES = [
    "Wall Art", "Light Fixture", "Throw Pillow", "Rug", "Storage", "Kids Decor",
    "Tabletop", "Window Treatment", "Multifunction Furniture", "Interactive Toy"
]

_THEMES = [
    "Adventure", "Cozy Cottage", "Modern Minimal", "Retro Playroom", "Nature",
    "Space", "Underwater", "Forest Friends", "Scandi Calm", "Bright Pop"
]

_MATERIALS = [
    "organic cotton", "recycled wood", "bamboo", "ceramic", "soft polyester",
    "felt", "hand-blown glass", "metal", "biodegradable composite"
]

_FEATURES = [
    "machine-washable", "modular", "LED-lit", "mountable", "reversible",
    "stain-resistant", "sensor-activated", "stackable", "flat-pack", "personalizable"
]

_MARKET_ADJUSTMENTS = {
    "US": 1.0,
    "UK": 1.1,
    "EU": 1.05,
    "JP": 1.2,
    "GLOBAL": 1.0
}

def _pick(listobj, k=1):
    return random.sample(listobj, k) if k > 1 else [random.choice(listobj)]

def _compose_name(theme: str, category: str, feature: Optional[str]) -> str:
    parts = [theme, category]
    if feature:
        # keep name short and catchy
        parts.append(feature.split("-")[0])
    return " ".join(parts)

def _estimate_price(category: str, markets: List[str]) -> float:
    base = {
        "Wall Art": 45, "Light Fixture": 120, "Throw Pillow": 30, "Rug": 80,
        "Storage": 60, "Kids Decor": 35, "Tabletop": 25, "Window Treatment": 70,
        "Multifunction Furniture": 250, "Interactive Toy": 40
    }.get(category, 50)
    factor = max(_MARKET_ADJUSTMENTS.get(m.upper(), 1.0) for m in markets)
    variance = random.uniform(0.85, 1.35)
    return round(base * factor * variance, 2)

def generate_ideas(count: int = 10, markets: Optional[List[str]] = None, seed: Optional[int] = None) -> List[ProductIdea]:
    if seed is not None:
        random.seed(seed)
    markets = markets or ["US"]
    ideas: List[ProductIdea] = []
    for _ in range(count):
        category = random.choice(_CATEGORIES)
        theme = random.choice(_THEMES)
        mats = random.sample(_MATERIALS, k=random.randint(1, 2))
        features = random.sample(_FEATURES, k=random.randint(1, 2))
        name = _compose_name(theme, category, features[0] if features else None)
        price = _estimate_price(category, markets)
        idea = ProductIdea(
            id=uuid.uuid4().hex,
            name=name,
            category=category,
            materials=mats,
            features=features,
            price_estimate_usd=price,
            target_markets=markets
        )
        ideas.append(idea)
    return ideas

def save_ideas_json(ideas: List[ProductIdea], path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump([asdict(i) for i in ideas], f, indent=2)

def save_ideas_csv(ideas: List[ProductIdea], path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "name", "category", "materials", "features", "price_estimate_usd", "target_markets"]
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in ideas:
            writer.writerow({
                "id": i.id,
                "name": i.name,
                "category": i.category,
                "materials": ";".join(i.materials),
                "features": ";".join(i.features),
                "price_estimate_usd": i.price_estimate_usd,
                "target_markets": ";".join(i.target_markets)
            })

if __name__ == "__main__":
    # Example: generate a brief catalog for family-friendly markets
    sample = generate_ideas(count=12, markets=["US", "GLOBAL"], seed=42)
    for item in sample:
        print(f"- {item.name} ({item.category}) — ${item.price_estimate_usd} — materials: {', '.join(item.materials)}")
    save_ideas_json(sample, "design/product_ideas_sample.json")
    save_ideas_csv(sample, "design/product_ideas_sample.csv")