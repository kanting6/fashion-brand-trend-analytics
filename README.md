# Brand-Level Fashion Trend Analysis (Merchandising & Content Strategy)

This repo is an **industry-style analytics project** built to showcase:
- **Python + SQL pipelines** to aggregate weekly **traffic → add-to-cart → conversion** for **40+ brands**, segmented by **category, gender, region**
- **Brand-specific trend indices** (momentum + acceleration) to identify **emerging styles** (silhouettes, colors, categories) **4–6 weeks earlier** than a naive baseline, plus **early fatigue** flags
- **Tableau-ready extracts** and a dashboard spec for merchandising decisions (**sell-through**, **discount dependency**, **return rate**)

**Data is synthetic** (generated locally) and safe to publish publicly.

---

## Included datasets (GitHub-friendly)

### ✅ Committed sample dataset (small)
This repo includes a small sample dataset at:

- `data/sample/`  
  - `products.csv`
  - `inventory_receipts.csv`
  - `web_events.csv`
  - `orders.csv`
  - `order_items.csv`

Use it to run the pipeline without generating new data.

### 🧱 Full dataset (recommended for “realistic scale”)
For a larger dataset, generate it locally and store it **outside Git history**:
- Use **Git LFS** (if you must keep data in the repo)
- Or upload it as a **GitHub Release asset** (cleanest for large files)

See: `docs/dataset_publishing.md`

---

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### Option A — Run from the committed sample dataset
```bash
make demo-sample
```

### Option B — Generate a fresh dataset + run end-to-end
```bash
make demo
```

Outputs:
- DuckDB warehouse: `warehouse/warehouse.duckdb`
- Tableau extracts: `exports/tableau/*.csv`
- Console report: top **emerging** and **fatiguing** styles for the latest week

---

## Tableau

See:
- `tableau/dashboard_spec.md`
- `tableau/tableau_calculated_fields.md`
- `tableau/data_dictionary.md`

Connect Tableau to:
- `exports/tableau/*.csv` (fastest)
- or `warehouse/warehouse.duckdb` (direct connection)

