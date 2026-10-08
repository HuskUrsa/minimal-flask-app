# minimal-flask-app
Minimal code for a Flask app making calls to the OpenAI API.

You need Python 3 installed. Run the commands below from inside the project folder.


## macOS / Linux

```bash
# Create virtual environment
python3 -m venv ./venv

# Activate your virtual environment
source venv/bin/activate

# Install the required packages
pip3 install flask openai python-dotenv gunicorn

# Rename the file .env-bup to .env
mv .env-bup .env
# Then open .env and add your OPENAI_API_KEY

# Run the app
python3 app.py
```

## Windows (PowerShell)

```powershell
# Create virtual environment
python -m venv venv

# Activate your virtual environment
.\venv\Scripts\Activate.ps1

# Install the required packages
pip install flask openai python-dotenv gunicorn

# Rename the file .env-bup to .env
Rename-Item .env-bup .env
# Then open .env and add your OPENAI_API_KEY

# Run the app
python app.py
```

Notes for Windows:

- If `python` is not recognised, use `py` instead (for example, `py -m venv venv` and `py app.py`).
- If PowerShell says that running scripts is disabled, run this once and try the activation again:
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`
- With Command Prompt (cmd) instead of PowerShell, activate with `venv\Scripts\activate.bat` and rename with `ren .env-bup .env`.
- `gunicorn` installs on Windows but cannot run there. It is only needed when deploying (for example, on Render), so locally always start the app with `python app.py`.

## Which terminal am I using?

Use a **Linux-style shell** if you can: the commands are the same on every platform, which makes it easier to follow tutorials and to get help.

- **macOS / Linux:** the built-in Terminal already is one. Use the *macOS / Linux* commands below.
- **Windows, recommended:** install [Git for Windows](https://git-scm.com/download/win), which includes **Git Bash**, or install **WSL** (Windows Subsystem for Linux) by running `wsl --install` in PowerShell. Both give you Linux-style commands.
  - In **WSL**, use the *macOS / Linux* commands exactly as written.
  - In **Git Bash**, use the *macOS / Linux* commands, with two changes: use `python` instead of `python3`, and activate with `source venv/Scripts/activate`.
- **Windows, default:** the terminal in VS Code opens **PowerShell** by default (the prompt starts with `PS C:\...`). If you stay with it, use the *Windows (PowerShell)* commands below.

In VS Code, the dropdown next to the `+` in the terminal panel shows which shell is open and lets you pick another one (Git Bash and WSL appear there once installed).

## Check that it works

When the virtual environment is active, `(venv)` appears at the start of your prompt. After `python app.py` (or `python3 app.py`), open <http://127.0.0.1:5000> in your browser.

VS Code may show a message saying that an environment file is configured but terminal environment injection is disabled (`python.terminal.useEnvFile`). That is fine: the app loads `.env` by itself, so you can ignore the message and leave the setting off.

## Deploying on Render

- **Build command:** `pip install flask openai python-dotenv gunicorn`
- **Start command:** `gunicorn app:app`
- **Environment variable:** `OPENAI_API_KEY` = your key. Never commit your key to GitHub.

If the deploy fails with `gunicorn: command not found` (status 127), `gunicorn` is missing from the build command. If it fails with `No module named 'openai'`, `openai` is missing.

### If Render times out

If requests time out (the logs may show `WORKER TIMEOUT`), for example when the OpenAI call is slow, add the `--timeout` parameter to the `gunicorn` line in the Render configuration. gunicorn stops a request after 30 seconds by default, and this raises the limit to 240 seconds:

- **Start command:** `gunicorn app:app --timeout 240`

## Paired studio interface

One central prompt makes a text response and a companion image. Expand Generation settings to edit the system prompt, text model, temperature, response limit, and image look. The image model remains GPT Image 1 Mini, low quality, 1024 square. The Early AI look is a prompt treatment, not an older model.

Results append without page navigation. IndexedDB preserves paired and earlier single-media entries in the same browser; history is not synced between devices or origins. Text and image downloads remain available. If the image call fails, completed text is kept with the error. Settings persist locally.

The shared five-image allowance resets on server restart and is not an account billing limit. Failed image calls consume an attempt. There are no automatic provider retries. Each provider call has a 110-second timeout, keeping the two-call path within the configured 240-second worker timeout.

Original hero artwork: `static/art/red-membrane.jpg`; generation prompt/provenance in `static/art/provenance.json`. The image is decorative artwork, not a live generation sample. No custom cursor or pointer-reactive effects. FT Overpass is loaded from an installed licensed copy when present, otherwise Arial; no font binaries are redistributed. Calder identity is outlined SVG.

Regression checks (mocked, no API charges):

```bash
python -m unittest discover -s tests -v
```

### Minimal motion workspace

Headline and tagline removed at Sam’s request. The composer and expandable settings lead the first viewport. Ambient particles sit behind opaque controls; the native cursor remains. Motion can be paused and respects reduced-motion and hidden-tab states. The background is an original free Hugging Face MiniMax-H3 / Larry Turbo LoRA generation, processed into a silent forward-only 4.46-second loop with a short cross-dissolve at the seam. Source, prompt and processing provenance: `static/art/background-provenance.json`. Video and poster are served locally by Flask; no Hugging Face calls run for visitors.
