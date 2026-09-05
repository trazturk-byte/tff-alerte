"""Verification adversariale : est-ce que le bot detectera VRAIMENT le jour J ?

On ne teste pas des chaines inventees, mais le contenu reel des pages TFF.
"""
import check

print("=" * 70)
print("TEST 1 — La page d'actus TFF contient-elle les titres en HTML brut ?")
print("=" * 70)
texte = check.recuperer(check.URLS["tff_news"])
print(f"Longueur recuperee : {len(texte)} caracteres")
n = check.normaliser(texte)
# Des mots qui doivent apparaitre si les titres sont bien dans le HTML
for mot in ["milli", "takim", "haber", "kadro", "mac"]:
    print(f"  contient '{mot}' : {mot in n}")
print("\nExtrait (600 premiers caracteres apres le menu) :")
print("  " + texte[1500:2100].replace("\n", " "))

print()
print("=" * 70)
print("TEST 2 — Le detecteur reagit-il a une VRAIE annonce TFF passee ?")
print("=" * 70)
# Page reelle de l'annonce Turkiye-Gurcistan (meme stade que le match vise)
reelle = check.recuperer("https://www.tff.org/default.aspx?pageID=202&ftxtID=48608")
print(f"Page recuperee : {len(reelle)} caracteres")
titre = [l for l in reelle.split(". ") if "Gurcistan" in check.normaliser(l)][:1]
print(f"Titre trouve : {titre}")
# On remplace Gurcistan par Fransa : c'est exactement ce que la TFF publiera
simule = reelle.replace("Gürcistan", "Fransa").replace("GÜRCİSTAN", "FRANSA")
r = check.detecter_tff(simule)
print(f"\n>>> DETECTION : {'OUI' if r else 'NON'}")
for x in r:
    print(f"    {x[:200]}")

print()
print("=" * 70)
print("TEST 3 — Toutes les formulations possibles du titre")
print("=" * 70)
FORMULATIONS = [
    "Türkiye - Fransa Maçının Öncelikli Bilet Satışı Başladı",
    "Türkiye - Fransa Maçının Genel Bilet Satışları Başladı",
    "Türkiye - Fransa Maçının Bilet Satışı Başladı",
    "Türkiye-Fransa Maçının Öncelikli Bilet Satışları Başladı",
    "Türkiye - Fransa Maçı Biletleri Satışa Çıktı",
    "A Milli Takımımızın Fransa Maçının Bilet Satışı Başladı",
    "Türkiye - Fransa Maçının Misafir Tribün Biletleri Satışa Sunulacak",
    "Fransa Maçı Bilet Satışı Hakkında Bilgilendirme",
]
for f in FORMULATIONS:
    ok = bool(check.detecter_tff(f))
    print(f"  [{'OK ' if ok else 'RATE'}] {f}")

print()
print("=" * 70)
print("TEST 4 — La sentinelle du fan-club est-elle toujours la ?")
print("=" * 70)
fan = check.recuperer(check.URLS["fanclub"])
present = check.SENTINELLE in check.normaliser(fan)
print(f"  Sentinelle presente : {present}")
print(f"  -> {'OK, la vente n est pas ouverte' if present else 'ALERTE : sentinelle absente !'}")
print(f"  Le match Fransa est-il liste : {'fransa' in check.normaliser(fan)}")
