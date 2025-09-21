This project has a large `requirements.txt` of cross-platform packages and a separate
`src/windows-requirements.txt` for Windows-only packages (Win32 APIs, winrt, pycaw, etc.).

For Linux/macOS (recommended):

```bash
python -m pip install -r src/requirements.txt
```

For Windows, to install everything (including Windows-only packages):

```powershell
python -m pip install -r src/requirements.txt
python -m pip install -r src/windows-requirements.txt
```

If you prefer a single combined `requirements.txt` on Windows, apply the patch in
`WINDOWS_LIBS_DIFF.patch` to add `; sys_platform == 'win32'` markers back into
`src/requirements.txt` or simply copy the contents of `src/windows-requirements.txt` into your environment.
