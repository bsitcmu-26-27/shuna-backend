# shuna-backend

for CMU BSIT 26-27 Website booth backend

# To-Dos

## Cloudflare Turnstile (replaces booth passcode — open posting, bot-filtered)
- [x] Sign up for Cloudflare Turnstile, create a widget, get Site Key + Secret Key
- [ ] Backend: add `requests` to `requirements.txt`
- [ ] Backend: add `require_captcha` decorator (calls Turnstile's `siteverify` endpoint)
- [ ] Backend: apply `@require_captcha` to `POST /posts` (replacing the passcode check)
- [ ] Backend: add `TURNSTILE_SECRET_KEY` to `config.py` and as a Koyeb env var
- [ ] Front-end (`index.html`): load `https://challenges.cloudflare.com/turnstile/v0/api.js`
- [ ] `post-composer.tsx`: swap passcode state/input for a rendered Turnstile widget + `captchaToken` state
- [ ] `post-composer.tsx`: reset the Turnstile widget after a successful post (tokens are single-use)
- [ ] `wall-provider.tsx`: rename `addPost`'s second argument from `passcode` to `captchaToken`, form field to `captcha_token`
- [ ] Set `VITE_TURNSTILE_SITE_KEY` in `.env` / build secrets
- [ ] `shuna-backend/index.html` (admin/test page): swap passcode input for a Turnstile widget too, update submit handler to send `captcha_token`
- [ ] *(optional, still flagged from earlier)* Fix admin page's "Save position" button — still points at `/posts/<id>` instead of `/posts/<id>/position`
- [ ] *(optional, still flagged from earlier)* Fix admin page's mod buttons — not sending `X-API-Key`, will 401 against a live backend

## Subpath deployment fix (`/ufd-26-freedom-wall/`)
- [x] `vite.config.ts`: set `base` so built asset URLs resolve under the subpath instead of root
- [x] `src/router.tsx`: set `basepath` on `createRouter(...)` to match — this is the one that actually fixes the "header loads, content 404s" symptom
- [x] Rebuild, redeploy, confirm both local dev (`localhost:5173/ufd-26-freedom-wall/`) and the live GitHub Pages URL load correctly
- [x] Add `cp dist/index.html dist/404.html` to the build/publish step, so refreshing on a non-root route (e.g. `/canvas`) doesn't hit GitHub Pages' real 404

## `PUBLIC_URL_ROOT` — reusable config for future booths
- [x] `vite.config.ts`: read `PUBLIC_URL_ROOT` from `process.env`, derive `base` and `build.outDir` from it
- [x] `vite.config.ts`: `define: { __PUBLIC_URL_ROOT__: ... }` to expose the value to client code
- [x] `src/router.tsx`: use `__PUBLIC_URL_ROOT__` for `basepath` instead of a hardcoded string
- [x] `src/vite-env.d.ts`: `declare const __PUBLIC_URL_ROOT__: string;` so TypeScript doesn't complain
- [x] `vite.config.ts`: throw a clear error if `PUBLIC_URL_ROOT` is unset/empty, so a forgotten flag fails loudly instead of silently building broken asset paths
- [x] Confirm the actual build command in use: `PUBLIC_URL_ROOT=ufd-26-freedom-wall npm run build` (plain env var, not `npm run build --public_url_root=...` — that one triggers an npm deprecation warning and shouldn't be relied on)
- [ ] *(only if a Windows contributor ever joins)* add `cross-env` so the env-var syntax works outside Linux/macOS shells too

## Still-open from earlier, unrelated to the above but never confirmed fixed
- [x] `config.py`'s `check()` function prints all secrets (DB URL, admin key, S3 keys) in plaintext on every startup — worth removing or gating before relying on Koyeb's logs being private
