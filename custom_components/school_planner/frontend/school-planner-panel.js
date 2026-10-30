/* School Planner sidebar panel: hosts the card full page so the integration can be
   set up and used without adding a card to a dashboard first. */
class SchoolPlannerPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (this._card) this._card.hass = hass;
    if (this._menu) this._menu.hass = hass;
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (this._menu) this._menu.narrow = narrow;
  }

  set panel(panel) { this._panel = panel; }

  connectedCallback() {
    if (this._ready) return;
    this._ready = true;
    this.style.cssText = "display:block;box-sizing:border-box;min-height:100%;background:var(--primary-background-color);";
    this.innerHTML = `<div style="display:flex;align-items:center;gap:4px;height:56px;padding:0 8px;background:var(--app-header-background-color, var(--primary-color));color:var(--app-header-text-color, #fff)">
      <ha-menu-button></ha-menu-button><span style="font-size:1.25rem;font-weight:500">School Planner</span></div>
      <div class="sp-body" style="max-width:1100px;margin:0 auto;padding:16px;box-sizing:border-box"></div>`;
    this._menu = this.querySelector("ha-menu-button");
    if (this._menu) { this._menu.hass = this._hass; this._menu.narrow = this._narrow; }
    customElements.whenDefined("school-planner-card").then(() => {
      const card = document.createElement("school-planner-card");
      card.setConfig({ type: "custom:school-planner-card", view: "day" });
      if (this._hass) card.hass = this._hass;
      this._card = card;
      this.querySelector(".sp-body").appendChild(card);
    });
  }
}

customElements.define("school-planner-panel", SchoolPlannerPanel);
