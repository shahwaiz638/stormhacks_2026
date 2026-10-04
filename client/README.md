# Frontend

Existing React 19 + Vite JavaScript app with React Router, Tailwind CSS 3, PostCSS, and Oxlint.

## Development

Use Node.js 22.12+ (or 20.19+) and npm.

```sh
npm install
npm run dev
npm run build
npm run lint
```

Run FastAPI from `backend/` with `python main.py` and Vite from `client/` with `npm run dev`. Open `http://localhost:5173`. Both servers bind to `0.0.0.0`. Other devices can open `http://<computer-LAN-IP>:5173`; the client uses that same hostname on port 8000 for the API. `VITE_API_URL` optionally overrides the API URL. No gateway is used.

## UI components

shadcn/ui is configured for JavaScript, the New York style, Neutral colors, and Tailwind CSS 3. Components belong in `src/components/ui`; `@/` resolves to `src/` in both Vite and the editor. Use `cn` from `@/lib/utils` to merge classes.

Use the Tailwind 3-compatible CLI when adding components:

```sh
npx shadcn@2.3.0 add button
```

Theme tokens live in `src/index.css`, with matching utilities in `tailwind.config.js`. The root uses the `dark` class to preserve the starter's dark appearance; remove it to use the light tokens.

## Report submission

`/report/lost` posts JSON to `http://<frontend-hostname>:8000/reports/lost`; `/report/found` posts to `/reports/found`. Fields are `title` (lost form), `description`, `location_name`, `event_timestamp`, `time_zone`, and `images`, an array of Base64 data URLs. Found reports require a photo; lost photos are optional. Uploads accept up to five JPEG/PNG/WebP photos, 5 MiB each. The location limit is 100 characters.

The backend owns Gemini instructions and validates the photos and structured attributes before storing FOUND reports and 768-dimensional text embeddings in TiDB. LOST submissions are read-only searches: vector retrieval gets five FOUND candidates, then Gemini rejects incompatible types and selects at most two plausible matches. No LOST row is inserted. If Gemini evaluation fails, the API returns an error instead of unvetted matches. The frontend and backend apply a basic instruction-pattern guard; it is not a guarantee against prompt injection. Private identifying details are not stored or sent to Gemini because the table has no private-detail column.

The submit button spins while processing. A shadcn-style alert reports success/failure; matches appear automatically below the form with photos. Expand Processing details for IDs, extracted attributes, vector/AI scores, and notices. Credentials belong only in `backend/.env`.
