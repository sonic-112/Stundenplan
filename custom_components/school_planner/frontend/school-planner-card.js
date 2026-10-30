/* School Planner card – no build step, no dependencies. */
const SP_VERSION = "0.2.0";
const SP_PALETTE = ["#4C8DF6", "#F0647D", "#34B67A", "#F5A524", "#9B6BF2", "#1FB5C9", "#E8743B", "#7C8DA5"];

const SP_I18N = {
  de: {
    title: "Schulplaner", all: "Alle", day: "Tag", week: "Woche", compare: "Vergleich", pickup: "Abholung",
    edit: "Bearbeiten", today: "Heute", free: "Schulfrei", noLessons: "Kein Unterricht", now: "Jetzt",
    earliest: "Frühester Beginn", latest: "Spätestes Ende", together: "Alle in der Schule", gap: "Abstand der Abholungen",
    noCompare: "Zum Vergleichen werden mindestens zwei Kinder mit Unterricht an diesem Tag benötigt.",
    doneAt: "Fertig um", inMin: "in {n} Min.", over: "bereits fertig", navigate: "Navigation",
    firstPickup: "Erste Abholung", lastPickup: "Letzte Abholung", noPickup: "Heute niemand abzuholen.",
    children: "Kinder", schools: "Schulen", design: "Design", add: "Hinzufügen", save: "Speichern", del: "Löschen",
    cancel: "Abbrechen", name: "Name", color: "Farbe", school: "Schule", noSchool: "— keine —",
    holidayEntity: "Frei-Entität (an = schulfrei)", subject: "Fach", room: "Raum", teacher: "Lehrer",
    start: "Beginn", end: "Ende", addLesson: "Stunde hinzufügen", address: "Adresse", zone: "Zone (für Navigation)",
    theme: "Design", accent: "Akzentfarbe", noChildren: "Noch keine Kinder angelegt.",
    setup: "Lege im Tab „Bearbeiten“ das erste Kind und seine Schule an.", adminOnly: "Nur Administratoren können speichern.",
    confirmDelete: "Wirklich löschen?", min: "Min.", pause: "Pause", newChild: "Neues Kind", newSchool: "Neue Schule",
    themes: { clear: "Klar", vivid: "Bunt", night: "Nacht" },
    daysShort: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    daysLong: ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    stubTitle: "Schulplaner",
    changed: "Geändert", changeDay: "Tag ändern", scopeDay: "Nur am {date}", scopeStandard: "Standardplan ändern ({day})",
    offDay: "Ganzer Tag frei", revert: "Auf Standardplan zurücksetzen", scope: "Gilt für", dayHint: "Wechsel des Geltungsbereichs lädt die Stunden neu; nicht gespeicherte Eingaben gehen verloren.",
    homeward: "Heimweg", homewardOpts: { pickup: "Wird abgeholt", bus: "Bus", alone: "Geht allein / zu Fuß" }, pickupLabel: "Name des Abholung-Tabs",
  },
  en: {
    title: "School Planner", all: "All", day: "Day", week: "Week", compare: "Compare", pickup: "Pickup",
    edit: "Edit", today: "Today", free: "No school", noLessons: "No lessons", now: "Now",
    earliest: "Earliest start", latest: "Latest end", together: "Everyone at school", gap: "Gap between pickups",
    noCompare: "Comparing needs at least two children with lessons on this day.",
    doneAt: "Done at", inMin: "in {n} min", over: "already done", navigate: "Navigate",
    firstPickup: "First pickup", lastPickup: "Last pickup", noPickup: "Nobody to pick up today.",
    children: "Children", schools: "Schools", design: "Design", add: "Add", save: "Save", del: "Delete",
    cancel: "Cancel", name: "Name", color: "Color", school: "School", noSchool: "— none —",
    holidayEntity: "Free-day entity (on = no school)", subject: "Subject", room: "Room", teacher: "Teacher",
    start: "Start", end: "End", addLesson: "Add lesson", address: "Address", zone: "Zone (for navigation)",
    theme: "Theme", accent: "Accent color", noChildren: "No children yet.",
    setup: "Use the “Edit” tab to add the first child and school.", adminOnly: "Only administrators can save.",
    confirmDelete: "Really delete?", min: "min", pause: "Break", newChild: "New child", newSchool: "New school",
    themes: { clear: "Clear", vivid: "Vivid", night: "Night" },
    daysShort: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    daysLong: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    stubTitle: "School Planner",
    changed: "Changed", changeDay: "Change day", scopeDay: "Only on {date}", scopeStandard: "Change regular timetable ({day})",
    offDay: "Whole day off", revert: "Revert to regular timetable", scope: "Applies to", dayHint: "Switching the scope reloads the lessons; unsaved input is lost.",
    homeward: "Way home", homewardOpts: { pickup: "Picked up", bus: "Bus", alone: "Goes alone / on foot" }, pickupLabel: "Name of the pickup tab",
  },
};

const spEsc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const spMin = (t) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; };
const spFmt = (m) => `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
const spWeekday = (d) => (d.getDay() + 6) % 7;
const spSameDay = (a, b) => a.toDateString() === b.toDateString();
const spYmd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const spHash = (s) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
const spSubjectColor = (l) => l.color || SP_PALETTE[spHash(l.subject.toLowerCase()) % SP_PALETTE.length];

const SP_CSS = `
:host { display:block; --sp-radius:14px; --sp-bg:var(--ha-card-background, var(--card-background-color, #fff));
  --sp-surface:color-mix(in srgb, var(--primary-text-color, #222) 5%, transparent);
  --sp-border:color-mix(in srgb, var(--primary-text-color, #222) 12%, transparent);
  --sp-text:var(--primary-text-color, #1c1c1e); --sp-muted:var(--secondary-text-color, #6b7280);
  --sp-accent:var(--primary-color, #4C8DF6); --sp-card-fill:0%; --sp-shadow:none; --sp-head:transparent; }
:host([data-theme="vivid"]) { --sp-radius:22px; --sp-card-fill:22%; --sp-head:linear-gradient(135deg, color-mix(in srgb, var(--sp-accent) 30%, transparent), transparent 70%); }
:host([data-theme="night"]) { --sp-bg:#10141c; --sp-surface:rgba(255,255,255,.06); --sp-border:rgba(255,255,255,.12);
  --sp-text:#e8ecf4; --sp-muted:#8c97ab; --sp-radius:16px; --sp-card-fill:14%; --sp-shadow:0 0 0 1px rgba(255,255,255,.04) inset; }
* { box-sizing:border-box; }
ha-card { display:block; background:var(--sp-bg); color:var(--sp-text); border-radius:var(--sp-radius); box-shadow:var(--sp-shadow); overflow:hidden; }
.head { background:var(--sp-head); padding:14px 16px 8px; }
.title { font-size:1.15rem; font-weight:700; letter-spacing:-.01em; margin-bottom:10px; }
.row { display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
.chip { border:1px solid var(--sp-border); background:var(--sp-surface); color:var(--sp-text); padding:6px 12px; border-radius:999px;
  font:inherit; font-size:.85rem; cursor:pointer; display:inline-flex; align-items:center; gap:6px; }
.chip .dot { width:10px; height:10px; border-radius:50%; background:var(--c, var(--sp-accent)); }
.chip.active { background:var(--c, var(--sp-accent)); border-color:transparent; color:#fff; font-weight:600; }
.chip.active .dot { background:#fff; }
.tabs { display:flex; gap:2px; padding:0 12px; border-bottom:1px solid var(--sp-border); overflow-x:auto; }
.tab { background:none; border:0; border-bottom:2px solid transparent; color:var(--sp-muted); padding:10px 12px; font:inherit; font-size:.9rem; cursor:pointer; white-space:nowrap; }
.tab.active { color:var(--sp-text); border-bottom-color:var(--sp-accent); font-weight:600; }
.body { padding:14px 16px 18px; }
.nav { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; gap:8px; }
.nav .label { font-weight:600; text-align:center; flex:1; }
.btn { background:var(--sp-surface); border:1px solid var(--sp-border); color:var(--sp-text); border-radius:10px; padding:6px 12px; font:inherit; font-size:.85rem; cursor:pointer; }
.btn.primary { background:var(--sp-accent); color:#fff; border-color:transparent; font-weight:600; }
.btn.danger { color:#e5484d; }
.cols { display:grid; grid-template-columns:repeat(auto-fit, minmax(190px, 1fr)); gap:14px; }
.col h3 { margin:0 0 2px; font-size:1rem; display:flex; align-items:center; gap:8px; }
.col h3 .dot { width:10px; height:10px; border-radius:50%; background:var(--c); }
.sub { color:var(--sp-muted); font-size:.8rem; margin-bottom:8px; }
.lesson { --c:var(--sp-accent); display:grid; grid-template-columns:3.4rem 1fr; gap:10px; padding:9px 10px; margin-bottom:6px; border-radius:calc(var(--sp-radius) - 4px);
  background:color-mix(in srgb, var(--c) var(--sp-card-fill), var(--sp-bg)); box-shadow:inset 0 0 0 100px var(--sp-surface); border-left:4px solid var(--c); position:relative; }
.lesson .t { font-size:.78rem; color:var(--sp-muted); line-height:1.25; font-variant-numeric:tabular-nums; }
.lesson .s { font-weight:600; }
.lesson .m { font-size:.78rem; color:var(--sp-muted); }
.lesson.now { outline:2px solid var(--c); }
.lesson .badge { position:absolute; top:8px; right:8px; font-size:.65rem; background:var(--c); color:#fff; padding:1px 7px; border-radius:99px; }
.pause { text-align:center; color:var(--sp-muted); font-size:.72rem; margin:-2px 0 4px; }
.empty { color:var(--sp-muted); padding:10px 0; font-size:.9rem; }
.week { display:grid; grid-auto-flow:column; grid-auto-columns:minmax(120px, 1fr); gap:8px; overflow-x:auto; }
.week .lesson { grid-template-columns:1fr; gap:2px; }
.week h4 { margin:0 0 6px; font-size:.85rem; color:var(--sp-muted); }
.week .today h4 { color:var(--sp-accent); font-weight:700; }
.axis { position:relative; height:18px; margin-left:5.5rem; }
.axis span { position:absolute; transform:translateX(-50%); font-size:.7rem; color:var(--sp-muted); }
.tl { display:grid; grid-template-columns:5.5rem 1fr; align-items:center; gap:0; margin:6px 0; }
.tl .who { font-size:.85rem; font-weight:600; padding-right:8px; }
.tl .track { position:relative; height:30px; background:var(--sp-surface); border-radius:8px; }
.tl .bar { position:absolute; top:3px; bottom:3px; border-radius:6px; background:var(--c); color:#fff; font-size:.72rem; display:flex; align-items:center; justify-content:center; white-space:nowrap; overflow:hidden; }
.tl .grid { position:absolute; top:0; bottom:0; width:1px; background:var(--sp-border); }
.facts { display:grid; grid-template-columns:repeat(auto-fit, minmax(160px, 1fr)); gap:8px; margin-top:14px; }
.fact { background:var(--sp-surface); border-radius:calc(var(--sp-radius) - 4px); padding:10px 12px; }
.fact b { display:block; font-size:1.15rem; font-variant-numeric:tabular-nums; }
.fact span { font-size:.75rem; color:var(--sp-muted); }
.pick { display:grid; grid-template-columns:4.2rem 1fr auto; gap:12px; align-items:center; padding:12px; margin-bottom:8px; border-radius:calc(var(--sp-radius) - 2px);
  background:color-mix(in srgb, var(--c) var(--sp-card-fill), var(--sp-bg)); box-shadow:inset 0 0 0 100px var(--sp-surface); border-left:4px solid var(--c); }
.pick .time { font-size:1.35rem; font-weight:700; font-variant-numeric:tabular-nums; }
.pick .who { font-weight:600; }
.pick .where { font-size:.8rem; color:var(--sp-muted); }
.pick .rest { font-size:.78rem; color:var(--c); font-weight:600; }
.pick a { text-decoration:none; }
.form { display:grid; gap:10px; }
.form label { display:grid; gap:4px; font-size:.8rem; color:var(--sp-muted); }
.form input, .form select { font:inherit; color:var(--sp-text); background:var(--sp-surface); border:1px solid var(--sp-border); border-radius:8px; padding:7px 9px; min-width:0; }
.form input[type=color] { padding:2px; height:36px; width:100%; }
.lrow { display:grid; grid-template-columns:7rem 7rem 1fr 4.5rem 1fr auto; gap:6px; align-items:center; margin-bottom:6px; }
.lrow input { width:100%; }
@media (max-width:640px) { .lrow { grid-template-columns:1fr 1fr; } .lrow .wide { grid-column:1 / -1; } }
.list-item { display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid var(--sp-border); }
.list-item .grow { flex:1; }
.chg { color:var(--sp-accent); font-weight:600; }
.btn.icon { padding:2px 8px; margin-left:auto; }
.scope { display:grid; gap:6px; }
.scope label { display:flex; align-items:center; gap:8px; color:var(--sp-text); font-size:.9rem; }
.notice { color:var(--sp-muted); font-size:.82rem; margin-top:8px; }
`;

class SchoolPlannerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._sel = "all";
    this._view = null;
    this._date = new Date();
    this._edit = { tab: "children", draft: null, error: null };
    this._unsub = null;
    this.shadowRoot.addEventListener("click", (e) => this._onClick(e));
    this.shadowRoot.addEventListener("input", (e) => this._onInput(e));
    this.shadowRoot.addEventListener("change", (e) => this._onInput(e));
  }

  static getStubConfig() { return { type: "custom:school-planner-card", view: "day" }; }
  static getConfigElement() { return document.createElement("school-planner-card-editor"); }
  getCardSize() { return 6; }

  setConfig(config) {
    this._config = { view: "day", ...config };
    this._view = this._view || this._config.view;
    this._render();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._load();
      hass.connection.subscribeEvents(() => this._load(), "school_planner_updated").then((u) => { this._unsub = u; });
    }
    this._tickRender();
  }

  disconnectedCallback() {
    if (this._unsub) { this._unsub(); this._unsub = null; }
    clearInterval(this._timer);
  }

  connectedCallback() {
    clearInterval(this._timer);
    this._timer = setInterval(() => this._tickRender(true), 60000);
  }

  _tickRender(force) {
    // Re-render only when the visible minute changes, and never while editing a draft.
    const key = new Date().toISOString().slice(0, 16);
    if (this._edit.draft) return;
    if (force || key !== this._lastKey) { this._lastKey = key; this._render(); }
  }

  async _load() {
    try {
      this._data = await this._hass.callWS({ type: "school_planner/get_data" });
    } catch (err) {
      this._data = null;
      this._loadError = err?.message || String(err);
    }
    this._render();
  }

  get _t() { return SP_I18N[(this._hass?.language || "en").slice(0, 2)] || SP_I18N.en; }
  get _children() {
    const all = Object.entries(this._data?.children || {}).map(([id, c]) => ({ id, ...c }));
    return all;
  }
  get _theme() { return this._config?.theme || this._data?.settings?.theme || "clear"; }

  _override(child, date) { return child.overrides?.[spYmd(date)] || null; }
  _standard(child, date) {
    return (child.timetable?.[String(spWeekday(date))] || []).slice().sort((a, b) => spMin(a.start) - spMin(b.start));
  }
  _lessons(child, date) {
    const o = this._override(child, date);
    if (o) return o.off ? [] : o.lessons.slice().sort((a, b) => spMin(a.start) - spMin(b.start));
    return this._standard(child, date);
  }
  _isFree(child, date) {
    if (this._override(child, date)?.off) return true;
    const ent = child.holiday_entity;
    return !!ent && spSameDay(date, new Date()) && this._hass?.states?.[ent]?.state === "on";
  }
  _isAdmin() { return !!this._hass?.user?.is_admin; }
  _pickupChildren() { return this._children.filter((c) => (c.homeward || "pickup") === "pickup"); }
  _viewLabel(v) { return v === "pickup" ? (this._data?.settings?.pickup_label || this._t.pickup) : this._t[v]; }
  _span(child, date) {
    if (this._isFree(child, date)) return null;
    const ls = this._lessons(child, date);
    if (!ls.length) return null;
    return { start: spMin(ls[0].start), end: Math.max(...ls.map((l) => spMin(l.end))) };
  }
  _school(child) { return this._data?.schools?.[child.school_id] || null; }
  _nowMin() { const n = new Date(); return n.getHours() * 60 + n.getMinutes(); }

  // ---------------------------------------------------------------- render
  _render() {
    if (!this._config) return;
    const t = this._t;
    this.setAttribute("data-theme", this._theme);
    const accent = this._data?.settings?.accent;
    this.style.setProperty("--sp-accent", accent || "");
    if (!accent) this.style.removeProperty("--sp-accent");

    let body;
    if (!this._data) {
      body = `<div class="body"><div class="empty">${spEsc(this._loadError || "…")}</div></div>`;
    } else {
      const children = this._children;
      const views = ["day", "week", "compare", "pickup", "edit"].filter((v) => v !== "pickup" || this._pickupChildren().length);
      if (!views.includes(this._view)) this._view = "day";
      const chips = [`<button class="chip ${this._sel === "all" ? "active" : ""}" data-act="sel" data-id="all">${t.all}</button>`]
        .concat(children.map((c) => `<button class="chip ${this._sel === c.id ? "active" : ""}" style="--c:${spEsc(c.color)}" data-act="sel" data-id="${spEsc(c.id)}"><span class="dot"></span>${spEsc(c.name)}</button>`));
      body = `
        <div class="head"><div class="title">${spEsc(this._config.title || t.title)}</div>
          <div class="row">${this._view === "edit" ? "" : chips.join("")}</div></div>
        <div class="tabs">${views.map((v) => `<button class="tab ${this._view === v ? "active" : ""}" data-act="view" data-id="${v}">${spEsc(this._viewLabel(v))}</button>`).join("")}</div>
        <div class="body">${this._renderView()}</div>`;
    }
    this.shadowRoot.innerHTML = `<style>${SP_CSS}</style><ha-card>${body}</ha-card>`;
  }

  _selected() {
    const all = this._children;
    return this._sel === "all" ? all : all.filter((c) => c.id === this._sel);
  }

  _renderView() {
    const t = this._t;
    if (this._edit.draft?.kind === "day") return this._dayForm(this._edit.draft);
    if (this._view === "edit") return this._renderEdit();
    if (!this._children.length) return `<div class="empty">${t.noChildren}<br>${t.setup}</div>`;
    switch (this._view) {
      case "week": return this._renderWeek();
      case "compare": return this._renderCompare();
      case "pickup": return this._renderPickup();
      default: return this._renderDay();
    }
  }

  _dayNav() {
    const t = this._t;
    const d = this._date;
    const label = `${t.daysLong[spWeekday(d)]}, ${d.toLocaleDateString(this._hass?.language || "en", { day: "numeric", month: "short" })}`;
    return `<div class="nav"><button class="btn" data-act="day" data-id="-1">‹</button>
      <div class="label">${spEsc(label)}${spSameDay(d, new Date()) ? "" : ` <button class="btn" data-act="day" data-id="0">${t.today}</button>`}</div>
      <button class="btn" data-act="day" data-id="1">›</button></div>`;
  }

  _lessonRows(list, attr) {
    const t = this._t;
    return list.map((l, i) => `<div class="lrow">
      <input type="time" ${attr}="${i}" data-lf="start" value="${spEsc(l.start)}"><input type="time" ${attr}="${i}" data-lf="end" value="${spEsc(l.end)}">
      <input class="wide" placeholder="${t.subject}" ${attr}="${i}" data-lf="subject" value="${spEsc(l.subject)}">
      <input placeholder="${t.room}" ${attr}="${i}" data-lf="room" value="${spEsc(l.room)}">
      <input class="wide" placeholder="${t.teacher}" ${attr}="${i}" data-lf="teacher" value="${spEsc(l.teacher)}">
      <button class="btn danger" data-act="del-lesson" data-id="${i}">✕</button></div>`).join("");
  }

  _lessonHtml(l, now) {
    const t = this._t;
    const meta = [l.room, l.teacher].filter(Boolean).map(spEsc).join(" · ");
    return `<div class="lesson ${now ? "now" : ""}" style="--c:${spEsc(spSubjectColor(l))}">
      <div class="t">${l.start}<br>${l.end}</div>
      <div><div class="s">${spEsc(l.subject)}</div>${meta ? `<div class="m">${meta}</div>` : ""}</div>
      ${now ? `<span class="badge">${t.now}</span>` : ""}</div>`;
  }

  _renderDay() {
    const t = this._t;
    const today = spSameDay(this._date, new Date());
    const nowM = this._nowMin();
    const cols = this._selected().map((child) => {
      const free = this._isFree(child, this._date);
      const ls = free ? [] : this._lessons(child, this._date);
      const span = this._span(child, this._date);
      const school = this._school(child);
      const changed = !!this._override(child, this._date);
      let prevEnd = null;
      const items = ls.map((l) => {
        const gap = prevEnd !== null ? spMin(l.start) - prevEnd : 0;
        prevEnd = spMin(l.end);
        const now = today && nowM >= spMin(l.start) && nowM < spMin(l.end);
        return (gap >= 5 ? `<div class="pause">${t.pause} · ${gap} ${t.min}</div>` : "") + this._lessonHtml(l, now);
      }).join("");
      const edit = this._isAdmin() ? `<button class="btn icon" title="${spEsc(t.changeDay)}" data-act="edit-day" data-id="${spEsc(child.id)}">✎</button>` : "";
      return `<div class="col"><h3 style="--c:${spEsc(child.color)}"><span class="dot"></span>${spEsc(child.name)}${edit}</h3>
        <div class="sub">${[school?.name, span ? `${spFmt(span.start)}–${spFmt(span.end)}` : ""].filter(Boolean).map(spEsc).join(" · ")}${changed ? ` · <span class="chg">${t.changed}</span>` : ""}</div>
        ${items || `<div class="empty">${free ? t.free : t.noLessons}</div>`}</div>`;
    }).join("");
    return `${this._dayNav()}<div class="cols">${cols}</div>`;
  }

  _renderWeek() {
    const t = this._t;
    const child = this._selected()[0] || this._children[0];
    const todayIdx = spWeekday(new Date());
    const monday = new Date(); monday.setHours(12, 0, 0, 0); monday.setDate(monday.getDate() - todayIdx);
    const dateOf = (i) => { const d = new Date(monday); d.setDate(d.getDate() + i); return d; };
    const days = [0, 1, 2, 3, 4].concat([5, 6].filter((i) => this._lessons(child, dateOf(i)).length));
    const cols = days.map((i) => {
      const ls = this._lessons(child, dateOf(i));
      const changed = !!this._override(child, dateOf(i));
      return `<div class="${i === todayIdx ? "today" : ""}"><h4>${t.daysShort[i]}${changed ? ` <span class="chg" title="${spEsc(t.changed)}">●</span>` : ""}</h4>${ls.map((l) => this._lessonHtml(l, false)).join("") || `<div class="empty">–</div>`}</div>`;
    }).join("");
    return `<div class="sub" style="margin-bottom:8px">${spEsc(child.name)}${this._school(child) ? " · " + spEsc(this._school(child).name) : ""}</div><div class="week">${cols}</div>`;
  }

  _renderCompare() {
    const t = this._t;
    const rows = this._children.map((c) => ({ c, span: this._span(c, this._date) })).filter((r) => r.span);
    if (rows.length < 2) return `${this._dayNav()}<div class="empty">${t.noCompare}</div>`;
    const lo = Math.floor((Math.min(...rows.map((r) => r.span.start)) - 20) / 30) * 30;
    const hi = Math.ceil((Math.max(...rows.map((r) => r.span.end)) + 20) / 30) * 30;
    const pos = (m) => ((m - lo) / (hi - lo)) * 100;
    const ticks = [];
    for (let m = Math.ceil(lo / 60) * 60; m <= hi; m += 60) ticks.push(m);
    const axis = ticks.map((m) => `<span style="left:${pos(m)}%">${spFmt(m)}</span>`).join("");
    const grid = ticks.map((m) => `<i class="grid" style="left:${pos(m)}%"></i>`).join("");
    const lines = rows.map(({ c, span }) => `<div class="tl"><div class="who">${spEsc(c.name)}</div><div class="track">${grid}
      <div class="bar" style="--c:${spEsc(c.color)};left:${pos(span.start)}%;width:${pos(span.end) - pos(span.start)}%">${spFmt(span.start)}–${spFmt(span.end)}</div></div></div>`).join("");
    const first = rows.reduce((a, b) => (b.span.start < a.span.start ? b : a));
    const last = rows.reduce((a, b) => (b.span.end > a.span.end ? b : a));
    const byEnd = rows.slice().sort((a, b) => a.span.end - b.span.end);
    const from = Math.max(...rows.map((r) => r.span.start));
    const until = Math.min(...rows.map((r) => r.span.end));
    const facts = [
      [t.earliest, spFmt(first.span.start), first.c.name],
      [t.latest, spFmt(last.span.end), last.c.name],
      from < until ? [t.together, `${spFmt(from)}–${spFmt(until)}`, ""] : null,
      [t.gap, `${byEnd[byEnd.length - 1].span.end - byEnd[0].span.end} ${t.min}`, `${byEnd[0].c.name} → ${byEnd[byEnd.length - 1].c.name}`],
    ].filter(Boolean).map(([l, v, s]) => `<div class="fact"><span>${l}</span><b>${v}</b><span>${spEsc(s)}</span></div>`).join("");
    return `${this._dayNav()}<div class="axis">${axis}</div>${lines}<div class="facts">${facts}</div>`;
  }

  _mapsUrl(school) {
    if (!school) return null;
    const zone = school.zone && this._hass?.states?.[school.zone];
    if (zone?.attributes?.latitude != null) return `https://www.google.com/maps/dir/?api=1&destination=${zone.attributes.latitude},${zone.attributes.longitude}`;
    if (school.address) return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(school.address)}`;
    return null;
  }

  _renderPickup() {
    const t = this._t;
    const today = spSameDay(this._date, new Date());
    const nowM = this._nowMin();
    const rows = this._selected().filter((c) => (c.homeward || "pickup") === "pickup").map((c) => ({ c, span: this._span(c, this._date) })).filter((r) => r.span).sort((a, b) => a.span.end - b.span.end);
    if (!rows.length) return `${this._dayNav()}<div class="empty">${t.noPickup}</div>`;
    const items = rows.map(({ c, span }) => {
      const school = this._school(c);
      const url = this._mapsUrl(school);
      const left = span.end - nowM;
      const rest = !today ? "" : left > 0 ? t.inMin.replace("{n}", left) : t.over;
      return `<div class="pick" style="--c:${spEsc(c.color)}"><div class="time">${spFmt(span.end)}</div>
        <div><div class="who">${spEsc(c.name)}</div><div class="where">${[school?.name, school?.address].filter(Boolean).map(spEsc).join(" · ")}</div>
        ${rest ? `<div class="rest">${rest}</div>` : ""}</div>
        ${url ? `<a class="btn" target="_blank" rel="noopener" href="${spEsc(url)}">${t.navigate}</a>` : "<span></span>"}</div>`;
    }).join("");
    const facts = rows.length > 1
      ? `<div class="facts"><div class="fact"><span>${t.firstPickup}</span><b>${spFmt(rows[0].span.end)}</b><span>${spEsc(rows[0].c.name)}</span></div>
         <div class="fact"><span>${t.lastPickup}</span><b>${spFmt(rows[rows.length - 1].span.end)}</b><span>${spEsc(rows[rows.length - 1].c.name)}</span></div></div>` : "";
    return `${this._dayNav()}${items}${facts}`;
  }

  // ------------------------------------------------------------------ edit
  _renderEdit() {
    const t = this._t;
    const ed = this._edit;
    const tabs = ["children", "schools", "design"].map((k) => `<button class="chip ${ed.tab === k ? "active" : ""}" data-act="etab" data-id="${k}">${t[k]}</button>`).join("");
    const err = ed.error ? `<div class="notice" style="color:#e5484d">${spEsc(ed.error)}</div>` : "";
    let inner;
    if (ed.draft) inner = ed.draft.kind === "child" ? this._childForm(ed.draft) : this._schoolForm(ed.draft);
    else if (ed.tab === "children") {
      inner = this._children.map((c) => `<div class="list-item"><span class="chip" style="--c:${spEsc(c.color)}"><span class="dot"></span></span><div class="grow">${spEsc(c.name)}<div class="sub">${spEsc(this._school(c)?.name || "")}</div></div>
        <button class="btn" data-act="edit-child" data-id="${spEsc(c.id)}">${t.edit}</button></div>`).join("")
        + `<p><button class="btn primary" data-act="new-child">${t.newChild}</button></p>`;
    } else if (ed.tab === "schools") {
      inner = Object.entries(this._data.schools).map(([id, s]) => `<div class="list-item"><div class="grow">${spEsc(s.name)}<div class="sub">${spEsc(s.address)}</div></div>
        <button class="btn" data-act="edit-school" data-id="${spEsc(id)}">${t.edit}</button></div>`).join("")
        + `<p><button class="btn primary" data-act="new-school">${t.newSchool}</button></p>`;
    } else {
      const s = this._data.settings;
      inner = `<div class="form"><label>${t.theme}<select data-f="theme">${["clear", "vivid", "night"].map((k) => `<option value="${k}" ${s.theme === k ? "selected" : ""}>${t.themes[k]}</option>`).join("")}</select></label>
        <label>${t.accent}<input type="color" data-f="accent" value="${spEsc(s.accent || "#4c8df6")}"></label>
        <label>${t.pickupLabel}<input data-f="pickup_label" maxlength="30" value="${spEsc(s.pickup_label || t.pickup)}"></label></div>`;
    }
    return `<div class="row" style="margin-bottom:12px">${ed.draft ? "" : tabs}</div>${inner}${err}<div class="notice">${t.adminOnly}</div>`;
  }

  _childForm(d) {
    const t = this._t;
    const schools = Object.entries(this._data.schools).map(([id, s]) => `<option value="${spEsc(id)}" ${d.school_id === id ? "selected" : ""}>${spEsc(s.name)}</option>`).join("");
    const days = t.daysShort.map((n, i) => `<button class="chip ${d.day === i ? "active" : ""}" data-act="eday" data-id="${i}">${n}${(d.timetable[String(i)] || []).length ? " •" : ""}</button>`).join("");
    const rows = this._lessonRows(d.timetable[String(d.day)] || [], "data-l");
    const homeward = ["pickup", "bus", "alone"].map((k) => `<option value="${k}" ${(d.homeward || "pickup") === k ? "selected" : ""}>${spEsc(t.homewardOpts[k])}</option>`).join("");
    return `<div class="form">
      <label>${t.name}<input data-f="name" value="${spEsc(d.name)}"></label>
      <label>${t.color}<input type="color" data-f="color" value="${spEsc(d.color)}"></label>
      <label>${t.school}<select data-f="school_id"><option value="">${t.noSchool}</option>${schools}</select></label>
      <label>${t.homeward}<select data-f="homeward">${homeward}</select></label>
      <label>${t.holidayEntity}<input data-f="holiday_entity" placeholder="calendar.schulferien" value="${spEsc(d.holiday_entity || "")}"></label>
      <div class="row">${days}</div>${rows}
      <div><button class="btn" data-act="add-lesson">${t.addLesson}</button></div>
      <div class="row"><button class="btn primary" data-act="save-child">${t.save}</button><button class="btn" data-act="cancel">${t.cancel}</button>
      ${d.id ? `<button class="btn danger" data-act="del-child">${t.del}</button>` : ""}</div></div>`;
  }

  _dayForm(d) {
    const t = this._t;
    const date = new Date(`${d.date}T12:00:00`);
    const label = `${t.daysShort[spWeekday(date)]}, ${date.toLocaleDateString(this._hass?.language || "en", { day: "numeric", month: "short" })}`;
    const rows = d.off && d.scope === "day" ? "" : this._lessonRows(d.lessons, "data-dl");
    return `<div class="form">
      <h3 style="margin:0">${spEsc(d.name)} · ${spEsc(label)}</h3>
      <div class="scope"><span class="notice" style="margin:0">${t.scope}</span>
        <label><input type="radio" name="scope" data-f="scope" value="day" ${d.scope === "day" ? "checked" : ""}>${spEsc(t.scopeDay.replace("{date}", label))}</label>
        <label><input type="radio" name="scope" data-f="scope" value="standard" ${d.scope === "standard" ? "checked" : ""}>${spEsc(t.scopeStandard.replace("{day}", t.daysLong[spWeekday(date)]))}</label></div>
      ${d.scope === "day" ? `<label style="display:flex;gap:8px;align-items:center;color:var(--sp-text)"><input type="checkbox" data-f="off" ${d.off ? "checked" : ""}>${t.offDay}</label>` : ""}
      ${rows}
      ${d.off && d.scope === "day" ? "" : `<div><button class="btn" data-act="add-lesson">${t.addLesson}</button></div>`}
      <div class="notice" style="margin:0">${t.dayHint}</div>
      ${d.error ? `<div class="notice" style="color:#e5484d">${spEsc(d.error)}</div>` : ""}
      <div class="row"><button class="btn primary" data-act="save-day">${t.save}</button><button class="btn" data-act="cancel">${t.cancel}</button>
      ${d.hadOverride ? `<button class="btn danger" data-act="revert-day">${t.revert}</button>` : ""}</div></div>`;
  }

  _openDay(childId) {
    const child = this._children.find((c) => c.id === childId);
    const o = this._override(child, this._date);
    this._edit.draft = {
      kind: "day", id: childId, name: child.name, date: spYmd(this._date), scope: "day", off: !!o?.off, hadOverride: !!o, error: null,
      lessons: JSON.parse(JSON.stringify(this._lessons(child, this._date))),
    };
  }

  _reloadDayLessons(d) {
    const child = this._children.find((c) => c.id === d.id);
    const date = new Date(`${d.date}T12:00:00`);
    d.lessons = JSON.parse(JSON.stringify(d.scope === "day" ? this._lessons(child, date) : this._standard(child, date)));
    d.off = d.scope === "day" ? !!this._override(child, date)?.off : false;
  }

  _schoolForm(d) {
    const t = this._t;
    return `<div class="form"><label>${t.name}<input data-f="name" value="${spEsc(d.name)}"></label>
      <label>${t.address}<input data-f="address" value="${spEsc(d.address || "")}"></label>
      <label>${t.zone}<input data-f="zone" placeholder="zone.school" value="${spEsc(d.zone || "")}"></label>
      <div class="row"><button class="btn primary" data-act="save-school">${t.save}</button><button class="btn" data-act="cancel">${t.cancel}</button>
      ${d.id ? `<button class="btn danger" data-act="del-school">${t.del}</button>` : ""}</div></div>`;
  }

  // ---------------------------------------------------------------- events
  _onInput(e) {
    const el = e.target;
    const d = this._edit.draft;
    if (["theme", "accent", "pickup_label"].includes(el.dataset.f)) {
      if (e.type === "change" && (el.dataset.f !== "pickup_label" || el.value.trim())) this._ws({ type: "school_planner/save_settings", [el.dataset.f]: el.value.trim() });
      return;
    }
    if (!d) return;
    if (d.kind === "day") {
      if (el.dataset.dl !== undefined) d.lessons[Number(el.dataset.dl)][el.dataset.lf] = el.value;
      else if (el.dataset.f === "scope" && e.type === "change") { d.scope = el.value; this._reloadDayLessons(d); this._render(); }
      else if (el.dataset.f === "off" && e.type === "change") { d.off = el.checked; this._render(); }
      return;
    }
    if (el.dataset.f) d[el.dataset.f] = el.value;
    if (el.dataset.l !== undefined) d.timetable[String(d.day)][Number(el.dataset.l)][el.dataset.lf] = el.value;
  }

  async _ws(msg) {
    try {
      this._edit.error = null;
      return { result: await this._hass.callWS(msg) };
    } catch (err) {
      this._edit.error = err?.message || String(err);
      this._render();
      return null;
    }
  }

  async _onClick(e) {
    const btn = e.target.closest("[data-act]");
    if (!btn) return;
    const id = btn.dataset.id;
    const ed = this._edit;
    const d = ed.draft;
    switch (btn.dataset.act) {
      case "sel": this._sel = id; break;
      case "view": this._view = id; ed.draft = null; break;
      case "day": this._date = id === "0" ? new Date() : new Date(this._date.getTime() + Number(id) * 86400000); break;
      case "etab": ed.tab = id; break;
      case "edit-day": this._openDay(id); break;
      case "save-day": {
        const lessons = d.lessons.filter((l) => l.subject.trim()).map((l) => ({ ...l, subject: l.subject.trim() }));
        let msg;
        if (d.scope === "day") msg = { type: "school_planner/save_override", child_id: d.id, date: d.date, off: d.off, lessons: d.off ? [] : lessons };
        else {
          const child = this._children.find((c) => c.id === d.id);
          const wd = String(spWeekday(new Date(`${d.date}T12:00:00`)));
          msg = { type: "school_planner/save_child", child_id: d.id, name: child.name, timetable: { ...child.timetable, [wd]: lessons } };
        }
        if (await this._ws(msg)) { ed.draft = null; await this._load(); return; }
        d.error = ed.error; this._render(); return;
      }
      case "revert-day":
        if (await this._ws({ type: "school_planner/clear_override", child_id: d.id, date: d.date })) { ed.draft = null; await this._load(); return; }
        d.error = ed.error; this._render(); return;
      case "new-child": ed.draft = { kind: "child", id: null, name: "", color: SP_PALETTE[this._children.length % SP_PALETTE.length], school_id: "", holiday_entity: "", homeward: "pickup", timetable: {}, day: 0 }; break;
      case "edit-child": {
        const c = this._children.find((x) => x.id === id);
        ed.draft = { kind: "child", ...JSON.parse(JSON.stringify(c)), id, school_id: c.school_id || "", holiday_entity: c.holiday_entity || "", homeward: c.homeward || "pickup", day: 0 };
        break;
      }
      case "new-school": ed.draft = { kind: "school", id: null, name: "", address: "", zone: "" }; break;
      case "edit-school": ed.draft = { kind: "school", id, ...this._data.schools[id] }; break;
      case "cancel": ed.draft = null; break;
      case "eday": d.day = Number(id); break;
      case "add-lesson": {
        const list = d.kind === "day" ? d.lessons : (d.timetable[String(d.day)] ||= []);
        const prev = list[list.length - 1];
        const start = prev ? prev.end : "08:00";
        const end = spFmt(Math.min(spMin(start) + 45, 23 * 60 + 59));
        list.push({ start, end, subject: "", room: "", teacher: "" });
        break;
      }
      case "del-lesson": (d.kind === "day" ? d.lessons : d.timetable[String(d.day)]).splice(Number(id), 1); break;
      case "save-child": {
        const timetable = {};
        for (const [k, ls] of Object.entries(d.timetable)) timetable[k] = ls.filter((l) => l.subject.trim()).map((l) => ({ ...l, subject: l.subject.trim() }));
        const msg = { type: "school_planner/save_child", name: d.name.trim(), color: d.color, school_id: d.school_id || null, holiday_entity: d.holiday_entity || null, homeward: d.homeward || "pickup", timetable };
        if (d.id) msg.child_id = d.id;
        if (await this._ws(msg)) { ed.draft = null; await this._load(); return; }
        return;
      }
      case "del-child":
        if (confirm(this._t.confirmDelete) && (await this._ws({ type: "school_planner/delete_child", child_id: d.id }))) {
          ed.draft = null; this._sel = "all"; await this._load(); return;
        }
        return;
      case "save-school": {
        const msg = { type: "school_planner/save_school", name: d.name.trim(), address: d.address || "", zone: d.zone || null };
        if (d.id) msg.school_id = d.id;
        if (await this._ws(msg)) { ed.draft = null; await this._load(); return; }
        return;
      }
      case "del-school":
        if (confirm(this._t.confirmDelete) && (await this._ws({ type: "school_planner/delete_school", school_id: d.id }))) {
          ed.draft = null; await this._load(); return;
        }
        return;
    }
    this._render();
  }
}

class SchoolPlannerCardEditor extends HTMLElement {
  setConfig(config) { this._config = config; this._render(); }
  set hass(hass) { this._hass = hass; if (this._form) this._form.hass = hass; }
  _render() {
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (ev) => {
        this._config = ev.detail.value;
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config }, bubbles: true, composed: true }));
      });
      this.appendChild(this._form);
    }
    const t = SP_I18N[(this._hass?.language || "en").slice(0, 2)] || SP_I18N.en;
    this._form.hass = this._hass;
    this._form.data = this._config;
    this._form.computeLabel = (s) => ({ title: t.name, view: t.day, theme: t.theme }[s.name] || s.name);
    this._form.schema = [
      { name: "title", selector: { text: {} } },
      { name: "view", selector: { select: { options: ["day", "week", "compare", "pickup", "edit"].map((v) => ({ value: v, label: t[v] })) } } },
      { name: "theme", selector: { select: { options: [{ value: "", label: "—" }].concat(["clear", "vivid", "night"].map((v) => ({ value: v, label: t.themes[v] }))) } } },
    ];
  }
}

customElements.define("school-planner-card", SchoolPlannerCard);
customElements.define("school-planner-card-editor", SchoolPlannerCardEditor);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "school-planner-card",
  name: "School Planner",
  description: "Timetables, comparison and pickup times for several children.",
  preview: false,
});
console.info(`%c SCHOOL-PLANNER-CARD %c v${SP_VERSION} `, "background:#4C8DF6;color:#fff", "");
