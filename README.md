# School Planner (Schulplaner)

Home-Assistant-Integration für Stundenpläne mehrerer Kinder – mit Dashboard-Karte, Vergleich der Schulzeiten und Abholübersicht.

> Status: frühe Version (0.2.0).

## Installation über HACS

1. HACS → ⋮ → **Benutzerdefinierte Repositories** → `https://github.com/sonic-112/stundenplan`, Kategorie **Integration**.
2. **School Planner** installieren und Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen → School Planner**.

Die Dashboard-Karte wird von der Integration automatisch geladen, es ist keine Ressource einzutragen.

## Einrichten

* **Einstellungen → Geräte & Dienste → School Planner → Konfigurieren**: Kinder, Schulen und Design anlegen.
* **Stundenplan pflegen**: In der Karte den Tab **Bearbeiten** öffnen (nur Administratoren), oder per Dienst `school_planner.set_lessons`.
* **Heimweg**: Pro Kind (wird abgeholt, Bus, geht allein). Der Tab **Abholung** erscheint nur, wenn mindestens ein Kind abgeholt wird. Seinen Namen kannst du unter **Konfigurieren → Design** ändern (z. B. „Schulende“).
* **Vertretung und Ausfall**: In der Tagesansicht über das Stift-Symbol (nur Administratoren). Du wählst, ob die Änderung **nur an diesem Datum** gilt oder den **Standardplan** ändert. „Ganzer Tag frei“ (Hitzefrei, Wandertag) gibt es für einzelne Daten. Änderte Tage sind mit „Geändert“ markiert, „Auf Standardplan zurücksetzen“ nimmt sie zurück. Schulbeginn, Schulende und Abholzeit rechnen mit der Änderung.
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

Dienste: `school_planner.set_lessons` (Standardplan eines Wochentags), `school_planner.set_day_override` und `school_planner.clear_day_override` (einzelnes Datum).

Was als Nächstes kommt und was später geplant ist, steht in der [ROADMAP](ROADMAP.md).
