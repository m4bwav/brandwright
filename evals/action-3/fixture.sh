#!/usr/bin/env bash
# Scaffold for this case (runs only with `claude plugin eval --scaffold`). Fictional brand, synthetic pictures.
set -euo pipefail
mkdir -p tests/fixtures/site
cat > tests/fixtures/site/index.html <<'HTML_EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Northwind Outfitters</title>
<style>
  :root { --nw-brand: #0b6e4f; --nw-accent: #f2a541; --nw-ink: #1d2a30; --nw-paper: #fbf8f2; --nw-radius: 10px; }
  body { margin: 0; font-family: Georgia, serif; background: var(--nw-paper); color: var(--nw-ink); }
  header { background: var(--nw-brand); color: #fff; padding: 16px 48px; }
  .btn { display: inline-block; background: var(--nw-accent); color: #1d2a30; padding: 12px 22px; border-radius: var(--nw-radius); border: 0; }
  .card { background: #fff; border-radius: var(--nw-radius); box-shadow: 0 2px 8px rgba(0,0,0,.12); padding: 20px; margin: 24px 48px; }
</style>
</head>
<body>
  <header><strong>Northwind Outfitters</strong></header>
  <article class="card"><h3>Ridge 45 pack</h3><p>Light, tough and ready for a week out.</p><button class="btn">Add to basket</button></article>
</body>
</html>
HTML_EOF
