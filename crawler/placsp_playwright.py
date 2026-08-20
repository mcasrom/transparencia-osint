#!/usr/bin/env python3
"""Crawl PLACSP con Playwright: buscar contratos de un organo de Murcia."""
import sys
import time
from playwright.sync_api import sync_playwright

QUERY = sys.argv[1] if len(sys.argv) > 1 else "Ayuntamiento de Murcia"
URL = "https://contrataciondelestado.es/wps/portal/plataforma/portalContratacion/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36", locale="es-ES")
    page = ctx.new_page()
    page.goto(URL, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # localizar el campo de texto de busqueda (por atributo name con textTexto1)
    field = page.locator("input[name*='textTexto1']").first
    n = field.count()
    print("campos textTexto1:", n)
    field.fill(QUERY)
    print("rellenado:", QUERY)

    # buscar el boton Buscar: dojo, por texto o por atributos
    btns = page.locator("button, input[type=button], input[type=submit], [role=button]")
    found = None
    for i in range(btns.count()):
        try:
            txt = btns.nth(i).inner_text().strip() or btns.nth(i).get_attribute("value") or ""
            if "buscar" in txt.lower() or "busqueda" in txt.lower():
                found = btns.nth(i)
                print("boton encontrado:", txt[:30])
                break
        except Exception:
            continue
    if found:
        found.click()
    else:
        print("boton 'Buscar' no encontrado por texto; intento Enter en el campo")
        field.press("Enter")

    page.wait_for_timeout(6000)

    # capturar resultados
    html = page.content()
    open("/tmp/placsp_results.html", "w", encoding="utf-8").write(html)
    print("pagina capturada:", len(html), "bytes")

    # intentar extraer filas de resultados
    rows = page.locator("table tbody tr, .tabla tr, [class*=result] tr")
    print("filas detectadas:", rows.count())
    for i in range(min(rows.count(), 5)):
        try:
            print(" -", rows.nth(i).inner_text()[:120].replace("\n", " | "))
        except Exception:
            pass

    browser.close()
