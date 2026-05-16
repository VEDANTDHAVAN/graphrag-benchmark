# Security Checklist

- [ ] `.env` and `.env.production` are not committed.
- [ ] Production secrets are managed in Render/Vercel/VPS secret stores.
- [ ] `FRONTEND_URL` is set and CORS is restricted.
- [ ] `ADMIN_API_KEY` is set in production.
- [ ] Admin routes such as upload/ingestion require bearer auth.
- [ ] `SESSION_SECRET` or `JWT_SECRET` is set in production.
- [ ] HTTPS is enabled at the hosting/proxy layer.
- [ ] Request size limits are configured with `MAX_REQUEST_BYTES`.
- [ ] Rate limiting is enabled with `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`.
- [ ] `/health` passes.
- [ ] `/ready` passes.
- [ ] Data backups are configured with `scripts/backup_data.sh`.
- [ ] Restore has been tested with `scripts/restore_data.sh`.
- [ ] Application works with `TIGERGRAPH_ENABLED=false`.
- [ ] If TigerGraph is enabled, default passwords are changed.
- [ ] If TigerGraph is enabled, credentials are provided only through environment variables.
- [ ] No secrets are stored in Dockerfiles, compose files, `render.yaml`, or `vercel.json`.
