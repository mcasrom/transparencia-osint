#!/usr/bin/env python3
"""Diagnostico: por que Playwright no ve el campo textTexto1 en el PLACSP."""
from playwright.sync_api import sync_playwright

URL = "https://contrataciondelestado.es/wps/portal/plataforma/portalContratacion/"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0", locale="es-ES")
    pg = ctx.new_page()
    pg.goto(URL, timeout=60000, wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)

    print("title:", pg.title())
    print("url final:", pg.url[:120])
    print("iframes:", pg.frames if False else len(pg.frames))
    # inputs visibles
    ins = pg.locator("input")
    print("inputs totales:", ins.count())
    for i in range(min(ins.count(), 12)):
        try:
            nm = ins.nth(i).get_attribute("name") or ""
            ty = ins.nth(i).get_attribute("type") or ""
            if "text" in ty.lower() or "texttexto" in nm.lower():
                print("  input:", nm[:70], "| type:", ty)
        except Exception:
            pass
    # cookies / banners
    for sel in ["#onetrust-banner-container", "[class*=cookie]", "[id*=cookie]", "button:has-text(\"Aceptar\")", "button:has-text(\"Acepto\")"]:
        el = pg.locator(sel)
        if el.count() > 0:
            print("banner/btn:", sel, el.count())
    # texto visible que indique estado
    body = pg.locator("body").inner_text()[:300].replace("\n", " | ")
    print("body[:300]:", body)
    pg.screenshot(path="/tmp/placsp_diag.png")
    print("screenshot: /tmp/placsp_diag.png")
    b.close()
