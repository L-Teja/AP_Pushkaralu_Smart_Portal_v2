# AP Pushkaralu Smart Portal — starter project

A security-oriented starter for the AP Godavari Pushkaralu 2027 management portal.

## Stack
- Frontend: React + Vite
- Backend: Django + Django REST Framework
- Database: PostgreSQL (SQLite works for local development)
- Authentication: JWT foundation; Google OAuth and mobile OTP require real provider credentials.
- QR: browser-side QR display/scanning can be added using `qrcode` and `html5-qrcode`.
- Sensor ingestion: authenticated API endpoint scaffold.

## Festival configuration
Default event: Godavari Adi Pushkaralu, 26 June–7 July 2027 (12 days).
Do not assume every ghat is open. An authorized administrator must configure approved ghats, slot times and capacities based on district orders.

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
API: http://127.0.0.1:8000/api/

### 2. Frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the Vite URL shown in the terminal. The demo dashboard uses sample data until connected to the API.

## Production security checklist — mandatory before public launch
1. Use PostgreSQL, HTTPS, secure cookies, strong `SECRET_KEY`, `DEBUG=False`, strict `ALLOWED_HOSTS`.
2. Configure CORS only for the real frontend domain; never use wildcard origins with credentials.
3. Use an approved Google OAuth client and verify ID tokens server-side. Never trust a client-supplied email.
4. Use an SMS OTP provider (e.g. approved Indian DLT-compliant provider). Hash OTPs, rate-limit requests, expire codes, and prevent replay.
5. Add MFA for privileged department accounts; provision officer accounts through an authorized administrator.
6. Enforce object-level permissions on every API endpoint. Do not expose another visitor's booking or personal data.
7. Encrypt sensitive data at rest and in transit; minimize collected personal data; define retention and deletion schedules.
8. Add audit logs, backups, monitoring, vulnerability testing and incident response.
9. QR codes must contain an opaque random token, not a person's name, phone number or other personal data. Validate token server-side and make check-in idempotent.
10. Sensor alerts must be calibrated and verified against approved thresholds. Never rely on a demo threshold for real evacuation decisions. Use redundant sensors and human confirmation.
11. Emergency dispatch, CCTV/AI, drone feeds, shelters, GPS and public warning systems require agency approvals, integrations and operational procedures.
12. Conduct load, accessibility, Telugu-language, security and disaster-recovery testing before deployment.

## Demo credentials
There are no hard-coded production credentials. Create a Django superuser locally and configure department users through Django Admin. The frontend sample dashboard is illustrative only.

## Devotional background asset
The hero uses `frontend/public/pushkaralu-bg.png`. Replace it with an approved event image if required.
