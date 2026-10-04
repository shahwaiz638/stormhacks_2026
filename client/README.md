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

Vite proxies `/api` to `VITE_GATEWAY_URL`, defaulting to `http://localhost:4000`. See `.env.example`. `src/App.jsx` is an empty app shell ready for building LostLens section by section. The generated home page, agent playground, navigation, and chat component have been removed. React Router remains available through the existing `BrowserRouter` wrapper.

## UI components

shadcn/ui is configured for JavaScript, the New York style, Neutral colors, and Tailwind CSS 3. Components belong in `src/components/ui`; `@/` resolves to `src/` in both Vite and the editor. Use `cn` from `@/lib/utils` to merge classes.

Use the Tailwind 3-compatible CLI when adding components:

```sh
npx shadcn@2.3.0 add button
```

Theme tokens live in `src/index.css`, with matching utilities in `tailwind.config.js`. The root uses the `dark` class to preserve the starter's dark appearance; remove it to use the light tokens.

## Lost item submission

The form at `/report/lost` prepares a multipart POST using `src/lib/reports.js`. Set `VITE_LOST_REPORT_API_URL` in your local environment when the backend endpoint is ready, then restart Vite. An empty endpoint sends no request. Fields are `itemName`, `description`, `category` (when available), `lastSeenLocation`, `lastSeenAt` (local date/time), `timeZone`, `privateDetail`, and optional `photo`. The browser supplies the multipart content type and boundary. Category records will be connected later in `src/pages/LostReportPage.jsx`.

