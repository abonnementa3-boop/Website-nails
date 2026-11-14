"""Fabrique index.html (site complet, à héberger tel quel) à partir de page.html."""
from pathlib import Path

ici = Path(__file__).parent
tete, corps = (ici / "page.html").read_text(encoding="utf-8").split("<!--BODY-->", 1)
tete = tete.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       '<meta name="description" content="Naylis Agency: 24/7 chatting, managed socials and traffic generated on top of yours, by a dedicated team. 50/50 split. Apply in two minutes.">\n'
       '<link rel="icon" type="image/svg+xml" href="logo.svg">\n'
       '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
       '<script>window.NAYLIS_MAIL="https://formsubmit.co/ajax/kylian.business@icloud.com";</script>\n'
       + tete.strip() + "\n</head>\n<body>\n" + corps.strip() + "\n</body>\n</html>\n")
(ici / "index.html").write_text(doc, encoding="utf-8")
print("index.html :", len(doc), "octets")
