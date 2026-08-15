# AEP Downgrader

A web interface for detecting and downgrading Adobe After Effects `.aep` project header versions.

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

## Important

The conversion method changes the AEP header version byte. Backward compatibility is not guaranteed for every project, especially projects using newer features, plugins, expressions, or unsupported project data.
