# Site statique Naylis Agency, servi par nginx sur le port que Railway donne ($PORT).
# Image prise sur le registre public d'Amazon : le quota anonyme de Docker Hub est partagé sur Railway.
FROM public.ecr.aws/nginx/nginx:stable-alpine
ENV PORT=8080
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY index.html logo.svg favicon.ico favicon-32x32.png apple-touch-icon.png icon-512.png /usr/share/nginx/html/
