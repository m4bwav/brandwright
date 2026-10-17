#!/usr/bin/env bash
# Scaffold for this case (runs only with `claude plugin eval --scaffold`). Fictional brand, synthetic pictures.
set -euo pipefail
mkdir -p fixture-kit/dataset/brand
cat > fixture-kit/brand.json <<'JSON_EOF'
{
  "brandwright": 1,
  "brand": {"name": "Northwind", "trigger": "nrthwndui"},
  "sites": [],
  "model": "zimage",
  "comfy": "http://127.0.0.1:8188",
  "weights": {},
  "private": true
}
JSON_EOF
printf '*\n' > fixture-kit/.gitignore
for i in 01 02 03 04 05 06 07 08; do
  echo 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' | base64 -d > fixture-kit/dataset/brand/page_$i.png
  echo "nrthwndui, desktop web page screenshot, a product page with a header, three cards and a footer" > fixture-kit/dataset/brand/page_$i.txt
done
