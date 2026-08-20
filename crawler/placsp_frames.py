#!/usr/bin/env python3
"""Localizar el campo textTexto1 en los frames del PLACSP."""
from playwright.sync_api import sync_playwright

URL = "https://contrataciondelestado.es/wps/portal/plataforma/portalContratacion/"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0", locale="es-ES")
    pg = ctx.new_page()
    pg.goto(URL, timeout=60000, wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)
    for f in pg.frames:
        n = f.locator("input").count()
        tt = f.locator("input[name*='textTexto1']").count()
        print(f"frame: {f.name or '(unnamed)'} | url:{f.url[:60]} | inputs:{n} | textTexto1:{tt}")
        if tt:
            f.screenshot(path="/tmp/frame_tt.png")
            print("  -> campo encontrado; screenshot /tmp/frame_tt.png")
    b.close()
