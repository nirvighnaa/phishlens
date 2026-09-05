"""
One-time script to clean the raw PhiUSIIL dataset and produce a
train/test-ready CSV using our OWN feature extractor (not the dataset's
pre-computed features), so training stays consistent with what the
live API computes at request time.

Run from backend/ with the venv active:
    python app/ml/prepare_dataset.py
"""

import sys
from pathlib import Path

import pandas as pd

# Allow running this script directly (adds backend/ to the import path)
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.feature_extractor import extract_features
from app.utils.validators import validate_url, URLValidationError

RAW_PATH = Path(__file__).resolve().parents[3] / "data" / "raw" / "PhiUSIIL_Phishing_URL_Dataset.csv"
OUT_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "dataset_features.csv"


def main():
    print(f"Loading raw dataset from: {RAW_PATH}")
    df = pd.read_csv(RAW_PATH)

    print(f"Raw shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # PhiUSIIL uses 'URL' and 'label' columns (1 = legitimate, 0 = phishing
    # in the original dataset card — we'll confirm and normalize below).
    if "URL" not in df.columns or "label" not in df.columns:
        raise ValueError(
            "Expected columns 'URL' and 'label' not found. "
            f"Actual columns: {list(df.columns)}"
        )

    df = df[["URL", "label"]].copy()

    before = len(df)
    df = df.dropna(subset=["URL", "label"])
    df = df.drop_duplicates(subset=["URL"])
    print(f"Dropped {before - len(df)} rows (missing values or duplicate URLs)")

    # Normalize label: we standardize to 1 = PHISHING, 0 = LEGITIMATE
    # for the rest of our pipeline, regardless of the source dataset's convention.
    # PhiUSIIL's dataset card defines label=1 as legitimate, 0 as phishing —
    # so we flip it here to match our own convention.
    df["label"] = df["label"].apply(lambda x: 0 if x == 1 else 1)

    print("Label distribution after normalization (1=phishing, 0=legitimate):")
    print(df["label"].value_counts())

    features_list = []
    skipped = 0

    for i, row in df.iterrows():
        try:
            clean_url = validate_url(str(row["URL"]))
            feats = extract_features(clean_url)
            feats["label"] = row["label"]
            features_list.append(feats)
        except URLValidationError:
            skipped += 1
        except Exception:
            skipped += 1

        if i % 20000 == 0 and i > 0:
            print(f"Processed {i} rows...")

    print(f"Skipped {skipped} rows that failed validation/feature extraction")

    result_df = pd.DataFrame(features_list)
    print(f"Final processed shape: {result_df.shape}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(OUT_PATH, index=False)
    print(f"Saved to: {OUT_PATH}")


if __name__ == "__main__":
    main()