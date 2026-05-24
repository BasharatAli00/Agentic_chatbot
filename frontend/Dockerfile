# 1. Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
# Point to the package files inside the frontend folder
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# 2. Build the application source
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
# Copy everything inside the frontend subdirectory into the builder
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# 3. Production runner layer
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Next.js standalone features copy things relative to the build context
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]