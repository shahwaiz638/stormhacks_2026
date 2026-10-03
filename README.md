# stormhacks_2026 monorepo foundation

Theme-agnostic starter monorepo for a hackathon web app with:
- **client/**: React + Vite + Tailwind CSS frontend
- **gateway/**: Node.js + Express API gateway
- **ai-service/**: Python + FastAPI AI agent service

## 1) Prerequisites
- Node.js 20+
- npm 10+
- Python 3.10+

## 2) Install dependencies
From repository root:

```bash
npm install
npm --prefix client install
npm --prefix gateway install
python -m pip install -r ai-service/requirements.txt
```

## 3) Configure environment variables
Copy each service template and fill values as needed:

```bash
cp client/.env.example client/.env
cp gateway/.env.example gateway/.env
cp ai-service/.env.example ai-service/.env
```

## 4) Run all services concurrently
From repository root:

```bash
npm run dev
```

Default local ports:
- Frontend (Vite): `5173`
- Gateway (Express): `4000`
- AI service (FastAPI): `8000`

## 5) Run services individually (optional)

```bash
npm run dev:client
npm run dev:gateway
npm run dev:ai
```

## 6) Health checks
- Gateway: `GET http://localhost:4000/health`
- AI service: `GET http://localhost:8000/health`
