# Author: niranjanxprt (https://github.com/niranjanxprt)
# React frontend - run from frontend-react/ as root directory
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . ./
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-http://localhost:8000}
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
ENV NODE_ENV=production
EXPOSE 3000
CMD serve -s dist -l ${PORT:-3000}
