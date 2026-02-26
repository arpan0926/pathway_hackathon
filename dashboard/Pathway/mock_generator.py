"""Mock shipment data generator for Pathway-style endpoints.

Generates a list of shipments with latitude/longitude, ETA, status, and other
useful fields for the Streamlit dashboard demo.
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class MockPathwayShipmentGenerator:
    def __init__(self, seed: Optional[int] = None):
        self._rand = random.Random(seed)
        self.seed = seed

    def _random_coord(self, center: tuple[float, float], spread_km: float = 50.0):
        # crude conversion: ~1 deg lat ~= 111 km
        lat0, lon0 = center
        lat = lat0 + (self._rand.uniform(-1, 1) * (spread_km / 111))
        lon = lon0 + (self._rand.uniform(-1, 1) * (spread_km / (111 * abs(lat0) if lat0 != 0 else 1)))
        return round(lat, 6), round(lon, 6)

    def _eta_str(self, minutes: int) -> str:
        if minutes < 60:
            return f"{minutes}m"
        else:
            hrs = minutes // 60
            mins = minutes % 60
            return f"{hrs}h {mins}m"

    def generate_shipment(self, base_center: tuple[float, float] = (28.6139, 77.2090)) -> Dict:
        shipment_id = f"S{self._rand.randint(100, 999)}"
        lat, lon = self._random_coord(base_center)
        eta_min = self._rand.randint(5, 240)
        status = self._rand.choices(["On Time", "Delayed", "At Risk"], weights=[70, 20, 10])[0]
        created = datetime.utcnow() - timedelta(minutes=self._rand.randint(0, 120))
        return {
            "shipment_id": shipment_id,
            "lat": lat,
            "lon": lon,
            "ETA": self._eta_str(eta_min),
            "eta_minutes": eta_min,
            "status": status,
            "last_seen": created.isoformat() + "Z",
            "speed_kmph": round(self._rand.uniform(20, 90), 1),
            "destination": self._rand.choice(["Mumbai", "Delhi", "Bengaluru", "Kolkata", "Chennai"]),
        }

    def generate_batch(self, n: int = 5, base_center: tuple[float, float] = (28.6139, 77.2090)) -> List[Dict]:
        return [self.generate_shipment(base_center=base_center) for _ in range(n)]


def generate_shipments(seed: Optional[int] = None, n: int = 5, **kwargs) -> List[Dict]:
    g = MockPathwayShipmentGenerator(seed=seed)
    return g.generate_batch(n=n, **kwargs)
