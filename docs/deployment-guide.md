# 🚀 راهنمای استقرار Far AI روی سرور

> این راهنما «روز ۲ و ۲۹» پلن را پوشش می‌دهد: از صفر تا داشتن Far AI روی یک سرور واقعی
> با دامنه و SSL. هر دستوری را به‌ترتیب اجرا کنید.

---

## 🏃 مسیر سریع (پیشنهادی — فقط ۴ قدم)

اگر نمی‌خواهید دستورات را یکی‌یکی بزنید، اسکریپت خودکار همه‌چیز را انجام می‌دهد:

```bash
# ۱) آپلود پروژه روی سرور (از روی سیستم خودتان):
cd far-ai
tar -czf far-ai.tar.gz --exclude=".venv" --exclude="*.db" .
scp far-ai.tar.gz root@YOUR_SERVER_IP:/opt/

# ۲) روی سرور:
cd /opt && tar -xzf far-ai.tar.gz

# ۳) اجرای راه‌انداز خودکار (نصب Docker + کلیدها + بالا آوردن سیستم):
sudo bash /opt/far-ai/deploy/setup.sh

# ۴) بعد از تمام شدن:
#    - رکورد DNS:  api.<دامنه>  ←  IP سرور
#    - SSL:  certbot --nginx -d api.<دامنه>
#    - نصب پلاگین وردپرس و تنظیم آدرس API
```

اسکریپت `deploy/setup.sh` به‌صورت خودکار:
1. Docker و Docker Compose را نصب می‌کند
2. فایل `.env` را می‌سازد و کلیدها را از شما می‌پرسد
3. رمز دیتابیس و رمز داشبورد را خودش می‌سازد
4. CORS را با دامنه شما تنظیم می‌کند
5. کل سیستم را بالا می‌آورد و سلامت آن را چک می‌کند

> بقیه این راهنما، توضیح گام‌به‌گام همین کارهاست (برای وقتی که بخواهید دستی انجام دهید).

---

## ۱) انتخاب سرور

### گزینه A — VPS اروپایی (پیشنهاد برای شروع) 🥇
- **Hetzner** یا **Contabo** — حدود ۵ تا ۱۰ دلار در ماه
- بدون دردسر تحریم و پرداخت (کارت ارزی یا ریالی واسط)
- مشخصات: Ubuntu 24.04 LTS، ۲ vCPU، ۴GB RAM، ۵۰GB SSD

### گزینه B — Oracle Cloud (لایه رایگان) 🆓
- **Always Free**: Ampere A1 (۴ هسته + ۲۴GB رمز) یا ۲ ماشین AMD Micro
- ذخیره‌سازی ۲۰۰GB رایگان + ۱۰TB خروجی اینترنت — هزینه سرور صفر
- مشخصات: Ubuntu 24.04 LTS (image رسمی Canonical)
- **نکات مخصوص Oracle Cloud:**
  - ✅ همه تصاویر Docker پروژه از ARM پشتیبانی می‌کنند — بدون نیاز به تغییر کد
  - ⚠️ **پورت ۸۰/۴۳ پیش‌فرض بسته است:** کنسول OCI ← Networking ← VCN ← Security Lists ← Add Ingress Rules برای TCP 80 و TCP 443 (Source: 0.0.0.0/0)
  - ⚠️ خطای «Out of capacity» موقع ساخت Ampere رایج است — چند بار تلاش یا تغییر region
  - ⚠️ ساخت اکانت نیاز به کارت بین‌المللی دارد و گاهی اکانت‌های ایرانی رد می‌شوند
  - Boot volume پیش‌فرض ~47GB — در صورت نیاز یک Block Volume اضافه کنید

### گزینه C — Google Cloud (Compute Engine)
- برای بعداً که پروژه جدی‌تر شد
- ساخت اکانت نیاز به کارت بین‌المللی دارد
- چون همه‌چیز Docker است، **انتقال از هر گزینه‌ای فقط چند ساعت طول می‌کشد** (بخش ۱۲)

---

## ۲) اتصال به سرور

```bash
ssh root@YOUR_SERVER_IP
```

> بعد از اولین ورود، حتماً این‌ها را انجام بده (بخش ۹ «امنیت» را ببین).

---

## ۳) نصب Docker

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
docker --version   # تست
```

---

## ۴) انتقال پروژه به سرور

روش ۱ — با Git (پیشنهادی):

```bash
cd /opt
git clone <آدرس ریپوی شما> far-ai
cd far-ai
```

روش ۲ — اگر ریپو ندارید (انتقال مستقیم از روی سیستم خودتان):

```bash
# روی سیستم خودتان (جایی که پروژه است):
cd far-ai
tar -czf far-ai.tar.gz --exclude=".venv" --exclude="*.db" .

# روی سرور:
scp far-ai.tar.gz root@YOUR_SERVER_IP:/opt/
cd /opt && tar -xzf far-ai.tar.gz && mv far-ai* far-ai 2>/dev/null; cd far-ai
```

---

## ۵) تنظیم `.env`

```bash
cd /opt/far-ai
cp .env.example .env
nano .env
```

چیزهایی که باید پر کنی:

| متغیر | از کجا؟ |
|---|---|
| `GEMINI_API_KEY` | **رایگان** از [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — بدون کارت بانکی (پیشنهادی) |
| `AI_PROVIDER` | `gemini` (پیش‌فرض) یا `openai` |
| `OPENAI_API_KEY` | فقط اگر `AI_PROVIDER=openai` گذاشتید — از [platform.openai.com](https://platform.openai.com) |
| `POSTGRES_PASSWORD` | یک رمز قوی خودت بساز |
| `TELEGRAM_BOT_TOKEN` | از [@BotFather](https://t.me/BotFather) → `/newbot` |
| `TELEGRAM_TEAM_CHAT_ID` | آیدی چت/کانال خصوصی تیم (عدد منفی برای گروه) |
| `SMTP_*` + `EMAIL_TO` | تنظیمات ایمیل تیم |
| `CORS_ORIGINS` | `["https://far.agency","https://www.far.agency"]` — دامنه واقعی سایت |
| `ADMIN_TOKEN` | یک رمز تصادفی برای داشبورد |

ساخت رمز تصادفی:

```bash
openssl rand -hex 24
```

> ⚠️ `.env` هرگز نباید وارد گیت شود. (`.gitignore` آماده است)

---

## ۶) بالا آوردن سیستم

```bash
docker compose up -d --build
```

چک کردن وضعیت:

```bash
docker compose ps          # هر سه سرویس باید Up باشند
docker compose logs -f     # دیدن لاگ‌ها
```

تست سریع:

```bash
curl http://localhost/health
# → {"status":"ok","database":"ok"}

curl -X POST http://localhost/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"سلام، می‌خوام سایت داشته باشم","source":"website"}'
# → {"session_id":"...","answer":"..."}
```

---

## ۷) دامنه + SSL

### ۷.۱) وصل کردن دامنه
یک رکورد DNS از نوع **A** بسازید:
```
نام:  api
مقدار:  <IP سرور شما>
```
مثلاً `api.far.agency` → `1.2.3.4`

### ۷.۲) تنظیم دامنه در Nginx
فایل `deploy/nginx.conf` را باز کن و در `server_name` دامنه خودت را بگذار:

```bash
nano /opt/far-ai/deploy/nginx.conf
```

سپس:

```bash
docker compose restart nginx
```

### ۷.۳) SSL رایگان با Let's Encrypt

نصب certbot:

```bash
apt update && apt install -y certbot
```

صدور گواهی:

```bash
certbot certonly --standalone -d api.far.agency --register-unsafely-without-email
```

> قبل از این دستور، nginx را موقتاً متوقف کن: `docker compose stop nginx`

پس از صدور، کپی گواهی‌ها:

```bash
mkdir -p /etc/letsencrypt  # پوشه روی هاست به کانتینر mount شده است
```

ویرایش `docker-compose.yml` برای فعال کردن HTTPS (فایل را باز کن و بخش nginx را کامل کن):

```yaml
  nginx:
    ...
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

فایل `deploy/nginx-ssl.conf` (نمونه):

```nginx
server {
    listen 80;
    server_name api.far.agency;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl;
    server_name api.far.agency;

    ssl_certificate     /etc/letsencrypt/live/api.far.agency/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.far.agency/privkey.pem;

    limit_req_zone $binary_remote_addr zone=far_ai:10m rate=10r/m;

    location / {
        limit_req zone=far_ai burst=20 nodelay;
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90s;
    }
}
```

راه‌اندازی مجدد:

```bash
docker compose up -d --build
docker compose logs nginx
```

تست نهایی:

```bash
curl https://api.far.agency/health
```

---

## ۸) داشبورد مدیریت لیدها

آدرس: `https://api.far.agency/dashboard`

- رمز ورود = همان `ADMIN_TOKEN` در `.env`
- نمایش: لیدهای امروز، لیدهای داغ، توزیع خدمات، آخرین مکالمات
- به‌روزرسانی خودکار هر ۳۰ ثانیه

---

## ۹) امنیت (چک‌لیست قبل از Launch)

```bash
# ۱) فایروال — فقط SSH، HTTP، HTTPS
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# ۲) ورود SSH با کلید به‌جای رمز
# در /etc/ssh/sshd_config:
#   PasswordAuthentication no
systemctl restart sshd

# ۳) اطمینان از رمز قوی PostgreSQL در .env
# ۴) ADMIN_TOKEN حتماً پر باشد
# ۵) CORS فقط دامنه فَر
# ۶) بکاپ روزانه (پایین)
```

---

## ۱۰) بکاپ روزانه

اسکریپت آماده است:

```bash
chmod +x /opt/far-ai/deploy/backup.sh
crontab -e
# این خط را اضافه کن (هر روز ۰۳:۰۰):
0 3 * * * cd /opt/far-ai && ./deploy/backup.sh >> /var/log/far-ai-backup.log 2>&1
```

تست بکاپ:

```bash
/opt/far-ai/deploy/backup.sh
ls -la /var/backups/far-ai/
```

---

## ۱۱) به‌روزرسانی سیستم

```bash
cd /opt/far-ai
git pull
docker compose up -d --build
docker image prune -f   # پاک‌سازی تصاویر قدیمی
```

---

## ۱۲) انتقال از VPS به Google Cloud (بعداً)

چون همه‌چیز Docker است، انتقال ساده است:

```bash
# ۱) روی سرور فعلی — پشتیبان دیتابیس
./deploy/backup.sh

# ۲) روی Google Cloud — ساخت VM با Ubuntu 24.04
# ۳) نصب Docker (مثل بخش ۳)
# ۴) انتقال پروژه + .env
scp -r /opt/far-ai root@NEW_SERVER_IP:/opt/

# ۵) برگرداندن بکاپ دیتابیس
docker compose up -d db
docker compose exec -T db pg_restore -U far -d far_ai < latest_backup

# ۶) بالا آوردن کامل
docker compose up -d --build
```

> همین! چون معماری وابسته به میزبان نیست، جابه‌جایی فقط چند ساعت کار دارد.

---

## ۱۳) عیب‌یابی رایج

| مشکل | راه‌حل |
|---|---|
| `OPENAI_API_KEY تنظیم نشده` | در `.env` کلید را پر کن، سپس `docker compose up -d` |
| پاسخ ۴۲۹ از API | تعداد پیام بیشتر از حد مجاز در دقیقه — `RATE_LIMIT_PER_MINUTE` را بالا ببر |
| CORS Error در سایت | دامنه سایت را در `CORS_ORIGINS` بگذار |
| بات تلگرام جواب نمی‌دهد | `TELEGRAM_BOT_TOKEN` را چک کن + `docker compose logs bot` |
| دیتابیس وصل نمی‌شود | `docker compose logs db` — رمز/نام در `.env` را با compose مقایسه کن |
| SSL معتبر نیست | `docker compose logs nginx` — مسیر گواهی‌ها را چک کن |
