FROM node:20-alpine AS builder
ARG VITE_BACKEND_URL=http://backend:8000
WORKDIR /app
COPY package.json package-lock.json* npm-shrinkwrap.json* ./
RUN npm ci || npm install
COPY . .
RUN VITE_BACKEND_URL=$VITE_BACKEND_URL npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
