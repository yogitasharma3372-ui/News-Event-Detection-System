# Troubleshooting and Operational Guide

## 1. Common Issues and Resolutions

### Issue: "No module named 'backend'" when running pytest
- **Cause**: Python does not automatically add the root workspace directory to `sys.path`.
- **Resolution**: `pytest.ini` has been added to the root directory with `pythonpath = .`. Always run pytest from the repository root:
  ```powershell
  .\.venv\Scripts\pytest -v
  ```

### Issue: Hugging Face Model Download Warning or Symlink Error on Windows
- **Cause**: Windows requires Developer Mode or Administrator privileges for NTFS symlinks.
- **Resolution**: The system automatically configures `os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"` and `os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"`. Files are cached directly as standard `.npy` and `.safetensors` files without requiring symlinks.

### Issue: Live NewsAPI returns error
- **Cause**: NewsAPI requires a valid user API key from [newsapi.org](https://newsapi.org).
- **Resolution**: In the frontend, navigate to **Settings** and enter your `NewsAPI Secret Key`, or add `NEWSAPI_KEY=your_key` to `.env`. Note that open RSS feeds (BBC, NPR, Phys.org) and local CSV/JSON dataset uploads work 100% offline without any API key.

### Issue: Port 8000 or 5173 is already in use
- **Resolution**: You can specify alternate ports in `.env` or run uvicorn on an alternate port:
  ```powershell
  .\.venv\Scripts\uvicorn backend.app.main:app --port 8080 --reload
  ```
  And update `frontend/vite.config.ts` proxy target accordingly.
