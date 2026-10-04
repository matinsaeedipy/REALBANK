# SimBank · سیم‌بانک

**فارسی** · [English](#english)

شبیه‌ساز بانک با Django؛ دوزبانه (فارسی و English)، با انتقال پول فرضی بین کاربران، رمز تراکنش، رسید و تاریخچه. فقط برای آموزش است و پول واقعی در کار نیست.

## امکانات
- ثبت‌نام با شماره حساب ۱۰ رقمی و موجودی اولیه‌ی فرضی
- انتقال دومرحله‌ای: ثبت اطلاعات، سپس تأیید با رمز تراکنش ۴ رقمی
- سقف هر انتقال و سقف روزانه، جلوگیری از تراکنش تکراری، دفتر کل تغییرناپذیر
- قفل موقت بعد از ورود یا رمز تراکنش اشتباه، خروج خودکار بعد از ۱۵ دقیقه
- هدرهای امنیتی (CSP و ...)، کوکی‌های امن، CSRF
- تم روشن/تیره، رابط فارسی (راست‌به‌چپ) و انگلیسی با دکمه‌ی تغییر زبان

## اجرای محلی (لینوکس، مک، Termux)
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # اختیاری
python manage.py runserver
```
آدرس: `http://127.0.0.1:8000` و پنل مدیریت: `/manage-bank-admin/`

اجرای تست‌ها:
```bash
python manage.py test bank
```

## اجرا با Docker (روی هر هاستی)
```bash
docker build -t simbank .
docker run -p 8000:8000 -e DJANGO_SECRET_KEY=یک-رشته-تصادفی-طولانی -e DJANGO_HTTPS=0 -v simbank-data:/app/data simbank
```
`DJANGO_HTTPS=0` فقط برای تست روی `http://localhost` است. روی سرور واقعی با HTTPS آن را حذف کن.

## انتشار روی justrunmy.app
1. در [justrunmy.app](https://justrunmy.app) ثبت‌نام کن و یک اپ جدید بساز.
2. روش **Zip Upload** را انتخاب کن و فایل `simbank-justrunmy.zip` را آپلود کن (یا مخزن گیت‌هاب را با Git Push بفرست). فایل `Dockerfile` پروژه خودکار استفاده می‌شود.
3. در بخش Ports یک پورت **8000** از نوع **HTTPS** اضافه کن.
4. در بخش Environment variables این‌ها را بگذار:
   - `DJANGO_SECRET_KEY` = یک رشته‌ی تصادفی طولانی (ساخت: `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
   - برای ساخت خودکار ادمین (اختیاری): `DJANGO_SUPERUSER_USERNAME` و `DJANGO_SUPERUSER_PASSWORD`
5. اپ را Start کن و لینک HTTPS را باز کن.

نکته‌ها:
- دیتابیس پیش‌فرض SQLite است و در `/app/data` ذخیره می‌شود. اگر بعد از هر Deploy دیتا پاک شد، از قالب PostgreSQL پلتفرم استفاده کن، `DATABASE_URL` را بگذار و خط `psycopg[binary]` را به `requirements.txt` اضافه کن.
- اگر هنگام ورود خطای «CSRF verification failed» دیدی، `DJANGO_CSRF_TRUSTED_ORIGINS=https://آدرس-اپ-تو` را اضافه کن.
- همه‌ی متغیرها در فایل `.env.example` توضیح داده شده‌اند.

## سایر هاست‌ها
- **هر هاستی با Docker** (Render، Railway، Fly.io، VPS و ...): از همین `Dockerfile` استفاده کن و پورت `8000` را باز کن.
- **هاست‌های مبتنی بر Procfile** (مثل Heroku): فایل `Procfile` آماده است.
- **VPS ساده**: `pip install -r requirements.txt` و بعد `sh entrypoint.sh` (متغیر `PORT` پورت را تعیین می‌کند).

## گذاشتن روی گیت‌هاب
```bash
git init
git add .
git commit -m "Initial commit: SimBank"
git branch -M main
git remote add origin https://github.com/USERNAME/simbank.git
git push -u origin main
```
فایل‌های `db.sqlite3`، `.secret_key` و `.env` در `.gitignore` هستند و هرگز آپلود نمی‌شوند.

## مجوز
MIT

---

<a id="english"></a>
# SimBank (English)

[فارسی](#simbank--سیم‌بانک) · **English**

A bilingual (Persian / English) bank simulator built with Django: fictional money transfers between users, transaction PIN, receipts and history. For education only, no real money involved.

## Features
- Sign-up with a 10-digit account number and a simulated starting balance
- Two-step transfers: enter details, then confirm with a 4-digit transaction PIN
- Per-transfer and daily limits, duplicate-submit protection, immutable ledger
- Temporary lockouts after failed logins or PINs, automatic sign-out after 15 minutes
- Security headers (CSP, etc.), secure cookies, CSRF protection
- Light/dark theme, Persian (RTL) and English UI with a language switch button

## Run locally (Linux, macOS, Termux)
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```
Open `http://127.0.0.1:8000`. Admin panel: `/manage-bank-admin/`.

Run the tests:
```bash
python manage.py test bank
```

## Run with Docker (any host)
```bash
docker build -t simbank .
docker run -p 8000:8000 -e DJANGO_SECRET_KEY=a-long-random-string -e DJANGO_HTTPS=0 -v simbank-data:/app/data simbank
```
Use `DJANGO_HTTPS=0` only to test on plain `http://localhost`. Remove it on a real HTTPS server.

## Deploy on justrunmy.app
1. Sign up at [justrunmy.app](https://justrunmy.app) and create a new app.
2. Choose **Zip Upload** and upload `simbank-justrunmy.zip` (or push the GitHub repo via Git Push). The project's `Dockerfile` is used automatically.
3. In Ports, add port **8000** of type **HTTPS**.
4. In Environment variables set:
   - `DJANGO_SECRET_KEY` = a long random string (generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
   - optional auto-created admin: `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD`
5. Start the app and open the HTTPS link.

Notes:
- The default database is SQLite stored in `/app/data`. If data disappears after a redeploy, use the platform's PostgreSQL template, set `DATABASE_URL`, and add `psycopg[binary]` to `requirements.txt`.
- If you see "CSRF verification failed" on login, add `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app-url`.
- All variables are documented in `.env.example`.

## Other hosts
- **Any Docker host** (Render, Railway, Fly.io, a VPS, ...): use the included `Dockerfile` and expose port `8000`.
- **Procfile-based hosts** (e.g. Heroku): the `Procfile` is included.
- **Plain VPS**: `pip install -r requirements.txt`, then `sh entrypoint.sh` (the `PORT` variable sets the port).

## Publish on GitHub
```bash
git init
git add .
git commit -m "Initial commit: SimBank"
git branch -M main
git remote add origin https://github.com/USERNAME/simbank.git
git push -u origin main
```
`db.sqlite3`, `.secret_key` and `.env` are in `.gitignore` and are never uploaded.

## License
MIT
