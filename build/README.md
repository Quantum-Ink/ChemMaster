# Build Instructions

## Prerequisites

1. **Go 1.21+** - https://go.dev/dl/
2. **Node.js 18+** - https://nodejs.org/
3. **Wails CLI** - `go install github.com/wailsapp/wails/v2/cmd/wails@latest`
4. **WebView2** - Windows 10/11 usually has it pre-installed

## Development

```bash
# Install dependencies
cd frontend && npm install && cd ..

# Run in dev mode (hot reload)
wails dev
```

## Production Build

```bash
# Build for Windows (hides console window)
wails build -platform windows/amd64 -ldflags "-H windowsgui"

# Output: build/bin/ChemMaster.exe
```

## Build with console (for debugging)

```bash
wails build -platform windows/amd64
```
