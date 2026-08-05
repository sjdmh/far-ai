=== Far AI — Chat Widget ===
Contributors: faragency
Tags: chat, ai, chatbot, customer support, far
Requires at least: 5.8
Tested up to: 6.7
Requires PHP: 7.4
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

ویجت چت هوشمند Far AI برای سایت وردپرسی آژانس فَر.

== Description ==

این پلاگین یک دکمه شناور چت به سایت شما اضافه می‌کند که گفتگوی بازدیدکننده را به
API دستیار هوشمند «Far AI» متصل می‌کند. Far AI نیاز مشتری را شناسایی می‌کند،
اطلاعات تماس را می‌گیرد و لید را به تیم آژانس اطلاع می‌دهد.

**امکانات:**
* دکمه شناور راست‌چین و واکنش‌گرا (RTL / Mobile)
* حفظ گفتگو برای هر بازدیدکننده (localStorage)
* صفحه تنظیمات کامل: آدرس API، عنوان، رنگ، پیام خوش‌آمد
* نمایش در همه صفحات یا فقط با شورت‌کد `[far_ai_chat]`
* امن (textContent — بدون XSS)

== Installation ==

1. پوشه `far-ai-chat-widget` را داخل `wp-content/plugins` کپی کنید (یا فایل ZIP را از پیشخوان وردپرس نصب کنید).
2. از پیشخوان → افزونه‌ها، افزونه «Far AI — Chat Widget» را فعال کنید.
3. به «تنظیمات → Far AI Widget» بروید و آدرس API سرور Far AI را وارد کنید.
4. ذخیره کنید. ویجت در سایت نمایش داده می‌شود.

== Frequently Asked Questions ==

= آیا بدون Backend کار می‌کند؟ =

خیر. این پلاگین یک کلاینت است؛ باید سرور Far AI (FastAPI) راه‌اندازی شده باشد.

= چطور فقط در یک صفحه نمایش دهم؟ =

در تنظیمات، گزینه «نمایش در همه صفحات» را غیرفعال کنید و شورت‌کد `[far_ai_chat]` را در صفحه موردنظر بگذارید.

== Changelog ==

= 1.0.0 =
* انتشار اولیه
