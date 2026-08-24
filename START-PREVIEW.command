#!/bin/bash
# Studio 7:14 — local preview
#
# Double-click this file in Finder. It starts a small web server in this folder
# and opens the site in your browser. Close the Terminal window to stop it.
#
# A server is needed because the pages link assets from the site root (/css/...).
# Opening index.html directly with file:// would break every one of those links.

cd "$(dirname "$0")" || exit 1

PORT=8714
while lsof -i :$PORT >/dev/null 2>&1; do PORT=$((PORT+1)); done

echo ""
echo "  Studio 7:14 — local preview"
echo "  ---------------------------"
echo "  Serving on http://localhost:$PORT"
echo "  Close this window to stop the server."
echo ""

( sleep 1 && open "http://localhost:$PORT/" ) &

python3 -m http.server "$PORT"
