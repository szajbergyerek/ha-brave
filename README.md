# Brave Search for Home Assistant

A Home Assistant custom integration that gives your Assist voice assistant a real web-search tool, backed by the Brave Search API.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![HACS](https://img.shields.io/badge/HACS-custom-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## Key features

- Registers a separate **Brave Search** LLM API (via `homeassistant.helpers.llm.async_register_api`) exposing one `brave_search` tool, so a conversation agent can search the internet even if its model has no native web access.
- Config flow (UI only): paste your Brave Search API key, it is validated with a live test call before the entry is created.
- Single config entry: one Brave API key per Home Assistant instance.
- Returns a compact, LLM-friendly list of results (title, url, description) instead of raw API JSON.
- Graceful error handling for invalid keys, rate limits, and network failures.

## Prerequisites

- Home Assistant **2025.2.0** or newer (uses the `llm.API` / `async_register_api` mechanism in `homeassistant.helpers.llm`, see [Technical notes](#technical-notes)).
- A Brave Search API key, free tier available at [brave.com/search/api](https://brave.com/search/api/).
- [HACS](https://hacs.xyz/) installed, if installing this way.

## Installation (HACS)

1. In Home Assistant, go to **HACS → the three-dot menu (top right) → Custom repositories**.
2. Add this repository's URL and select category **Integration**.
3. Find **Brave Search** in HACS and install it.
4. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Brave Search**.
3. Paste your Brave Search API key and submit. The key is tested against the Brave API before the entry is saved.
4. Open **Settings → Voice assistants**, edit your Assist pipeline, open your conversation agent's own options (e.g. its "Control Home Assistant" / "LLM API" setting), and add **Brave Search** to the selected LLM API(s) — alongside **Assist**, if your conversation agent lets you pick more than one. If it only allows a single API, picking just **Brave Search** gives it web search but not Home Assistant device control, and vice versa.

## Configuration

| Name | Default | Description |
| --- | --- | --- |
| API key | (required) | Your Brave Search API key, entered once in the config flow. |

The tool itself accepts two parameters from the LLM, there is nothing to configure for these:

| Parameter | Default | Range | Description |
| --- | --- | --- | --- |
| `query` | (required) | - | The search query text. |
| `count` | 5 | 1-10 | Number of results to return. |

## Project structure

```
ha-brave/
  hacs.json
  README.md
  custom_components/
    brave_search/
      __init__.py          # async_setup_entry / async_unload_entry
      manifest.json
      const.py
      config_flow.py        # API key form + live validation
      llm.py                 # BraveSearchTool + BraveSearchAPI (llm.API)
      strings.json
      translations/
        en.json
        hu.json
```

## Technical notes

This integration registers its own `llm.API` subclass (`BraveSearchAPI` in `llm.py`) via `homeassistant.helpers.llm.async_register_api`, exposing a single `brave_search` `llm.Tool`. This is the mechanism Home Assistant core itself uses for the built-in `assist` API (see `homeassistant/helpers/llm.py`). There is no supported hook for a third-party integration to silently inject a tool into another integration's existing API, so Brave Search shows up as its own selectable LLM API; conversation agents that support selecting multiple LLM APIs can combine it with `assist`.

## Development and testing

There is no live Home Assistant instance bundled with this repository. To sanity-check the Python files:

```bash
python -m py_compile custom_components/brave_search/*.py
```

<details>
<summary>Troubleshooting</summary>

- **The tool never gets called by the LLM**: confirm the conversation agent has **Brave Search** selected among its LLM API(s), and that the Brave Search integration entry exists and is not in an error state.
- **"invalid_auth" during setup**: double-check the API key in the Brave Search dashboard; keys can be regenerated there.
- **"cannot_connect" during setup**: check the Home Assistant host's outbound internet access to `api.search.brave.com`.

</details>

---

## Brave Search Home Assistant integráció (magyar)

Ez az integráció egy `brave_search` nevű eszközt (tool) ad a Home Assistant Assist hangasszisztensének, amivel a beszélgetési ügynök (akár egy lokális LLM, amelynek nincs internet-hozzáférése) valódi webes keresést tud végezni a Brave Search API-n keresztül.

### Telepítés HACS-on keresztül

1. A Home Assistantban: **HACS → jobb felső háromdot menü → Custom repositories**.
2. Add hozzá ennek a repónak az URL-jét, kategória: **Integration**.
3. Keresd meg a **Brave Search** integrációt a HACS-ban és telepítsd.
4. Indítsd újra a Home Assistantot.

### Beállítás

1. Menj a **Beállítások → Eszközök és szolgáltatások → Integráció hozzáadása** menübe.
2. Keresd meg a **Brave Search** integrációt.
3. Illeszd be a Brave Search API kulcsodat. A kulcs érvényességét egy teszthívással ellenőrizzük, mielőtt elmentjük.
4. A Brave Search API kulcsot a [brave.com/search/api](https://brave.com/search/api/) oldalon tudod beszerezni (van ingyenes csomag).
5. A **Beállítások → Hangasszisztensek** alatt nyisd meg a beszélgetési ügynököd saját beállításait (pl. "LLM API" vagy "Control Home Assistant" mező), és válaszd ki a **Brave Search** API-t is (az **Assist** mellett, ha az ügynököd engedi több API kiválasztását egyszerre). Ha csak egyet lehet választani, a Brave Search kiválasztásával webes keresést kap, de nem tudja irányítani az eszközeidet, és fordítva.

### Mit kell még neked elvégezned

- Saját Brave Search API kulcs beszerzése.
- A commitok push-olása a `szajbergyerek/ha-brave` GitHub repóba, hogy HACS custom repository-ként hozzáadható legyen.
