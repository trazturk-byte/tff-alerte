"""Verifie que les detecteurs se declenchent bien sur de vraies annonces."""
import check

CAS = [
    ("TFF - annonce prevente", check.detecter_tff,
     "Türkiye - Fransa Maçının Öncelikli Bilet Satışı Başladı", True),
    ("TFF - annonce generale", check.detecter_tff,
     "Türkiye - Fransa Maçının Genel Bilet Satışları Başladı", True),
    ("TFF - actu sans rapport", check.detecter_tff,
     "Türkiye - Fransa maçı Kocaeli'de oynanacak", False),
    ("Fanclub - vente ouverte", check.detecter_fanclub,
     "UEFA ULUSLAR LIGI TÜRKİYE FRANSA Satın Al", True),
    ("Fanclub - rien en vente", check.detecter_fanclub,
     "TÜRKİYE FRANSA Bilet satışı yapılan maç bulunmamaktadır", False),
    ("News - article 2026", check.detecter_gnews,
     "<item><title>Türkiye Fransa maçı biletleri satışa çıktı</title>"
     "<pubDate>Mon, 14 Sep 2026 09:00:00 GMT</pubDate></item>", True),
    ("News - vieil article 2019", check.detecter_gnews,
     "<item><title>Türkiye Fransa maçı biletleri satışa çıktı</title>"
     "<pubDate>Mon, 03 Jun 2019 09:00:00 GMT</pubDate></item>", False),
    ("News - simple annonce de match", check.detecter_gnews,
     "<item><title>Türkiye Fransa maçı ne zaman?</title>"
     "<pubDate>Mon, 14 Sep 2026 09:00:00 GMT</pubDate></item>", False),
]

ok = True
for nom, fn, entree, attendu in CAS:
    obtenu = bool(fn(entree))
    marque = "OK " if obtenu == attendu else "ECHEC"
    if obtenu != attendu:
        ok = False
    print(f"[{marque}] {nom:32} -> alerte={obtenu} (attendu {attendu})")

print("\nTOUS LES TESTS PASSENT" if ok else "\n!!! DES TESTS ECHOUENT")
