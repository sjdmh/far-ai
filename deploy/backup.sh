#!/usr/bin/env bash
# ── بکاپ روزانه دیتابیس Far AI (روز ۲۷ سند) ──
# اجرا از ریشه پروژه (جایی که docker-compose.yml هست):
#   ./deploy/backup.sh
# افزودن به cron (هر روز ساعت ۰۳:۰۰):
#   0 3 * * * cd /opt/far-ai && ./deploy/backup.sh >> /var/log/far-ai-backup.log 2>&1
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/far-ai}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP="$(date +%Y%m%d_%H%M%S)"
DB_USER="${POSTGRES_USER:-far}"
DB_NAME="${POSTGRES_DB:-far_ai}"

mkdir -p "$BACKUP_DIR"

docker compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" \
  | gzip > "$BACKUP_DIR/far_ai_${STAMP}.sql.gz"

# حذف بکاپ‌های قدیمی‌تر از دوره نگهداری
find "$BACKUP_DIR" -name 'far_ai_*.sql.gz' -mtime "+${RETENTION_DAYS}" -delete

echo "✅ بکاپ ساخته شد: $BACKUP_DIR/far_ai_${STAMP}.sql.gz"
