# CapiDOFChat frontend

For production on this computer, run `scripts/Start-Local.ps1` from the repository
root and open <http://localhost:8080>. Nginx serves the compiled assets and forwards
API requests to the local backend. Fonts and icons do not require external CDNs.

Install the locked dependencies and start the development server:

```sh
npm ci
npm run dev
```

Use `npm run lint` to validate the source and `npm run build` to create a production build. Use `npm run preview` to inspect that build locally. Generated files are excluded from version control.
