# Site statique Naylis Agency, servi par nginx sur le port que Railway donne ($PORT).
# Image prise sur le registre public d'Amazon : le quota anonyme de Docker Hub est partagé sur Railway.
# site/ est fabriqué par « python3 build.py » et livré tel quel (pas de Python dans l'image).
FROM public.ecr.aws/nginx/nginx:stable-alpine
ENV PORT=8080
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY site/ /usr/share/nginx/html/
