"""Fabrique le site complet dans site/ (ce que nginx sert) à partir de page.html et de articles/.

    python3 build.py

- site/index.html            : l'accueil en anglais
- site/fr/index.html         : l'accueil en français, écrit EN DUR (un moteur de recherche ne lit
                               pas un texte posé par un bouton)
- site/blog/…, site/fr/blog/… : le blog, un dossier par article
- site/sitemap.xml, robots.txt, 404.html
Un article = un fichier articles/<langue>/<adresse>.html : des lignes « clé: valeur », une ligne vide,
le texte en HTML, puis éventuellement « ---FAQ--- » et des lignes « Q: … » / « R: … ».
"""
import html
import json
import re
import shutil
from pathlib import Path

ICI = Path(__file__).parent
SITE = "https://naylisagency.com"
SORTIE = ICI / "site"
MAIL = "https://formsubmit.co/ajax/kylian.business@icloud.com"
FICHIERS = ("logo.svg", "favicon.ico", "favicon-32x32.png", "apple-touch-icon.png", "icon-512.png")

LANGUES = {
    "en": {
        "racine": "/", "blog": "/blog/", "locale": "en_US",
        "titre": "OnlyFans Agency — OFM Management, 24/7 Chatting, 50/50 Split | Naylis Agency",
        "description": ("Naylis is an OnlyFans agency (OFM): 24/7 chatting, managed socials and traffic "
                        "generated on top of yours, by a dedicated team. 50/50 split. Apply in two minutes."),
        "blog_titre": "OnlyFans Agency Blog — OFM, Management, Chatting, Percentages | Naylis Agency",
        "blog_description": ("Straight answers for creators: what an OnlyFans management agency does, what it "
                             "costs, how to choose one and how to spot a bad one."),
        "blog_h1": "The OnlyFans agency <em>blog.</em>",
        "blog_intro": "Plain answers for creators: what an agency does, what it costs, and how to pick one.",
        "lire": "Read the article", "accueil": "Home", "postuler": "Apply", "agence": "The agency",
        "maj": "Updated", "minutes": "min read", "faq": "Frequently asked questions",
        "suite": "Keep reading", "guides": "Guides",
        "cta_titre": "Want a team that works as hard as you do?",
        "cta_texte": ("24/7 chatting, managed socials, traffic generated on top of yours. "
                      "50/50 split for established creators. The form takes two minutes."),
        "cta_bouton": "Apply to Naylis", "majeurs": "Adults only",
        "introuvable": "This page doesn't exist.", "retour": "Back to the home page",
    },
    "fr": {
        "racine": "/fr/", "blog": "/fr/blog/", "locale": "fr_FR",
        "titre": "Agence OnlyFans — Management, chatting 24h/24, partage 50/50 | Naylis Agency",
        "description": ("Naylis est une agence OnlyFans : chatting 24h/24, réseaux sociaux gérés et trafic généré "
                        "en plus du tien, par une équipe dédiée. Partage 50/50. Candidature en deux minutes."),
        "blog_titre": "Blog agence OnlyFans — management, chatting, pourcentages | Naylis Agency",
        "blog_description": ("Des réponses claires pour les créatrices : à quoi sert une agence OnlyFans, combien "
                             "elle prend, comment en trouver une sérieuse et repérer les arnaques."),
        "blog_h1": "Le blog de l'<em>agence OnlyFans.</em>",
        "blog_intro": ("Des réponses claires pour les créatrices : ce que fait une agence, ce qu'elle coûte, "
                       "et comment bien la choisir."),
        "lire": "Lire l'article", "accueil": "Accueil", "postuler": "Postuler", "agence": "L'agence",
        "maj": "Mis à jour le", "minutes": "min de lecture", "faq": "Questions fréquentes",
        "suite": "À lire aussi", "guides": "Guides",
        "cta_titre": "Tu cherches une équipe qui travaille autant que toi ?",
        "cta_texte": ("Chatting 24h/24, réseaux sociaux gérés, trafic généré en plus du tien. "
                      "Partage 50/50 pour les créatrices déjà lancées. Le formulaire prend deux minutes."),
        "cta_bouton": "Postuler chez Naylis", "majeurs": "Site réservé aux personnes majeures",
        "introuvable": "Cette page n'existe pas.", "retour": "Retour à l'accueil",
    },
}
LANGUES["es"] = {
    "racine": "/es/", "blog": "/es/blog/", "locale": "es_ES",
    "titre": "Agencia OnlyFans — Management, chatting 24/7, reparto 50/50 | Naylis Agency",
    "description": ("Naylis es una agencia de OnlyFans: chatting 24/7, redes sociales gestionadas y tráfico generado "
                    "además del tuyo, con un equipo dedicado. Reparto 50/50. Postula en dos minutos."),
    "blog_titre": "Blog agencia OnlyFans — management, chatting, porcentajes | Naylis Agency",
    "blog_description": ("Respuestas claras para creadoras: qué hace una agencia de OnlyFans, cuánto cobra, "
                         "cómo elegir una seria y cómo detectar las estafas."),
    "blog_h1": "El blog de la <em>agencia OnlyFans.</em>",
    "blog_intro": "Respuestas claras para creadoras: qué hace una agencia, cuánto cuesta y cómo elegirla bien.",
    "lire": "Leer el artículo", "accueil": "Inicio", "postuler": "Postular", "agence": "La agencia",
    "maj": "Actualizado el", "minutes": "min de lectura", "faq": "Preguntas frecuentes",
    "suite": "Sigue leyendo", "guides": "Guías",
    "cta_titre": "¿Buscas un equipo que trabaje tanto como tú?",
    "cta_texte": ("Chatting 24/7, redes sociales gestionadas, tráfico generado además del tuyo. "
                  "Reparto 50/50 para creadoras ya lanzadas. El formulario toma dos minutos."),
    "cta_bouton": "Postular en Naylis", "majeurs": "Sitio reservado a mayores de edad",
    "introuvable": "Esta página no existe.", "retour": "Volver al inicio",
}
MOIS_ES = ("enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre").split()
MOIS_FR = ("janvier février mars avril mai juin juillet août septembre octobre novembre décembre").split()
MOIS_EN = ("January February March April May June July August September October November December").split()


def date_lisible(iso: str, langue: str) -> str:
    a, m, j = (int(x) for x in iso.split("-"))
    if langue == "es":
        return f"{j} de {MOIS_ES[m - 1]} de {a}"
    return f"{j} {MOIS_FR[m - 1]} {a}" if langue == "fr" else f"{MOIS_EN[m - 1]} {j}, {a}"


def texte_nu(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def ld(donnees: dict) -> str:
    return ('<script type="application/ld+json">'
            + json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/") + "</script>\n")


ORGANISATION = {
    "@type": "Organization", "@id": SITE + "/#organisation", "name": "Naylis Agency", "url": SITE + "/",
    "logo": SITE + "/icon-512.png",
    "description": "OnlyFans management agency: 24/7 chatting, managed social accounts and traffic generation.",
}


def tete_commune(titre, description, adresse, langue, autres, genre="website"):
    """Tout ce qu'un moteur de recherche lit avant le texte : titre, description, adresse de
    référence, la même page dans l'autre langue, et l'aperçu des partages."""
    t = [f"<title>{html.escape(titre)}</title>",
         f'<meta name="description" content="{html.escape(description, quote=True)}">',
         f'<link rel="canonical" href="{SITE}{adresse}">']
    for l, a in sorted(autres.items()):
        t.append(f'<link rel="alternate" hreflang="{l}" href="{SITE}{a}">')
    if "en" in autres:
        t.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{autres["en"]}">')
    t += [f'<meta property="og:type" content="{genre}">',
          '<meta property="og:site_name" content="Naylis Agency">',
          f'<meta property="og:title" content="{html.escape(titre, quote=True)}">',
          f'<meta property="og:description" content="{html.escape(description, quote=True)}">',
          f'<meta property="og:url" content="{SITE}{adresse}">',
          f'<meta property="og:image" content="{SITE}/icon-512.png">',
          f'<meta property="og:locale" content="{LANGUES[langue]["locale"]}">',
          '<meta name="twitter:card" content="summary">',
          '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">',
          '<link rel="icon" href="/favicon.ico" sizes="any">',
          '<link rel="icon" type="image/svg+xml" href="/logo.svg">',
          '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
          '<link rel="apple-touch-icon" href="/apple-touch-icon.png">']
    return "\n".join(t) + "\n"


# ------------------------------------------------------------------ les articles
def lire_article(chemin: Path, langue: str) -> dict:
    brut = chemin.read_text(encoding="utf-8")
    entete, reste = brut.split("\n\n", 1)
    a = {"langue": langue, "adresse_courte": chemin.stem}
    for ligne in entete.splitlines():
        cle, valeur = ligne.split(":", 1)
        a[cle.strip()] = valeur.strip()
    corps, _, faq = reste.partition("---FAQ---")
    a["corps"] = corps.strip()
    a["faq"] = []
    question = None
    for ligne in faq.strip().splitlines():
        if ligne.startswith("Q:"):
            question = ligne[2:].strip()
        elif ligne.startswith("R:") and question:
            a["faq"].append((question, ligne[2:].strip()))
            question = None
    a["adresse"] = LANGUES[langue]["blog"] + a["adresse_courte"] + "/"
    # Jamais un « : » seul en début de ligne dans un titre français.
    a["court"] = a.get("court", "").replace(" : ", "\u00a0: ").replace(" ?", "\u00a0?")
    a["minutes"] = max(2, round(len(texte_nu(a["corps"]).split()) / 220))
    for cle in ("titre", "description", "h1", "date", "resume"):
        if not a.get(cle):
            raise SystemExit(f"{chemin} : il manque « {cle} »")
    return a


def marque(langue: str) -> str:
    return (f'<a class="brand" href="{LANGUES[langue]["racine"]}" aria-label="Naylis Agency">'
            '<img src="/logo.svg" width="38" height="38" alt="">'
            '<span class="brand-name"><b>Naylis</b><small>Agency</small></span></a>')


def entete_blog(langue: str, autres: dict | None) -> str:
    """`autres` : langue → adresse de la même page dans les autres langues."""
    L = LANGUES[langue]
    bascule = "".join(f'<a class="lang-lien" href="{a}" hreflang="{l}">{l.upper()}</a>'
                      for l, a in sorted((autres or {}).items()) if l != langue)
    return (f'<header class="top wrap"><div class="bar glass">{marque(langue)}<nav class="nav" aria-label="Main">'
            f'<a href="{L["racine"]}#agency">{L["agence"]}</a><a href="{L["blog"]}">Blog</a>{bascule}'
            f'<a class="btn btn-primary" href="{L["racine"]}#apply">{L["postuler"]}</a></nav></div></header>')


def pied_blog(langue: str, articles: list) -> str:
    L = LANGUES[langue]
    liens = "".join(f'<a href="{a["adresse"]}">{html.escape(a["court"])}</a>' for a in articles)
    return (f'<footer class="wrap"><div class="foot-liens"><b>{L["guides"]}</b>{liens}</div>'
            f'<div class="foot">{marque(langue)}<span>{L["majeurs"]} · © 2026 Naylis Agency</span></div></footer>')


def page(langue, tete, corps, articles, autre=None):
    return ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n%s'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
            '&family=Manrope:wght@400;500;600;700&display=swap">\n'
            '<link rel="stylesheet" href="/blog.css">\n</head>\n<body>\n<div class="aura" aria-hidden="true"></div>\n'
            '<div class="page">\n%s\n<main class="wrap">\n%s\n</main>\n%s\n</div>\n</body>\n</html>\n'
            % (langue, tete, entete_blog(langue, autre), corps, pied_blog(langue, articles)))


def carte(a: dict, L: dict) -> str:
    return (f'<a class="carte glass" href="{a["adresse"]}"><span class="eyebrow">{html.escape(a.get("rubrique", "Guide"))}</span>'
            f'<h2>{html.escape(a["court"])}</h2><p>{html.escape(a["resume"])}</p>'
            f'<span class="lire">{L["lire"]} →</span></a>')


def ecrire(adresse: str, contenu: str) -> None:
    cible = SORTIE / adresse.strip("/") / "index.html" if not adresse.endswith((".html", ".xml", ".txt", ".css")) \
        else SORTIE / adresse.strip("/")
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(contenu, encoding="utf-8")


def fabriquer_blog(langue: str, articles: list, groupes: dict) -> None:
    L = LANGUES[langue]
    for a in articles:
        autres = {b["langue"]: b["adresse"] for b in groupes.get(a["groupe"], [a])}
        tete = tete_commune(a["titre"], a["description"], a["adresse"], langue, autres, "article")
        fil = [("Naylis Agency", L["racine"]), ("Blog", L["blog"]), (a["court"], a["adresse"])]
        graphe = [ORGANISATION, {
            "@type": "BlogPosting", "headline": texte_nu(a["h1"]), "description": a["description"],
            "datePublished": a["date"], "dateModified": a.get("maj", a["date"]), "inLanguage": langue,
            "mainEntityOfPage": SITE + a["adresse"], "image": SITE + "/icon-512.png",
            "author": {"@id": SITE + "/#organisation"}, "publisher": {"@id": SITE + "/#organisation"},
        }, {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(fil)]}]
        faq = ""
        if a["faq"]:
            graphe.append({"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": texte_nu(r)}}
                for q, r in a["faq"]]})
            faq = (f'<section class="faq-article"><h2>{L["faq"]}</h2>'
                   + "".join(f"<details class=\"glass\"><summary>{html.escape(q)}</summary><p>{r}</p></details>"
                             for q, r in a["faq"]) + "</section>")
        tete += ld({"@context": "https://schema.org", "@graph": graphe})
        voisins = [b for b in articles if b is not a][:3]
        corps = (
            f'<nav class="fil" aria-label="Breadcrumb"><a href="{L["racine"]}">{L["accueil"]}</a> › '
            f'<a href="{L["blog"]}">Blog</a> › <span>{html.escape(a["court"])}</span></nav>'
            f'<article class="article"><header><p class="eyebrow">{html.escape(a.get("rubrique", "Guide"))}</p>'
            f'<h1>{a["h1"]}</h1><p class="meta">{L["maj"]} <time datetime="{a.get("maj", a["date"])}">'
            f'{date_lisible(a.get("maj", a["date"]), langue)}</time> · {a["minutes"]} {L["minutes"]}</p></header>'
            f'<div class="prose">{a["corps"]}</div>{faq}'
            f'<aside class="cta glass"><h2>{L["cta_titre"]}</h2><p>{L["cta_texte"]}</p>'
            f'<a class="btn btn-primary" href="{L["racine"]}#apply">{L["cta_bouton"]} →</a></aside></article>'
            f'<section class="suite"><h2>{L["suite"]}</h2><div class="grille">'
            + "".join(carte(b, L) for b in voisins) + "</div></section>")
        ecrire(a["adresse"], page(langue, tete, corps, articles, autres))
    # La page d'accueil du blog
    autres = {l: LANGUES[l]["blog"] for l in LANGUES}
    tete = tete_commune(L["blog_titre"], L["blog_description"], L["blog"], langue, autres)
    tete += ld({"@context": "https://schema.org", "@graph": [ORGANISATION, {
        "@type": "Blog", "name": texte_nu(L["blog_h1"]), "url": SITE + L["blog"], "inLanguage": langue,
        "publisher": {"@id": SITE + "/#organisation"},
        "blogPost": [{"@type": "BlogPosting", "headline": texte_nu(a["h1"]), "url": SITE + a["adresse"],
                      "datePublished": a["date"]} for a in articles]}]})
    corps = (f'<section class="blog-tete"><p class="eyebrow">Blog</p><h1>{L["blog_h1"]}</h1>'
             f'<p class="lead">{L["blog_intro"]}</p></section><div class="grille">'
             + "".join(carte(a, L) for a in articles) + "</div>"
             f'<aside class="cta glass"><h2>{L["cta_titre"]}</h2><p>{L["cta_texte"]}</p>'
             f'<a class="btn btn-primary" href="{L["racine"]}#apply">{L["cta_bouton"]} →</a></aside>')
    ecrire(L["blog"], page(langue, tete, corps, articles, autres))


# ------------------------------------------------------------------ l'accueil
def dictionnaire(source: str, langue: str) -> dict:
    """Le français vit dans le script de page.html ; les autres langues dans traductions/<langue>.json."""
    if langue == "fr":
        return dictionnaire_fr(source)
    return json.loads((ICI / "traductions" / f"{langue}.json").read_text(encoding="utf-8"))


def dictionnaire_fr(source: str) -> dict:
    bloc = source[source.index("var FR = {") + 9: source.index("};", source.index("var FR = {")) + 1]
    return {cle: json.loads('"' + valeur + '"')
            for cle, valeur in re.findall(r'(\w+):\s*"((?:[^"\\]|\\.)*)"', bloc)}


def en_francais(corps: str, fr: dict) -> str:
    """Écrit le français DANS la page (ce que le bouton FR faisait après coup dans le navigateur)."""
    def texte(m):
        return m.group(1) + fr[m.group(3)] + m.group(5) if m.group(3) in fr else m.group(0)
    corps = re.sub(r'(<(\w+)\b[^>]*\bdata-i="(\w+)"[^>]*>)(.*?)(</\2>)', texte, corps, flags=re.S)

    def indice(m):
        cle = re.search(r'data-ip="(\w+)"', m.group(0)).group(1)
        if cle not in fr:
            return m.group(0)
        return re.sub(r'placeholder="[^"]*"', 'placeholder="%s"' % html.escape(fr[cle], quote=True), m.group(0))
    return re.sub(r'<[^>]*\bdata-ip="\w+"[^>]*>', indice, corps)


def fabriquer_accueil(langue: str, articles: list) -> None:
    L = LANGUES[langue]
    source = (ICI / "page.html").read_text(encoding="utf-8")
    tete, corps = source.split("<!--BODY-->", 1)
    tete = tete.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    tete = re.sub(r"<title>.*?</title>\n?", "", tete)
    if langue != "en":
        corps = en_francais(corps, dictionnaire(source, langue))
        corps = corps.replace('aria-pressed="true">EN', 'aria-pressed="false">EN').replace(
            'aria-pressed="false">%s' % langue.upper(), 'aria-pressed="true">%s' % langue.upper())
    corps = corps.replace('href="/blog/" data-blog', 'href="%s"' % L["blog"])
    liens = "".join(f'<a href="{a["adresse"]}">{html.escape(a["court"])}</a>' for a in articles)
    corps = corps.replace("<!--LIENS-BLOG-->", f'<div class="foot-liens"><b>{L["guides"]}</b>'
                          f'<a href="{L["blog"]}">Blog</a>{liens}</div>')
    questions = re.findall(r'<summary[^>]*>(.*?)</summary>\s*<p[^>]*>(.*?)</p>', corps, flags=re.S)
    graphe = [ORGANISATION,
              {"@type": "WebSite", "url": SITE + "/", "name": "Naylis Agency", "inLanguage": langue,
               "publisher": {"@id": SITE + "/#organisation"}},
              {"@type": "Service", "serviceType": "OnlyFans management", "provider": {"@id": SITE + "/#organisation"},
               "name": texte_nu(L["titre"].split("|")[0]), "description": L["description"], "areaServed": "Worldwide",
               "url": SITE + L["racine"]},
              {"@type": "FAQPage", "mainEntity": [
                  {"@type": "Question", "name": texte_nu(q), "acceptedAnswer": {"@type": "Answer", "text": texte_nu(r)}}
                  for q, r in questions]}]
    doc = ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' % langue
           + tete_commune(L["titre"], L["description"], L["racine"], langue, {l: LANGUES[l]["racine"] for l in LANGUES})
           + ld({"@context": "https://schema.org", "@graph": graphe})
           + '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
           + '<script>window.NAYLIS_MAIL="%s";window.NAYLIS_LANGUE="%s";</script>\n' % (MAIL, langue)
           + tete.strip() + "\n</head>\n<body>\n" + corps.strip() + "\n</body>\n</html>\n")
    ecrire(L["racine"] if langue != "en" else "/index.html", doc)


def main() -> None:
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    for f in FICHIERS:
        shutil.copyfile(ICI / f, SORTIE / f)
    shutil.copyfile(ICI / "assets" / "blog.css", SORTIE / "blog.css")
    articles = {l: sorted((lire_article(c, l) for c in (ICI / "articles" / l).glob("*.html")),
                          key=lambda a: int(a.get("ordre", 99))) for l in LANGUES}
    # Les versions d'un même article se retrouvent par leur adresse ANGLAISE : un article français ou
    # espagnol la donne dans « jumeau ». Sans jumeau, l'article n'existe que dans sa langue.
    groupes = {}
    for l in articles:
        for a in articles[l]:
            a["groupe"] = a["adresse_courte"] if l == "en" else (a.get("jumeau") or f"{l}:{a['adresse_courte']}")
            groupes.setdefault(a["groupe"], []).append(a)
    pages = []
    for l in LANGUES:
        fabriquer_accueil(l, articles[l])
        fabriquer_blog(l, articles[l], groupes)
        pages += [(LANGUES[l]["racine"], "1.0", None), (LANGUES[l]["blog"], "0.8", None)]
        pages += [(a["adresse"], "0.7", a.get("maj", a["date"])) for a in articles[l]]
    plan = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for adresse, poids, date in pages:
        plan.append("  <url><loc>%s%s</loc>%s<priority>%s</priority></url>"
                    % (SITE, adresse, "<lastmod>%s</lastmod>" % date if date else "", poids))
    ecrire("/sitemap.xml", "\n".join(plan + ["</urlset>"]) + "\n")
    ecrire("/robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
    L = LANGUES["en"]
    tete = ('<title>Page not found | Naylis Agency</title>\n<meta name="robots" content="noindex">\n'
            '<link rel="icon" href="/favicon.ico" sizes="any">\n')
    corps = (f'<section class="blog-tete"><p class="eyebrow">404</p><h1>{L["introuvable"]}</h1>'
             f'<p class="lead">{LANGUES["fr"]["introuvable"]}</p>'
             f'<p><a class="btn btn-primary" href="/">{L["retour"]}</a> '
             f'<a class="btn btn-ghost" href="/fr/">{LANGUES["fr"]["retour"]}</a> '
             f'<a class="btn btn-ghost" href="/es/">{LANGUES["es"]["retour"]}</a></p></section>')
    ecrire("/404.html", page("en", tete, corps, articles["en"]))
    print("site/ :", sum(1 for _ in SORTIE.rglob("*.html")), "pages,", len(pages), "adresses dans le plan du site")


if __name__ == "__main__":
    main()
