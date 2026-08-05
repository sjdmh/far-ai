<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Far AI — داشبورد لیدها</title>
<style>
  :root {
    --accent: #7c3aed;
    --bg: #f4f4f8;
    --card: #ffffff;
    --border: #e5e5ec;
    --text: #1a1a2e;
    --muted: #6b7280;
    --hot: #ef4444;
    --warm: #f59e0b;
    --cold: #3b82f6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Tahoma, "Segoe UI", Arial, sans-serif; background: var(--bg); color: var(--text); }
  header { background: linear-gradient(135deg, #6d28d9, #7c3aed); color: #fff; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
  header h1 { font-size: 20px; }
  header .badge { background: rgba(255,255,255,.18); padding: 6px 12px; border-radius: 20px; font-size: 13px; }
  .container { max-width: 1100px; margin: 24px auto; padding: 0 16px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,.04); }
  .card .label { font-size: 13px; color: var(--muted); margin-bottom: 6px; }
  .card .value { font-size: 28px; font-weight: bold; }
  .card.hot .value { color: var(--hot); }
  .card.today .value { color: var(--accent); }
  .panel { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; margin-bottom: 24px; }
  .panel h2 { font-size: 16px; margin-bottom: 14px; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip { background: #f0edff; color: var(--accent); padding: 6px 14px; border-radius: 20px; font-size: 13px; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { text-align: right; padding: 10px 12px; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: normal; font-size: 12px; }
  .score { display: inline-block; padding: 4px 10px; border-radius: 14px; font-size: 12px; font-weight: bold; color: #fff; }
  .score.hot { background: var(--hot); }
  .score.warm { background: var(--warm); }
  .score.cold { background: var(--cold); }
  .empty { color: var(--muted); text-align: center; padding: 24px; }
  .updated { color: var(--muted); font-size: 12px; }
  #token-modal { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: none; align-items: center; justify-content: center; z-index: 10; }
  #token-modal.show { display: flex; }
  #token-modal .box { background: #fff; border-radius: 14px; padding: 28px; width: 320px; }
  #token-modal input { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; margin: 12px 0; }
  #token-modal button { width: 100%; padding: 10px; border: none; border-radius: 8px; background: var(--accent); color: #fff; font-size: 14px; cursor: pointer; }
</style>
</head>
<body>

<header>
  <h1>🤖 Far AI — داشبورد لیدها</h1>
  <span class="badge" id="updated">در حال بارگذاری…</span>
</header>

<div class="container">
  <div class="cards">
    <div class="card"><div class="label">کل لیدها</div><div class="value" id="total">—</div></div>
    <div class="card today"><div class="label">لیدهای امروز</div><div class="value" id="today">—</div></div>
    <div class="card hot"><div class="label">لیدهای داغ 🔥</div><div class="value" id="hot">—</div></div>
    <div class="card"><div class="label">میانگین امتیاز</div><div class="value" id="avg">—</div></div>
  </div>

  <div class="panel">
    <h2>📊 توزیع خدمات</h2>
    <div class="chips" id="services"></div>
  </div>

  <div class="panel">
    <h2>🕒 آخرین لیدها</h2>
    <table>
      <thead>
        <tr><th>نام</th><th>شرکت</th><th>خدمت</th><th>امتیاز</th><th>منبع</th><th>زمان</th></tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
    <div class="empty" id="empty" hidden>هنوز لیدی ثبت نشده است.</div>
  </div>
</div>

<div id="token-modal">
  <div class="box">
    <h3>🔐 کد دسترسی داشبورد</h3>
    <input type="password" id="token-input" placeholder="ADMIN_TOKEN را وارد کنید">
    <button id="token-submit">ورود</button>
  </div>
</div>

<script>
(function () {
  "use strict";
  var TOKEN_KEY = "far_ai_admin_token";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY) || "";
  }

  function showTokenModal() {
    document.getElementById("token-modal").classList.add("show");
  }

  function hideTokenModal() {
    document.getElementById("token-modal").classList.remove("show");
  }

  function fmtTime(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toLocaleString("fa-IR", { hour: "2-digit", minute: "2-digit", day: "numeric", month: "short" });
  }

  async function load() {
    var token = getToken();
    try {
      var res = await fetch("/api/stats", {
        headers: { "X-Admin-Token": token }
      });
      if (res.status === 401) {
        showTokenModal();
        return;
      }
      if (!res.ok) throw new Error("HTTP " + res.status);
      var data = await res.json();

      document.getElementById("total").textContent = data.total;
      document.getElementById("today").textContent = data.today;
      document.getElementById("hot").textContent = data.hot;
      document.getElementById("avg").textContent = data.average_score;

      var chips = document.getElementById("services");
      chips.innerHTML = "";
      var entries = Object.entries(data.by_service || {});
      if (entries.length === 0) {
        chips.innerHTML = '<span class="updated">—</span>';
      }
      entries.forEach(function (e) {
        var chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = e[0] + " · " + e[1];
        chips.appendChild(chip);
      });

      var rows = document.getElementById("rows");
      rows.innerHTML = "";
      var empty = document.getElementById("empty");
      var recent = data.recent || [];
      empty.hidden = recent.length > 0;
      recent.forEach(function (lead) {
        var tr = document.createElement("tr");
        var service = (lead.service && lead.service.length) ? lead.service.join("، ") : "نامشخص";
        var levelClass = lead.lead_score >= 70 ? "hot" : (lead.lead_score >= 40 ? "warm" : "cold");
        tr.innerHTML =
          "<td>" + (lead.name || "—") + "</td>" +
          "<td>" + (lead.company || "—") + "</td>" +
          "<td>" + service + "</td>" +
          '<td><span class="score ' + levelClass + '">' + lead.lead_score + "٪</span></td>" +
          "<td>" + (lead.source === "telegram" ? "تلگرام" : "سایت") + "</td>" +
          "<td>" + fmtTime(lead.created_at) + "</td>";
        rows.appendChild(tr);
      });

      document.getElementById("updated").textContent = "آخرین به‌روزرسانی: " + fmtTime(new Date().toISOString());
    } catch (err) {
      console.error(err);
      document.getElementById("updated").textContent = "خطا در اتصال به سرور";
    }
  }

  document.getElementById("token-submit").addEventListener("click", function () {
    var token = document.getElementById("token-input").value.trim();
    if (!token) return;
    localStorage.setItem(TOKEN_KEY, token);
    hideTokenModal();
    load();
  });

  load();
  setInterval(load, 30000); // هر ۳۰ ثانیه
})();
</script>
</body>
</html>
