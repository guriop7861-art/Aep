# AEP Downgrader

A web interface for detecting and downgrading Adobe After Effects `.aep` project header versions.

**Owner & Developer:** Ravi  
**Telegram:** @RAVIOXY

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```

The included `Procfile` and `render.yaml` are already configured for deployment.

## Automatic file cleanup

After a successful downgrade/download response is closed, the temporary folder containing the uploaded and converted AEP files is scheduled for automatic deletion after **5 minutes**.

This cleanup is in-memory on the running server. A Render restart/redeploy can remove ephemeral files earlier.

## Important

The conversion method changes the AEP header version byte. Backward compatibility is not guaranteed for every project, especially projects using newer features, plugins, expressions, or unsupported project data.
