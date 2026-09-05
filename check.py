#!/usr/bin/env python3
"""
Surveille l'ouverture de la billetterie Türkiye - Fransa
(UEFA Nations League, 25 septembre 2026, TURKA Kocaeli Stadyumu).

Envoie une alerte Discord avec @everyone des qu'un signal est detecte.
Tourne sur GitHub Actions toutes les 5 minutes. Aucune dependance externe.

Chaque source a son propre detecteur, pour eviter les faux positifs :
le mot "Fransa" seul ne suffit pas, le match est deja affiche partout.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape

WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "").strip()

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Tant qu'aucun match n'est en vente, la page du fan-club contient cette phrase.
# Sa disparition = une billetterie vient d'ouvrir.
SENTINELLE = "bilet satisi yapilan mac bulunmamaktadir"

URLS = {
    "tff_news": "https://www.tff.org/default.aspx?pageID=202",
    "tff_bilet": "https://www.tff.org/default.aspx?pageId=1091",
    "fanclub": "https://taraftarkulubu.tff.org/maclar.aspx",
    "gnews": (
        "https://news.google.com/rss/search?"
        "q=T%C3%BCrkiye+Fransa+bilet+sat%C4%B1%C5%9F%C4%B1&hl=tr&gl=TR&ceid=TR:tr"
    ),
}

LIBELLES = {
    "tff_news": "TFF — actualités A Milli Takım",
    "tff_bilet": "TFF — page billetterie",
    "fanclub": "Fan-club — matchs en vente",
    "gnews": "Presse turque (Google News)",
}


def normaliser(texte):
    """Minuscules + suppression des diacritiques turcs."""
    table = str.maketrans("ıİşŞğĞçÇöÖüÜâÂîÎûÛ", "iisSgGcCoOuUaAiIuU")
    return texte.translate(table).lower()


def recuperer(url, brut=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "tr,en"})
    with urllib.request.urlopen(req, timeout=25) as rep:
        data = rep.read().decode("utf-8", errors="replace")
    if brut:
        return data
    data = re.sub(r"<script.*?</script>", " ", data, flags=re.S | re.I)
    data = re.sub(r"<style.*?</style>", " ", data, flags=re.S | re.I)
    data = re.sub(r"<[^>]+>", " ", data)
    return re.sub(r"\s+", " ", unescape(data)).strip()


def detecter_tff(texte):
    """Sur les pages TFF : un titre annoncant une vente pour le match contre la France."""
    n = normaliser(texte)
    raisons = []

    # "Turkiye - Fransa Macinin (Oncelikli) Bilet Satisi Basladi"
    for m in re.finditer(r"fransa.{0,90}?bilet\s*sat[iı]s|bilet\s*sat[iı]s.{0,90}?fransa", n):
        fenetre = n[m.start() : m.end() + 60]
        # La phrase "aucun match en vente" contient les memes mots : on l'ecarte.
        if SENTINELLE in fenetre:
            continue
        raisons.append("Annonce de vente détectée : ..." + texte[m.start() : m.end() + 60].strip() + "...")
        break

    return raisons


def detecter_fanclub(texte):
    """La page du fan-club ne dit plus 'aucun match en vente' -> une vente a ouvert."""
    if SENTINELLE not in normaliser(texte):
        return ["La page n'affiche plus « aucun match en vente ». Une billetterie vient d'ouvrir."]
    return []


def detecter_gnews(xml):
    """Articles de presse recents annoncant l'ouverture. On ignore le titre du flux."""
    raisons = []
    limite = datetime.now(timezone.utc) - timedelta(days=10)

    for bloc in re.findall(r"<item>(.*?)</item>", xml, flags=re.S):
        titre_m = re.search(r"<title>(.*?)</title>", bloc, flags=re.S)
        if not titre_m:
            continue
        titre = unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", titre_m.group(1))).strip()
        n = normaliser(titre)

        if "fransa" not in n:
            continue
        # Il faut un verbe d'ouverture, pas juste le mot "bilet".
        if not re.search(r"sat[iı]sa\s*c[iı]kt|sat[iı]s[iı]\s*basla|basladi|sat[iı]sta", n):
            continue

        date_m = re.search(r"<pubDate>(.*?)</pubDate>", bloc)
        if date_m:
            try:
                if parsedate_to_datetime(date_m.group(1).strip()) < limite:
                    continue  # article ancien (il existe un Turquie-France de 2019)
            except (TypeError, ValueError):
                pass

        raisons.append(f"Article récent : « {titre} »")
        if len(raisons) >= 3:
            break

    return raisons


DETECTEURS = {
    "tff_news": detecter_tff,
    "tff_bilet": detecter_tff,
    "fanclub": detecter_fanclub,
    "gnews": detecter_gnews,
}


def alerter(trouvailles):
    lignes = [
        "@everyone",
        "",
        "# 🚨 BILLETTERIE TÜRKİYE–FRANSA",
        "",
        "**Un signal vient d'être détecté. Vérifie MAINTENANT.**",
        "",
    ]
    for cle, raisons in trouvailles.items():
        lignes.append(f"**{LIBELLES[cle]}**")
        for r in raisons:
            lignes.append(f"> {r[:500]}")
        lignes.append(f"<{URLS[cle]}>")
        lignes.append("")

    lignes += [
        "---",
        "**À FAIRE, DANS L'ORDRE :**",
        "1. Ouvrir **passo.com.tr** — compte de ta mère (Kırmızı)",
        "2. Tribune **BATI ALT ORTA**, rang le plus bas",
        "3. **3 billets** — saisir les 3 pièces d'identité",
        "",
        "⏳ La prévente Kırmızı ne dure que **24 heures**.",
    ]

    corps = json.dumps({"content": "\n".join(lignes)[:1900]}).encode()
    req = urllib.request.Request(
        WEBHOOK,
        data=corps,
        headers={"Content-Type": "application/json", "User-Agent": UA},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as rep:
        print(f"Discord : HTTP {rep.status}")


def main():
    test = "--test" in sys.argv
    if not WEBHOOK and not test:
        print("ERREUR : le secret DISCORD_WEBHOOK n'est pas defini.", file=sys.stderr)
        return 1

    trouvailles = {}
    for cle, url in URLS.items():
        try:
            texte = recuperer(url, brut=(cle == "gnews"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            print(f"[ignore] {LIBELLES[cle]} : {e}")
            continue

        if len(texte) < 200:
            print(f"[ignore] {LIBELLES[cle]} : page trop courte, probablement bloquee")
            continue

        raisons = DETECTEURS[cle](texte)
        if raisons:
            print(f"[SIGNAL] {LIBELLES[cle]} : {raisons}")
            trouvailles[cle] = raisons
        else:
            print(f"[rien]   {LIBELLES[cle]}")

    if trouvailles and not test:
        alerter(trouvailles)
        print(">>> ALERTE ENVOYEE")
    elif trouvailles:
        print(">>> (mode test) alerte NON envoyee")
    else:
        print(">>> Rien a signaler.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
