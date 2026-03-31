# Python Virtual Environment Setup (PowerShell)

## 1) Install pyenv-win

Run in PowerShell:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Then close and reopen PowerShell.

## 2) Install and select Python 3.10

```powershell
pyenv install 3.10
pyenv global 3.10
```

## 3) Install project dependencies

In project root (`d:\soft\AutoGUI_project`):

```powershell
pip install -r requirements.txt
```

## 4) Run Python Desktop App

```powershell
python main.py
```

## Optional: Create a local venv (recommended)

If you want project-level isolation in addition to pyenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
