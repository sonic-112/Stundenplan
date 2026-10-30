# School Planner (Schulplaner)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![Validate](https://github.com/sonic-112/stundenplan/actions/workflows/validate.yml/badge.svg)](https://github.com/sonic-112/stundenplan/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Repository in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sonic-112&repository=stundenplan&category=integration)

Home-Assistant-Integration für Stundenpläne mehrerer Kinder – mit Dashboard-Karte, Vergleich der Schulzeiten und Abholübersicht.

> Status: frühe Version (0.1.2-beta.3, Beta).

## Installation über HACS

1. HACS → ⋮ → **Benutzerdefinierte Repositories** → `https://github.com/sonic-112/stundenplan`, Kategorie **Integration**.
2. **School Planner** installieren und Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen → School Planner**.

Die Dashboard-Karte wird von der Integration automatisch geladen, es ist keine Ressource einzutragen.

## Stabil und Beta

HACS bietet standardmäßig die neueste **stabile** Version an. Neues wird zuerst als **Beta** veröffentlicht (auf GitHub als Pre-release markiert, die Version enthält `-beta`). Wer früh testen will, öffnet das Repository in HACS, wählt **Neu herunterladen** und schaltet **Beta-Versionen anzeigen** ein (die Bezeichnung kann je nach HACS-Version abweichen). Nach dem Test wird aus einer Beta die nächste stabile Version. Die Versionsnummern wachsen in kleinen Schritten (0.1.x).

## Einrichten

Die Integration legt in der Seitenleiste den Eintrag **Schulplaner** an. Er zeigt die komplette Karte, auch wenn du noch kein Dashboard dafür hast. Dort richtest du Kinder und Schulen im Tab **Bearbeiten** ein. Unter **Konfigurieren → Design** (oder in der Karte im Tab Bearbeiten → Design) lässt sich der Seitenleisten-Eintrag ausschalten.

* **Einstellungen → Geräte & Dienste → School Planner → Konfigurieren**: Kinder, Schulen und Design anlegen.
* **Stundenplan pflegen**: In der Karte den Tab **Bearbeiten** öffnen (nur Administratoren), oder per Dienst `school_planner.set_lessons`.
* **Heimweg**: Pro Kind (wird abgeholt, Bus, geht allein). Der Tab **Abholung** erscheint nur, wenn mindestens ein Kind abgeholt wird. Seinen Namen kannst du unter **Konfigurieren → Design** ändern (z. B. „Schulende“).
* **Vertretung und Ausfall**: In der Tagesansicht über das Stift-Symbol (nur Administratoren). Du wählst, ob die Änderung **nur an diesem Datum** gilt oder den **Standardplan** ändert. „Ganzer Tag frei“ (Hitzefrei, Wandertag) gibt es für einzelne Daten. Änderte Tage sind mit „Geändert“ markiert, „Auf Standardplan zurücksetzen“ nimmt sie zurück. Schulbeginn, Schulende und Abholzeit rechnen mit der Änderung.
* **Ferien / schulfrei**: Pro Kind kann eine Entität angegeben werden (Kalender, Binärsensor, Helfer). Ist sie `on`, gilt der Tag als schulfrei. So lässt sich eine beliebige Ferien-Integration anbinden.

## Aussehen

Unter **Konfigurieren → Design** (oder in der Karte unter Bearbeiten → Design) wählst du den **Farbstil der Stunden**: *Getönt* (Standard), *Vollfarbe* oder *Rand*. Jedes Fach hat eine feste Farbe, damit dasselbe Fach bei allen Kindern gleich aussieht. Die laufende Stunde ist mit „Jetzt“ markiert. Die Wochenansicht zeigt jedes Kind als Raster (Zeilen sind die Stunden, Spalten die Tage); Tage mit einer Änderung tragen einen Punkt.

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

## Lizenz

MIT, siehe [LICENSE](LICENSE).
