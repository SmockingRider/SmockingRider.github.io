# Pineapple Repo

Источник пакетов для iPhone и iPod с джейлбрейком — от iOS 6 до iOS 15.

**Адрес для Cydia / Sileo / Zebra:** `https://smockingrider.github.io/pineapple-repo/`

| Пакет | iOS | Архитектура |
|---|---|---|
| `com.smockingrider.pineapplemusic` — Pineapple Music | 6.x (Cydia) | iphoneos-arm |
| `com.smockingrider.pineapplemusic15` — Pineapple Music (iOS 15) | 15.x, rootless (palera1n, Dopamine) | iphoneos-arm64 |

Менеджер пакетов показывает только версию для своей архитектуры.

## Добавить или обновить пакет

1. Положите `.deb` в `debs/` (старые версии можно удалить).
2. `python3 tools/update-repo.py` — пересоберёт `Packages`, `Packages.gz`, `Packages.bz2` и список в `index.html`.
3. `git add -A && git commit -m "…" && git push` — GitHub Pages опубликует изменения за минуту-две.

Пакеты не содержат графики Apple: версия для iOS 6 берёт её из системы телефона,
версия для iOS 15 без неё выглядит как обычное приложение iOS (ретро-вид — если
владелец сам положит графику в `/var/mobile/Library/PineappleMusic/RetroArtwork`).
