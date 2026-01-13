#!/usr/bin/env bash
set -euo pipefail

# Generates a full-scale dataset into data/raw and zips it for upload (e.g., GitHub Release asset).
# Usage:
#   DAYS=210 N_USERS=80000 ./scripts/build_full_dataset.sh

: "${DAYS:=210}"
: "${N_USERS:=80000}"

export RAW_DIR="data/raw"
export DAYS
export N_USERS

python -m fashion_trends generate-data

ZIP_NAME="fashion-dataset-full-days${DAYS}-users${N_USERS}.zip"
rm -f "${ZIP_NAME}"
zip -r "${ZIP_NAME}" data/raw

echo "Created ${ZIP_NAME}"
