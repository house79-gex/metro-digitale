# Build Instructions

## Prerequisites

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Build Windows Executable

### Using PyInstaller with spec file:

```bash
pyinstaller build.spec
```

Output will be in `dist/MetroDigitaleConfigurator.exe`

### Alternative - Single command:

```bash
pyinstaller --onefile --windowed --name="MetroDigitaleConfigurator" main.py
```

### With Console (for debugging):

```bash
pyinstaller --onefile --console --name="MetroDigitaleConfigurator_Debug" main.py
```

## Build Linux/macOS

Same commands work on Linux/macOS:

```bash
pyinstaller build.spec
```

Output: `dist/MetroDigitaleConfigurator` (Linux) or `dist/MetroDigitaleConfigurator.app` (macOS)

## Testing Build

After building, test the executable:

**Windows:**
```cmd
dist\MetroDigitaleConfigurator.exe
```

**Linux:**
```bash
./dist/MetroDigitaleConfigurator
```

**macOS:**
```bash
open dist/MetroDigitaleConfigurator.app
```

## Troubleshooting

### Missing dependencies

If the exe fails to start, try rebuilding with console output to see errors:

```bash
pyinstaller --onefile --console main.py
```

### Missing Qt plugins

Add to build.spec if needed:

```python
datas += [
    ('path/to/Qt6/plugins', 'PyQt6/Qt6/plugins'),
]
```

### Large file size

To reduce size:
- Use UPX compression (enabled by default)
- Exclude unused modules in build.spec
- Use `--exclude-module` flag

Example:
```bash
pyinstaller --exclude-module matplotlib --exclude-module numpy build.spec
```

## Distribution

After successful build:

1. Test executable on clean Windows VM
2. Create installer with Inno Setup or NSIS (optional)
3. Sign executable with code signing certificate (recommended for production)
4. Distribute via:
   - GitHub Releases
   - Direct download
   - Windows Store (advanced)

## Build Size Estimates

- Without optimization: ~80-120 MB
- With UPX compression: ~50-80 MB
- With advanced optimization: ~30-50 MB

## Notes

- First run may trigger Windows Defender (unsigned exe)
- Consider code signing for production builds
- Test on multiple Windows versions (10, 11)
- Include Visual C++ Redistributable if needed
