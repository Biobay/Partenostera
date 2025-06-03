# Frontend Dockerfile
FROM node:18-alpine

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file package
COPY package*.json ./

# Installa le dipendenze
RUN npm ci --only=production

# Copia il codice sorgente
COPY . .

# Build dell'applicazione
RUN npm run build

# Usa nginx per servire l'applicazione
FROM nginx:alpine

# Copia i file build
COPY --from=0 /app/build /usr/share/nginx/html

# Copia la configurazione nginx personalizzata
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Espone la porta
EXPOSE 80

# Comando di avvio
CMD ["nginx", "-g", "daemon off;"]
