import re
import urllib.request
import http.cookiejar
import urllib.parse

BASE = "https://contrataciondelestado.es"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    return opener.open(req, timeout=40).read().decode("utf-8", "ignore")


def post(url, data, headers=None):
    h = {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data.encode(), headers=h)
    return opener.open(req, timeout=60).read().decode("utf-8", "ignore")


def main():
    portal = BASE + "/wps/portal/plataforma/portalContratacion/"
    s = get(portal)
    # form action + viewstate + text field name
    fa = re.search(r'<form[^>]*action="([^"]+)"', s)
    vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]*)"', s)
    txtfield = re.findall(r'name="([^"]*textTexto1)"', s)
    if not fa or not vs:
        print("ERR: no form/viewstate"); return
    action = urllib.parse.urljoin(BASE, fa.group(1))
    viewstate = vs.group(1)
    field = txtfield[0] if txtfield else "viewns_Z7_BS88AB1A0GSM10A6E3652010S2_:form1:tableEx1:0:textTexto1"
    print("action:", action[:90])
    print("viewstate:", viewstate[:40], "...")
    print("textfield:", field)

    query = "Murcia"
    data = {
        "javax.faces.ViewState": viewstate,
        field: query,
    }
    # submit del form
    submit_name = "viewns_Z7_BS88AB1A0GSM10A6E3652010S2_:form1_SUBMIT"
    data[submit_name] = "1"
    data["javax.faces.encodedURL"] = action
    print("==> POST buscando:", query)
    r = post(action, urllib.parse.urlencode(data))
    print("respuesta:", len(r), "bytes")
    # contar resultados / contratos en la respuesta
    m = re.findall(r"contrato[^<]{0,60}|licitaci[^<]{0,60}|n. resultados[^<]{0,40}|resultados[^<]{0,40}", r, re.I)
    print("menciones:", m[:6] if m else "ninguna")
    # buscar tablas de resultados
    rows = re.findall(r"<tr[^>]*>", r)
    print("filas <tr>:", len(rows))


if __name__ == "__main__":
    main()
