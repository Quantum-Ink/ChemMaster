package plugin

import (
	"fmt"
	"log"
	"sync"
)

// Category represents a plugin category.
type Category string

const (
	CategoryParser   Category = "parser"
	CategorySolver   Category = "solver"
	CategoryDatabase Category = "database"
	CategoryExport   Category = "export"
	CategoryAI       Category = "ai"
)

// Plugin represents a ChemMaster plugin.
type Plugin struct {
	Name        string   `json:"name"`
	Version     string   `json:"version"`
	Description string   `json:"description"`
	Category    Category `json:"category"`
	Enabled     bool     `json:"enabled"`
	Initialized bool     `json:"initialized"`
	Error       string   `json:"error,omitempty"`
}

// Manager manages plugins.
type Manager struct {
	mu      sync.RWMutex
	plugins map[string]*Plugin
}

// NewManager creates a new plugin manager.
func NewManager() *Manager {
	m := &Manager{
		plugins: make(map[string]*Plugin),
	}
	// Register built-in plugins
	m.registerBuiltins()
	return m
}

// registerBuiltins registers the built-in plugins.
func (m *Manager) registerBuiltins() {
	builtins := []Plugin{
		{Name: "formula-parser", Version: "1.0.0", Description: "Chemical formula parser", Category: CategoryParser, Enabled: true, Initialized: true},
		{Name: "equation-balancer", Version: "1.0.0", Description: "Chemical equation balancer using matrix method", Category: CategorySolver, Enabled: true, Initialized: true},
		{Name: "ion-engine", Version: "1.0.0", Description: "Ionic equation analyzer", Category: CategorySolver, Enabled: true, Initialized: true},
		{Name: "latex-export", Version: "1.0.0", Description: "LaTeX export plugin", Category: CategoryExport, Enabled: true, Initialized: true},
		{Name: "png-export", Version: "1.0.0", Description: "PNG export via SVG/Canvas", Category: CategoryExport, Enabled: true, Initialized: true},
		{Name: "local-database", Version: "1.0.0", Description: "Local SQLite chemistry database", Category: CategoryDatabase, Enabled: true, Initialized: true},
		{Name: "pubchem-provider", Version: "1.0.0", Description: "PubChem API data provider", Category: CategoryDatabase, Enabled: true, Initialized: true},
	}

	for _, p := range builtins {
		plugin := p
		m.plugins[p.Name] = &plugin
	}
	log.Printf("Registered %d built-in plugins", len(builtins))
}

// ListPlugins returns all registered plugins.
func (m *Manager) ListPlugins() []Plugin {
	m.mu.RLock()
	defer m.mu.RUnlock()

	result := make([]Plugin, 0, len(m.plugins))
	for _, p := range m.plugins {
		result = append(result, *p)
	}
	return result
}

// GetPlugin returns a plugin by name.
func (m *Manager) GetPlugin(name string) (*Plugin, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	p, ok := m.plugins[name]
	if !ok {
		return nil, fmt.Errorf("plugin '%s' not found", name)
	}
	return p, nil
}

// SetEnabled enables or disables a plugin.
func (m *Manager) SetEnabled(name string, enabled bool) error {
	m.mu.Lock()
	defer m.mu.Unlock()

	p, ok := m.plugins[name]
	if !ok {
		return fmt.Errorf("plugin '%s' not found", name)
	}
	p.Enabled = enabled
	return nil
}

// GetPluginsByCategory returns plugins filtered by category.
func (m *Manager) GetPluginsByCategory(category Category) []Plugin {
	m.mu.RLock()
	defer m.mu.RUnlock()

	var result []Plugin
	for _, p := range m.plugins {
		if p.Category == category {
			result = append(result, *p)
		}
	}
	return result
}
