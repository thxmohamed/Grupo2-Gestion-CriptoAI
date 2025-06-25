# Usar Node.js 18 como imagen base
FROM node:18-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json (si existe)
COPY package*.json ./

# Instalar dependencias
RUN npm ci 

# Copiar el código fuente
COPY . .

# Construir la aplicación para producción
RUN npm run build

RUN npm install -g serve

# Crear un usuario no root para seguridad
RUN addgroup -g 1001 -S nodejs
RUN adduser -S react -u 1001

# Cambiar la propiedad de los archivos al usuario react
RUN chown -R react:nodejs /app
USER react

# Exponer puerto para desarrollo (opcional)
EXPOSE 3000

# El comando por defecto será servir los archivos construidos
# Los archivos estáticos estarán en /app/dist
CMD ["serve", "-s", "dist", "-l", "3000"]
