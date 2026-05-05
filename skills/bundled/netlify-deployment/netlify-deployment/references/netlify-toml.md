# `netlify.toml` 快速規則

```toml
[build]
  command = "npm run build"
  publish = "dist"
```

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```
