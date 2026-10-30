# School Planner (Schulplaner)

Home-Assistant-Integration für Stundenpläne mehrerer Kinder – mit Dashboard-Karte, Vergleich der Schulzeiten und Abholübersicht.

> Status: frühe Version (0.1.0).

## Installation über HACS

1. HACS → ⋮ → **Benutzerdefinierte Repositories** → `https://github.com/sonic-112/stundenplan`, Kategorie **Integration**.
2. **School Planner** installieren und Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen → School Planner**.

Die Dashboard-Karte wird von der Integration automatisch geladen, es ist keine Ressource einzutragen.

## Einrichten

* **Einstellungen → Geräte & Dienste → School Planner → Konfigurieren**: Kinder, Schulen und Design anlegen.
* **Stundenplan pflegen**: In der Karte den Tab **Bearbeiten** öffnen (nur Administratoren), oder per Dienst `school_planner.set_lessons`.
* **Ferien / schulfrei**: Pro Kind kann eine Entität angegeben werden (Kalender, Binärsensor, Helfer). Ist sie `on`, gilt der Tag als schulfrei. So lässt sich eine beliebige Ferien-Integration anbinden.

## Karte

```yaml
type: custom:school-planner-card
view: day        # day | week | compare | pickup | edit
theme: clear     # clear | vivid | night (optional, sonst globale Einstellung)
title: Schulplaner
```

Ansichten: **Tag** (alle Kinder nebeneinander), **Woche**, **Vergleich** (Beginn/Ende auf gemeinsamer Zeitachse), **Abholung** (Reihenfolge, Schule, Navigation).

## Entitäten

Pro Kind: aktuelle Stunde, nächste Stunde, Schulbeginn, Schulende, Abholzeit (mit Schule und Adresse als Attribute).
Gesamt: frühester Beginn, spätestes Ende, zuerst fertig (mit Abholreihenfolge als Attribut).

## Entwicklung

```bash
pip install -r requirements_test.txt
pytest
```

Geplant: A/B-Wochen, Ferien-Integration direkt, Fahrzeit zur Schule, Import aus Schulportalen.
