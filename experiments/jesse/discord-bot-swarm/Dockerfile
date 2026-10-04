FROM node:24-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY scripts ./scripts
RUN npm run build

FROM node:24-bookworm-slim
ENV NODE_ENV=production PORT=3000 DATA_DIR=/var/lib/swarm
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && mkdir -p /var/lib/swarm && chown node:node /var/lib/swarm && chmod 700 /var/lib/swarm
COPY --chown=node:node server.js channel-setup.js config.js authentication.js core.js research.js vault.js store.js experiment.js discord.js discord-memory.js discord-commands.js chat-settings.js kanban.js setup-credentials.js relay-records.js mcp.js VERSION ./
COPY --chown=node:node frontend ./frontend
COPY --chown=node:node deploy/fairystack/adapter.js ./deploy/fairystack/adapter.js
COPY --from=build --chown=node:node /app/frontend/auth-oidc.js /app/frontend/THIRD_PARTY_NOTICES.txt ./frontend/
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD node -e "fetch('http://127.0.0.1:3000/health',{signal:AbortSignal.timeout(3000)}).then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "server.js"]
