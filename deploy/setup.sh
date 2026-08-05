#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Far AI — راه‌انداز خودکار سرور (Ubuntu / Debian)
#  اجرا:  sudo bash setup.sh
#  کارها: نصب Docker ← ساخت .env ← دریافت کلیدها ← بالا آوردن سیستم
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ""
echo "══════════════════════════════════════════"
echo "   Far AI — راه‌انداز خودکار 🦚"
echo "══════════════════════════════════════════"
echo ""

# ── ۱) روت بودن ─────────────────────────────────────────────
[ "$(id -u)" -eq 0 ] || fail "لطفاً با root اجرا کنید:  sudo bash setup.sh"

# ── ۲) نصب Docker ────────────────────────────────────────────
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    info "Docker از قبل نصب است"
else
    warn "در حال نصب Docker (چند دقیقه طول می‌کشد)..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker || true
    command -v docker >/dev/null 2>&1 || fail "نصب Docker ناموفق بود"
    info "Docker نصب شد"
fi

# ── ۳) ساخت فایل .env ────────────────────────────────────────
cd "$PROJECT_DIR"
if [ ! -f .env ]; then
    cp .env.example .env
    info "فایل .env ساخته شد"
else
    warn "فایل .env وجود دارد — فقط مقادیر خالی را می‌پرسیم"
fi

set_env() {
    local key="$1" value="$2"
    if grep -q "^${key}=" .env; then
        sed -i "s|^${key}=.*|${key}=${value}|" .env
    else
        echo "${key}=${value}" >> .env
    fi
}

# ── ۴) کلیدهای مورد نیاز ─────────────────────────────────────
echo ""
echo "──────────────────────────────────────────────"
echo "  کلیدها را وارد کنید (Enter = بدون تغییر)"
echo "──────────────────────────────────────────────"

read -rp "  ۱) تامین‌کننده هوش مصنوعی [gemini=رایگان/پیشنهادی، openai=پولی] (پیش‌فرض: gemini): " AI_PROVIDER
AI_PROVIDER="${AI_PROVIDER:-gemini}"
set_env "AI_PROVIDER" "$AI_PROVIDER"

if [ "$AI_PROVIDER" = "openai" ]; then
    read -rp "     OPENAI_API_KEY (کلید پولی OpenAI): " OPENAI_API_KEY
    [ -n "$OPENAI_API_KEY" ] && set_env "OPENAI_API_KEY" "$OPENAI_API_KEY"
else
    read -rp "     GEMINI_API_KEY (کلید رایگان — از aistudio.google.com/apikey): " GEMINI_API_KEY
    [ -n "$GEMINI_API_KEY" ] && set_env "GEMINI_API_KEY" "$GEMINI_API_KEY"
fi

read -rp "  ۲) TELEGRAM_BOT_TOKEN (توکن ربات تلگرام): " TELEGRAM_BOT_TOKEN
[ -n "$TELEGRAM_BOT_TOKEN" ] && set_env "TELEGRAM_BOT_TOKEN" "$TELEGRAM_BOT_TOKEN"

read -rp "  ۳) TELEGRAM_TEAM_CHAT_ID (آیدی کانال/گروه تیم): " TELEGRAM_TEAM_CHAT_ID
[ -n "$TELEGRAM_TEAM_CHAT_ID" ] && set_env "TELEGRAM_TEAM_CHAT_ID" "$TELEGRAM_TEAM_CHAT_ID"

read -rp "  ۴) دامنه سایت شما (مثلاً farr-agency.com) برای CORS: " SITE_DOMAIN
if [ -n "$SITE_DOMAIN" ]; then
    CORS="[\"https://${SITE_DOMAIN}\",\"https://www.${SITE_DOMAIN}\",\"http://localhost\"]"
    set_env "CORS_ORIGINS" "$CORS"
    info "CORS تنظیم شد: $CORS"
fi

# ── رمزهای خودکار ────────────────────────────────────────────
if grep -qE "^POSTGRES_PASSWORD=(far-secret|یک-رمز-قوی-بگذار|تغییرش-بده-یک-رمز-قوی)$" .env || ! grep -q "^POSTGRES_PASSWORD=.\{16,\}" .env; then
    GEN_PASS="$(openssl rand -hex 16)"
    set_env "POSTGRES_PASSWORD" "$GEN_PASS"
    info "رمز دیتابیس به‌صورت خودکار ساخته شد"
fi

if ! grep -q "^ADMIN_TOKEN=.\{16,\}" .env; then
    GEN_TOKEN="$(openssl rand -hex 24)"
    set_env "ADMIN_TOKEN" "$GEN_TOKEN"
    info "رمز داشبورد (ADMIN_TOKEN) به‌صورت خودکار ساخته شد"
fi

# ── ۵) بالا آوردن سیستم ──────────────────────────────────────
echo ""
info "در حال بالا آوردن سرویس‌ها (بار اول چند دقیقه طول می‌کشد)..."
docker compose up -d --build

# ── ۶) انتظار برای آماده شدن Backend ─────────────────────────
echo ""
info "در انتظار آماده شدن Far AI..."
for _ in $(seq 1 30); do
    if curl -fsS http://localhost/health >/dev/null 2>&1; then
        break
    fi
    sleep 2
done

echo ""
echo "══════════════════════════════════════════"
if curl -fsS http://localhost/health >/dev/null 2>&1; then
    info "Far AI با موفقیت راه‌اندازی شد! 🎉"
    curl -s http://localhost/health
else
    warn "سیستم بالا آمد ولی هنوز پاسخ نمی‌دهد — لاگ‌ها را ببینید:"
    echo "   docker compose logs -f"
fi
echo ""
echo "  ── کارهای بعدی ──────────────────────────"
echo "  ۱) رکورد DNS:  api.<دامنه>  ←  IP این سرور"
echo "  ۲) SSL:  certbot --nginx -d api.<دامنه>"
echo "  ۳) نصب پلاگین وردپرس و تنظیم آدرس API"
echo "  راهنمای کامل:  docs/deployment-guide.md"
echo "══════════════════════════════════════════"
