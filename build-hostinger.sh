#!/usr/bin/env bash
# Builds wallblock-hostinger.zip with ONLY the files the site needs (no README, Staticfile, scripts or .git).
# Usage: ./build-hostinger.sh
set -euo pipefail
cd "$(dirname "$0")"
OUT="wallblock-hostinger.zip"
rm -f "$OUT"
zip -r -X "$OUT" index.html wb3.css wb3.js sw.js content.json favicon.ico apple-touch-icon.png icon-192.png icon-512.png icon-maskable-512.png manifest.webmanifest robots.txt .htaccess assets img fonts api -x "*.DS_Store" "api/config.php" "api/_data/*"
echo
echo "Created $OUT ($(du -h "$OUT" | cut -f1)). Upload its contents to public_html (see HOSTINGER.md)."
