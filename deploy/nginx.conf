# Far AI — Nginx Reverse Proxy
# ۱) دامنه خود را در server_name جایگزین کنید
# ۲) برای HTTPS: certbot --nginx یا docker certbot (ولوم‌های certbot آماده است)

limit_req_zone $binary_remote_addr zone=far_ai:10m rate=10r/m;

server {
    listen 80;
    server_name api.far.agency;   # ← دامنه API خودتان

    # مسیر چک سلامت
    location /health {
        proxy_pass http://backend:8000/health;
        proxy_set_header Host $host;
    }

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
