# Naylis Agency — site

Site d'une page (présentation + candidature). Anglais par défaut, bouton FR.

- `index.html` : le site complet, c'est lui qui est servi.
- `logo.svg` : le logo (et l'icône de l'onglet).
- `page.html` + `build.py` : la source. Après une modification de `page.html`, lancer `python3 build.py` pour refaire `index.html`.
- `Dockerfile` + `nginx.conf.template` : ce que Railway construit et lance.

Candidatures : le formulaire demande le numéro WhatsApp de la candidate et envoie tout par e-mail
(FormSubmit, adresse dans `build.py`, `NAYLIS_MAIL`), puis affiche « Candidature envoyée ». Aucun contact
de l'agence n'est affiché sur le site. FormSubmit demande une activation : le premier envoi déclenche un
mail avec un lien à cliquer ; tant qu'il n'est pas cliqué, le site affiche une erreur d'envoi.
