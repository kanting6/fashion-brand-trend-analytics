# Publishing the dataset (sample vs full)

This repo includes a **small sample dataset** committed to Git for easy portfolio review:
- `data/sample/*.csv`

For realistic scale, generate a **full dataset** locally (recommended) and publish it **without bloating Git history**.

---

## Option 1 — GitHub Release asset (cleanest)

1. Generate a large dataset locally:
   ```bash
   DAYS=210 N_USERS=80000 RAW_DIR=data/raw python -m fashion_trends generate-data
   ```

2. Zip the dataset:
   ```bash
   zip -r fashion-dataset-full.zip data/raw
   ```

3. Create a GitHub Release and upload `fashion-dataset-full.zip` as a Release asset.

4. In your README, link to the Release asset and explain how to download/unzip.

Pros:
- Keeps repo lightweight
- Great for portfolios / reviewers

---

## Option 2 — Git LFS (if you must keep data in-repo)

> Use Git LFS for CSVs if they exceed normal Git comfort.

1. Install Git LFS:
   ```bash
   git lfs install
   ```

2. Track CSVs (example):
   ```bash
   git lfs track "data/raw/*.csv"
   ```

3. Commit `.gitattributes` + data:
   ```bash
   git add .gitattributes data/raw
   git commit -m "Track full dataset with Git LFS"
   ```

Pros:
- Dataset lives “in repo”
Cons:
- LFS quotas / cloning friction

---

## Recommended pattern

- Commit: **`data/sample/`** (small, reviewable)
- Publish: **full dataset** as a **Release asset** (or store externally)
