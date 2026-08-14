"""Price a single property with the shipped model bundle (Week 9).

The Streamlit app and any batch job both go through `Predictor` so a prediction is built exactly the
way the training rows were: engineer the Week 6 features, then apply the bundle's train-only encoders.

    from pipeline.predict import Predictor
    p = Predictor.load()
    p.predict(living_area=1800, beds=3, baths=2, lot_size=6000,
              year_built=1985, district="Palo Alto Unified")
"""
import json
from dataclasses import dataclass
from datetime import date

import joblib
import numpy as np
import pandas as pd

from . import config as C
from .features import add_engineered_features, apply_encoders


@dataclass
class Predictor:
    bundle: dict
    defaults: dict
    interval: dict

    # ---------------------------------------------------------------- loading
    @classmethod
    def load(cls, bundle_path=C.MODEL_BUNDLE, defaults_path=C.APP_DEFAULTS,
             interval_path=C.QUOTE_INTERVAL):
        bundle = joblib.load(bundle_path)
        defaults = json.loads(open(defaults_path).read()) if _exists(defaults_path) else {}
        interval = json.loads(open(interval_path).read()) if _exists(interval_path) else {}
        return cls(bundle=bundle, defaults=defaults, interval=interval)

    # ---------------------------------------------------------------- metadata
    @property
    def districts(self):
        return sorted(self.defaults.get("districts", {}))

    @property
    def model_name(self):
        return self.bundle["model_name"]

    def district_info(self, district):
        return self.defaults.get("districts", {}).get(district, {})

    # ---------------------------------------------------------------- prediction
    def build_row(self, living_area, beds, baths, lot_size, year_built, district,
                  city=None, county=None, postal=None, stories=None, garage_spaces=None,
                  latitude=None, longitude=None, as_of=None):
        """Assemble the one-row raw frame a prediction needs, filling gaps from district defaults."""
        info = self.district_info(district)
        med = self.defaults.get("medians", {})
        as_of = as_of or date.today()

        row = {
            "LivingArea": living_area,
            "BedroomsTotal": beds,
            "BathroomsTotalInteger": baths,
            "LotSizeSquareFeet": lot_size,
            "YearBuilt": year_built,
            "GarageSpaces": garage_spaces if garage_spaces is not None else med.get("GarageSpaces"),
            "Stories": stories if stories is not None else med.get("Stories"),
            "FireplacesTotal": np.nan,                       # 100% null in the source extract
            "Latitude": latitude if latitude is not None else info.get("lat"),
            "Longitude": longitude if longitude is not None else info.get("lon"),
            "CountyOrParish": county or info.get("county", "Unknown"),
            "City": city or info.get("city", "Unknown"),
            "PostalCode": str(postal or info.get("postal", "Unknown")),
            "SchoolDistrict": district,
            "HighSchoolDistrict": info.get("high_district", district),
            "district_enroll": info.get("enroll"),
            "district_sed_pct": info.get("sed_pct"),
            "district_el_pct": info.get("el_pct"),
            "is_unified": info.get("is_unified", 1),
            # missing-flags: 1 when the caller left the field to a default
            "GarageSpaces_missing": int(garage_spaces is None),
            "Stories_missing": int(stories is None),
            "FireplacesTotal_missing": 1,
        }
        frame = pd.DataFrame([row])
        return add_engineered_features(frame, as_of_year=as_of.year, as_of_month=as_of.month)

    def predict(self, **kwargs):
        """Return the point estimate plus the empirical quote ranges from Week 8."""
        raw = self.build_row(**kwargs)
        X = apply_encoders(raw, self.bundle["encoders"], self.bundle["feature_cols"],
                           self.bundle["numeric_cols"], self.bundle["categorical_cols"])

        yhat = float(self.bundle["model"].predict(X)[0])
        if self.bundle.get("log_target"):
            yhat = float(np.exp(yhat))

        iv = self.interval
        out = {
            "price": yhat,
            "price_per_sqft": yhat / kwargs["living_area"] if kwargs.get("living_area") else np.nan,
            "model": self.model_name,
            "features": X.iloc[0].to_dict(),
        }
        for tag in ("50", "80"):
            lo, hi = iv.get(f"lo{tag}"), iv.get(f"hi{tag}")
            if lo and hi:
                out[f"lo{tag}"], out[f"hi{tag}"] = yhat * lo, yhat * hi
        return out


def _exists(path):
    try:
        return path.exists()
    except AttributeError:
        import os
        return os.path.exists(path)


if __name__ == "__main__":       # quick smoke test: python -m pipeline.predict
    p = Predictor.load()
    demo = p.predict(living_area=1800, beds=3, baths=2, lot_size=6000, year_built=1985,
                     district=p.districts[0] if p.districts else "Unknown")
    print(f"{p.model_name}: ${demo['price']:,.0f}  "
          f"(80% range ${demo.get('lo80', float('nan')):,.0f} .. ${demo.get('hi80', float('nan')):,.0f})")
