# Naylis Agency — site

Site d'une page (présentation + candidature). Anglais par défaut, bouton FR.

- `index.html` : le site complet, c'est lui qui est servi.
- `logo.svg` : le logo (et l'icône de l'onglet).
- `page.html` + `build.py` : la source. Après une modification de `page.html`, lancer `python3 build.py` pour refaire `index.html`.
- `Dockerfile` + `nginx.conf.template` : ce que Railway construit et lance.

Candidatures : bouton WhatsApp (numéro dans `page.html`, `CONTACT`) et e-mail par FormSubmit
(adresse dans `build.py`, `NAYLIS_MAIL`). FormSubmit demande une activation : le premier envoi
déclenche un mail avec un lien à cliquer.
