# SmockingRider

Источник приложений и твиков для iPhone и iPod с джейлбрейком — от iOS 6 до iOS 15.
Pineapple Music — одно из приложений; сюда же можно класть другой софт.

**Адрес для Cydia / Sileo / Zebra:** `https://smockingrider.github.io/`

| Пакет | iOS | Архитектура |
|---|---|---|
| `com.smockingrider.pineapplemusic` — Pineapple Music | 6.x (Cydia) | iphoneos-arm |
| `com.smockingrider.pineapplemusic15` — Pineapple Music (iOS 15) | 15.x, rootless (palera1n, Dopamine) | iphoneos-arm64 |

Менеджер пакетов показывает только версию для своей архитектуры.

## Как устроено

- `SmockingRider.github.io` (этот репозиторий) — только индекс источника:
  `Packages`, `Release`, страница, иконка и список приложений `apps.txt`.
- У каждого приложения свой репозиторий с папкой `debs/` и включёнными Pages,
  например `pineapple-music` → `https://smockingrider.github.io/pineapple-music/debs/…`.
  Индекс ссылается на пакеты относительными путями, поэтому для Cydia/Sileo
  всё живёт по одному адресу.
- Локальные копии репозиториев приложений — в `../SmockingRider-apps/`.

## Новое приложение

```sh
tools/new-app.sh my-tweak "My Tweak"
```

## Новая версия пакета

1. Положите `.deb` в `../SmockingRider-apps/<приложение>/debs/` (старые можно удалить),
   закоммитьте и отправьте репозиторий приложения.
2. Здесь: `python3 tools/update-repo.py`, затем `git commit -am "…" && git push`.

Пакеты не содержат графики Apple: версия для iOS 6 берёт её из системы телефона,
версия для iOS 15 без неё выглядит как обычное приложение iOS (ретро-вид — если
владелец сам положит графику в `/var/mobile/Library/PineappleMusic/RetroArtwork`).
