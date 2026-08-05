/**
 * Far AI — Chat Widget (JavaScript)
 * دکمه شناور + پنل چت + میانبرهای خدمات + اتصال به API Far AI
 * هویت بصری: آژانس تبلیغاتی فَر 🦚
 */
(function () {
	"use strict";

	if (!window.FarAIConfig || !FarAIConfig.apiUrl) {
		console.warn("Far AI: تنظیمات API یافت نشد.");
		return;
	}

	var CONFIG = window.FarAIConfig;
	var SESSION_KEY = "far_ai_session_id";
	var sessionId = localStorage.getItem(SESSION_KEY) || null;

	// میانبرهای خدمات — بر اساس منوی خدمات سایت فَر
	var SERVICES = [
		"🎨 طراحی لوگو",
		"🪶 هویت بصری",
		"📸 عکاسی تبلیغاتی",
		"🎬 تیزر و ویدیو",
		"🛑 استاپ موشن",
		"🎓 دوره آموزش گرافیک",
	];

	// ── ساختار DOM ──────────────────────────────────────────
	var root = document.getElementById("far-ai-widget-root") || document.body;
	var style = document.createElement("style");
	style.textContent = ":root{--far-ai-accent:" + (CONFIG.accentColor || "#FF7A29") + ";}";
	document.head.appendChild(style);

	var widget = document.createElement("div");
	widget.className = "far-ai-widget";
	widget.innerHTML =
		'<button id="far-ai-toggle" class="far-ai-toggle" aria-label="چت با Far AI">' +
		'<span class="far-ai-toggle-icon">🦚</span>' +
		"</button>" +
		'<div id="far-ai-panel" class="far-ai-panel" hidden>' +
		'<div class="far-ai-header">' +
		'<div class="far-ai-avatar">🦚</div>' +
		'<div class="far-ai-header-text"><strong></strong><span>آنلاین — پاسخ فوری</span></div>' +
		'<button id="far-ai-close" class="far-ai-close" aria-label="بستن">✕</button>' +
		"</div>" +
		'<div id="far-ai-chips" class="far-ai-chips"></div>' +
		'<div id="far-ai-messages" class="far-ai-messages"></div>' +
		'<form id="far-ai-form" class="far-ai-form">' +
		'<input id="far-ai-input" type="text" autocomplete="off" />' +
		'<button type="submit" class="far-ai-send">➤</button>' +
		"</form>" +
		"</div>";

	root.appendChild(widget);

	var toggle = document.getElementById("far-ai-toggle");
	var panel = document.getElementById("far-ai-panel");
	var close = document.getElementById("far-ai-close");
	var messagesEl = document.getElementById("far-ai-messages");
	var chipsEl = document.getElementById("far-ai-chips");
	var form = document.getElementById("far-ai-form");
	var input = document.getElementById("far-ai-input");
	var titleEl = widget.querySelector(".far-ai-header-text strong");

	titleEl.textContent = CONFIG.widgetTitle || "دستیار فَر";
	input.placeholder = CONFIG.placeholder || "پیام خود را بنویسید...";

	var typing = false;

	// ── میانبرهای خدمات ─────────────────────────────────────
	SERVICES.forEach(function (service) {
		var chip = document.createElement("button");
		chip.type = "button";
		chip.className = "far-ai-chip";
		chip.textContent = service;
		chip.addEventListener("click", function () {
			chipsEl.style.display = "none";
			sendMessage(service);
		});
		chipsEl.appendChild(chip);
	});

	// ── توابع کمکی ──────────────────────────────────────────
	function addMessage(text, role) {
		var row = document.createElement("div");
		row.className = "far-ai-msg far-ai-msg--" + (role === "user" ? "user" : "bot");

		var bubble = document.createElement("div");
		bubble.className = "far-ai-bubble";
		bubble.textContent = text; // textContent = ضد XSS
		row.appendChild(bubble);
		messagesEl.appendChild(row);
		messagesEl.scrollTop = messagesEl.scrollHeight;
		return row;
	}

	function showTyping() {
		typing = true;
		var row = document.createElement("div");
		row.className = "far-ai-msg far-ai-msg--bot";
		row.id = "far-ai-typing";
		row.innerHTML = '<div class="far-ai-bubble far-ai-typing"><span></span><span></span><span></span></div>';
		messagesEl.appendChild(row);
		messagesEl.scrollTop = messagesEl.scrollHeight;
	}

	function hideTyping() {
		typing = false;
		var el = document.getElementById("far-ai-typing");
		if (el) el.remove();
	}

	// ── گفتگو با Backend ────────────────────────────────────
	async function sendMessage(text) {
		addMessage(text, "user");
		showTyping();

		var payload = { message: text, source: "website" };
		if (sessionId) payload.session_id = sessionId;

		try {
			var res = await fetch(CONFIG.apiUrl, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			});

			if (!res.ok) throw new Error("HTTP " + res.status);

			var data = await res.json();
			if (data.session_id) {
				sessionId = data.session_id;
				localStorage.setItem(SESSION_KEY, sessionId);
			}
			hideTyping();
			addMessage(data.answer || "…", "bot");
		} catch (err) {
			console.error("Far AI error:", err);
			hideTyping();
			addMessage("یه لحظه مشکل دارم 🙏 لطفاً دوباره تلاش کن یا با ما تماس بگیر: ۰۲۱۹۱۰۹۲۰۷۳", "bot");
		}
	}

	// ── رویدادها ────────────────────────────────────────────
	toggle.addEventListener("click", function () {
		var isHidden = panel.hasAttribute("hidden");
		panel.toggleAttribute("hidden");
		toggle.classList.toggle("far-ai-toggle--open", !isHidden);
		if (isHidden && messagesEl.children.length === 0) {
			addMessage(CONFIG.welcomeMessage || "سلام 👋 چطور می‌تونم کمکت کنم؟", "bot");
		}
		if (!isHidden) input.focus();
	});

	close.addEventListener("click", function () {
		panel.toggleAttribute("hidden", true);
		toggle.classList.remove("far-ai-toggle--open");
	});

	form.addEventListener("submit", function (e) {
		e.preventDefault();
		var text = input.value.trim();
		if (!text || typing) return;
		input.value = "";
		chipsEl.style.display = "none";
		sendMessage(text);
	});
})();
