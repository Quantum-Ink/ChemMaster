.PHONY: dev build frontend clean

# Development
dev:
	wails dev

# Build production
build: frontend
	wails build -platform windows/amd64 -ldflags "-H windowsgui"

# Build with console (for debugging)
build-debug: frontend
	wails build -platform windows/amd64

# Frontend only
frontend:
	cd frontend && npm install && npm run build

# Clean build artifacts
clean:
	rm -rf build/bin frontend/dist frontend/node_modules

# Run Go tests
test:
	go test ./...
