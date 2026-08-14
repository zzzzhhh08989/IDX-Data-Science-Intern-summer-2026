"""Shared configuration: paths, column lists, and the cleaning rules.

Single source of truth for everything the notebooks agreed on in Weeks 3-8, so the scripts and the
Streamlit app can never drift from the models that were trained in the notebooks.
"""
from pathlib import Path

# --- paths -------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent

RAW_SOLD_DIR = ROOT / "data" / "sold"
RAW_SOLD_GLOB = "CRMLSSold*.csv"

PROCESSED_DIR = ROOT / "data" / "processed"
CLEAN_CSV = PROCESSED_DIR / "sold_clean.csv"          # Week 3 output
FEATURES_CSV = PROCESSED_DIR / "sold_features.csv"    # Week 6 output

EXTERNAL_DIR = ROOT / "data" / "external"
SCHOOL_DISTRICT_SHP = EXTERNAL_DIR / "ca_school_districts_2024_25" / "DistrictAreas2425.shp"
SCHOOL_DISTRICT_URL = (
    "https://gis.data.ca.gov/api/download/v1/items/"
    "b0e3b936426a47ce9d9a2e77e2bb86cc/shapefile?layers=0"
)

MODELS_DIR = ROOT / "models"
MODEL_BUNDLE = MODELS_DIR / "best_model.joblib"
QUOTE_INTERVAL = MODELS_DIR / "quote_interval.json"
APP_DEFAULTS = MODELS_DIR / "app_defaults.json"
EVAL_BY_BAND = MODELS_DIR / "eval_by_price_band.json"  # Week 8 table, shipped so the app can warn

# --- target & source filters --------------------------------------------------------------------
TARGET = "ClosePrice"
PROPERTY_TYPE = "Residential"            # per the task prompt
PROPERTY_SUBTYPE = "SingleFamilyResidence"

# --- column groups -----------------------------------------------------------------------------
# Raw physical/location columns kept from the MLS extract (Week 3).
BASE_NUMERIC = [
    "LivingArea", "BedroomsTotal", "BathroomsTotalInteger",
    "LotSizeSquareFeet", "YearBuilt", "GarageSpaces",
    "Stories", "FireplacesTotal", "Latitude", "Longitude",
]
BASE_CATEGORICAL = ["CountyOrParish", "City", "PostalCode"]

# Engineered in Week 6.
ENGINEERED_NUMERIC = [
    "bed_bath_ratio", "living_area_per_bed", "lot_to_living_ratio", "total_rooms",
    "property_age", "is_new_build", "has_garage", "has_fireplace",
    "close_month_sin", "close_month_cos",
]

# School-district layer, from the spatial join in Week 6.
SCHOOL_CATEGORICAL = ["SchoolDistrict", "HighSchoolDistrict"]
SCHOOL_NUMERIC = ["district_enroll", "district_sed_pct", "district_el_pct", "is_unified"]
SCHOOL_ENCODED = ["district_ppsf_enc", "district_price_enc"]   # target-encoded: TRAIN ONLY

# Dropped from Week 7 onwards: FireplacesTotal is 100% null in this extract, so the column,
# its missing-flag and the has_fireplace feature derived from it are all constant.
DEAD_COLS = ["FireplacesTotal", "FireplacesTotal_missing", "has_fireplace"]

MISSING_FLAG_SOURCES = ["GarageSpaces", "Stories", "FireplacesTotal"]
FLAG_THRESHOLD_PCT = 2.0        # add a *_missing flag when null rate exceeds this

CATEGORICAL = BASE_CATEGORICAL + SCHOOL_CATEGORICAL

# --- cleaning rules (Week 3) --------------------------------------------------------------------
OUTLIER_RULES = {
    "ClosePrice": (1e4, 5e7),
    "LivingArea": (200, 20_000),
    "BedroomsTotal": (0, 12),
    "BathroomsTotalInteger": (0, 12),
    "LotSizeSquareFeet": (None, 871_200),      # 20 acres
    "YearBuilt": (1850, 2026),
}

# --- modelling ---------------------------------------------------------------------------------
DEFAULT_TRAIN_WINDOW = 13       # X, months of history before the test month (Week 4 sweep)
MIN_DISTRICT_N = 20             # min training sales before a district gets its own price encoding
RANDOM_STATE = 42


def numeric_features(columns):
    """Model numeric features present in `columns`, minus the dead ones (Week 7 onwards)."""
    flags = [f"{c}_missing" for c in MISSING_FLAG_SOURCES]
    wanted = BASE_NUMERIC + flags + ENGINEERED_NUMERIC + SCHOOL_NUMERIC
    return [c for c in wanted if c in set(columns) and c not in DEAD_COLS]
