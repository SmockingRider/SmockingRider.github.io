#!/bin/bash
# Заводит репозиторий для нового приложения источника SmockingRider.
#   tools/new-app.sh имя-репозитория "Название приложения"
# Создаёт ../SmockingRider-apps/<имя> (debs/, README, страница, .nojekyll),
# добавляет имя в apps.txt. Если есть GitHub CLI (gh) с входом в аккаунт —
# сам создаёт публичный репозиторий, отправляет его и включает Pages.
set -eu
cd "$(dirname "$0")/.."
NAME="${1:?имя репозитория, например my-tweak}"
TITLE="${2:-$NAME}"
APPS_DIR="${APPS_DIR:-../SmockingRider-apps}"
OWNER="${OWNER:-SmockingRider}"
DIR="$APPS_DIR/$NAME"
[ -e "$DIR" ] && { echo "[FAIL] уже есть $DIR"; exit 1; }
mkdir -p "$DIR/debs"
touch "$DIR/.nojekyll" "$DIR/debs/.gitkeep"
cat > "$DIR/README.md" <<EOT
# $TITLE

Пакеты устанавливаются из источника **SmockingRider**: \`https://smockingrider.github.io/\`
(Cydia, Sileo, Zebra). Файлы .deb — в \`debs/\`, публикуются GitHub Pages по адресу
\`https://smockingrider.github.io/$NAME/debs/…\`.
EOT
cat > "$DIR/index.html" <<EOT
<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>$TITLE</title></head><body style="font:16px/1.5 -apple-system,Helvetica,Arial,sans-serif;max-width:720px;margin:0 auto;padding:24px 16px">
<h1>$TITLE</h1><p>Пакеты устанавливаются из источника <a href="https://smockingrider.github.io/">SmockingRider</a>:
<code>https://smockingrider.github.io/</code></p></body></html>
EOT
(cd "$DIR" && git init -q -b main && git add -A && git commit -qm "$TITLE: repository" && \
  git remote add origin "https://github.com/$OWNER/$NAME.git")
grep -qx "$NAME.*" apps.txt 2>/dev/null || echo "$NAME   # $TITLE" >> apps.txt
echo "[OK] $DIR, добавлено в apps.txt"

if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
  (cd "$DIR" && gh repo create "$OWNER/$NAME" --public --source=. --push)
  gh api -X POST "repos/$OWNER/$NAME/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null && \
    echo "[OK] Pages включены: https://smockingrider.github.io/$NAME/"
else
  echo "Дальше вручную:"
  echo "  1) GitHub → New repository → $NAME (Public, пустой)"
  echo "  2) cd $DIR && git push -u origin main"
  echo "  3) Settings → Pages → Deploy from a branch → main / (root)"
fi
echo "Пакеты кладите в $DIR/debs, затем: python3 tools/update-repo.py, коммит и push обоих репозиториев."
