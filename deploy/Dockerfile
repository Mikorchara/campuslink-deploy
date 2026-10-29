FROM node:24-bookworm-slim AS frontend
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts tsconfig*.json ./
COPY src ./src
COPY public ./public
ENV VITE_API_BASE_URL=/api
RUN npm run typecheck && npm run build -- --outDir /site

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt \
    && useradd --create-home --uid 10001 campuslink
COPY backend/src ./src
COPY backend/tools ./tools
COPY deploy/start.py /app/deploy/start.py
COPY --from=frontend /site /app/site
ENV CAMPUSLINK_FRONTEND_DIST=/app/site
USER campuslink
EXPOSE 10000
CMD ["python", "/app/deploy/start.py"]
