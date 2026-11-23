# Naylis Agency — site (naylisagency.com)

Site statique : l'accueil (présentation + candidature) en anglais (`/`) et en français (`/fr/`), et un blog
dans les deux langues (`/blog/`, `/fr/blog/`). Railway construit le `Dockerfile` à chaque poussée sur `main`.

- `page.html` : la source de l'accueil (l'anglais dans la page, le français dans le dictionnaire `FR` du script).
- `articles/fr/*.html`, `articles/en/*.html` : un fichier par article du blog.
- `assets/blog.css` : la feuille de style du blog.
- `build.py` : fabrique tout le dossier `site/`. **Après toute modification, lancer `python3 build.py`
  et pousser `site/` avec le reste** (l'image ne contient pas Python : elle sert `site/` tel quel).
- `site/` : ce que nginx sert. Ne pas le modifier à la main.
- `Dockerfile` + `nginx.conf.template` : ce que Railway construit et lance.

## Ajouter un article

Créer `articles/fr/mon-adresse.html` (le nom du fichier devient l'adresse `/fr/blog/mon-adresse/`) :

    titre: Le titre que Google affiche (60 caractères environ)
    description: La phrase sous le titre dans Google (150 caractères environ)
    h1: Le grand titre de la page, <em>avec une partie en violet.</em>
    court: Le nom court (cartes, pied de page)
    resume: Une phrase pour la carte du blog.
    rubrique: Guide
    date: 2026-11-23
    ordre: 9
    jumeau: adresse-de-la-version-anglaise   (facultatif, et à mettre des DEUX côtés)

    <p>Le texte en HTML…</p>

    ---FAQ---
    Q: Une question ?
    R: Sa réponse.

Puis `python3 build.py` : l'article entre seul dans le blog, le pied de page et `sitemap.xml`.

## Ce que build.py pose pour les moteurs de recherche

Un titre et une description par page, l'adresse de référence (`canonical`), le lien entre les deux langues
(`hreflang`), les données structurées (Organization, Service, FAQPage, BlogPosting, BreadcrumbList),
`sitemap.xml`, `robots.txt` et une vraie page 404. PIÈGE : la page française est écrite EN DUR par
`en_francais()` — un texte posé par le bouton FR dans le navigateur n'est pas indexé. Les boutons EN / FR
mènent donc à `/` et `/fr/`.

## Candidatures

Le formulaire demande le numéro WhatsApp de la candidate et envoie tout par e-mail (FormSubmit, adresse dans
`build.py`, `MAIL`), puis affiche « Candidature envoyée ». Aucun contact de l'agence n'est affiché sur le site.
FormSubmit demande une activation : le premier envoi déclenche un mail avec un lien à cliquer.
