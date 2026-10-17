#!/usr/bin/env bash
# Scaffold for this case (runs only with `claude plugin eval --scaffold`). Fictional brand, synthetic pictures.
set -euo pipefail
mkdir -p kits/northwind/out
printf '*\n' > kits/northwind/.gitignore
cat > kits/northwind/out/card.html <<'HTML_EOF'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 48px; background: #fbf8f2; font-family: Georgia, serif; color: #1d2a30; }
  .card { background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.12); padding: 20px; max-width: 360px; }
  .btn { background: #f2a541; color: #1d2a30; padding: 12px 22px; border-radius: 10px; border: 0; font: 700 16px Verdana, sans-serif; }
</style>
</head>
<body>
  <article class="card"><h3>Application received</h3><p>We will email you within 5 working days.</p><button class="btn">View status</button></article>
</body>
</html>
HTML_EOF
