"""Verifie que les detecteurs se declenchent bien sur de vraies annonces."""
import check

CAS = [
    ("TFF - annonce prevente", check.detecter_tff,
     "Türkiye - Fransa Maçının Öncelikli Bilet Satışı Başladı", True),
    ("TFF - annonce generale", check.detecter_tff,
     "Türkiye - Fransa Maçının Genel Bilet Satışları Başladı", True),
    ("TFF - actu sans rapport", check.detecter_tff,
     "Türkiye - Fransa maçı Kocaeli'de oynanacak", False),
    # Formulations reelles vues chez la TFF, ratees par la premiere version.
    ("TFF - biletleri satisa cikti", check.detecter_tff,
     "Türkiye - Fransa Maçı Biletleri Satışa Çıktı", True),
    ("TFF - misafir tribun", check.detecter_tff,
     "Türkiye - Fransa Maçının Misafir Tribün Biletleri Satışa Sunulacak", True),
    # L'encodage windows-1254 de la TFF doit etre respecte, sinon les mots
    # turcs sont detruits et plus rien n'est detecte.
    ("Encodage windows-1254", check.detecter_tff,
     check.decoder(
         "Türkiye - Fransa Maçının Bilet Satışı Başladı".encode("windows-1254"),
         {"Content-Type": "text/html; charset=windows-1254"},
     ), True),
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
