package app

import (
	"chemmaster/internal/chemistry"
	"chemmaster/internal/plugin"
	"chemmaster/internal/provider"
)

// ============================================================
// Formula API
// ============================================================

// ParseFormula parses a chemical formula and returns element counts, molecular weight, etc.
func (a *App) ParseFormula(formula string) chemistry.FormulaResult {
	return a.formulaEng.Parse(formula)
}

// ============================================================
// Equation Balancer API
// ============================================================

// BalanceEquation balances a chemical equation.
func (a *App) BalanceEquation(equation string) chemistry.BalanceResult {
	return a.balancer.Balance(equation)
}

// ============================================================
// Reaction Engine API
// ============================================================

// ProcessEquation processes a chemical equation with full analysis.
func (a *App) ProcessEquation(equation string) map[string]interface{} {
	return a.reactionEng.ProcessEquation(equation)
}

// ============================================================
// Ion Engine API
// ============================================================

// AnalyzeIons converts a molecular equation to ionic forms.
func (a *App) AnalyzeIons(equation string) (*chemistry.IonicEquationResult, error) {
	return a.ionEng.Analyze(equation)
}

// BalanceIonEquation balances an ionic equation.
func (a *App) BalanceIonEquation(equation string) chemistry.BalanceResult {
	return a.ionEng.BalanceIonEquation(equation)
}

// ParseIon parses an ion string into an Ion struct.
func (a *App) ParseIon(ionStr string) chemistry.Ion {
	return a.ionEng.ParseIon(ionStr)
}

// ============================================================
// Renderer API
// ============================================================

// RenderFormula renders a formula in multiple formats.
func (a *App) RenderFormula(formula string) chemistry.RenderResult {
	return a.renderer.RenderFormula(formula)
}

// RenderEquation renders an equation in multiple formats.
func (a *App) RenderEquation(equation string) chemistry.RenderResult {
	return a.renderer.RenderEquation(equation)
}

// ============================================================
// Database API
// ============================================================

// GetElement queries an element by symbol.
func (a *App) GetElement(symbol string) interface{} {
	if a.db == nil {
		return map[string]string{"error": "database not initialized"}
	}
	elem, err := a.db.GetElement(symbol)
	if err != nil {
		return map[string]string{"error": err.Error()}
	}
	return elem
}

// SearchElements searches elements by name or symbol.
func (a *App) SearchElements(query string) interface{} {
	if a.db == nil {
		return []interface{}{}
	}
	results, err := a.db.SearchElements(query)
	if err != nil {
		return map[string]string{"error": err.Error()}
	}
	return results
}

// GetAllElements returns all elements from the database.
func (a *App) GetAllElements() interface{} {
	if a.db == nil {
		return []interface{}{}
	}
	results, err := a.db.GetAllElements()
	if err != nil {
		return map[string]string{"error": err.Error()}
	}
	return results
}

// SearchCompounds searches compounds by name or formula.
func (a *App) SearchCompounds(query string) interface{} {
	if a.db == nil {
		return []interface{}{}
	}
	results, err := a.db.SearchCompounds(query)
	if err != nil {
		return map[string]string{"error": err.Error()}
	}
	return results
}

// ============================================================
// Provider API
// ============================================================

// ListProviders returns all data providers.
func (a *App) ListProviders() []provider.Provider {
	return a.providerMgr.ListProviders()
}

// SearchCompoundOnline searches for a compound across all providers.
func (a *App) SearchCompoundOnline(query string) ([]provider.CompoundInfo, error) {
	return a.providerMgr.SearchCompound(query)
}

// SetProviderEnabled enables or disables a provider.
func (a *App) SetProviderEnabled(name string, enabled bool) error {
	return a.providerMgr.SetProviderEnabled(name, enabled)
}

// TestProviderConnection tests a provider's connectivity.
func (a *App) TestProviderConnection(name string) (string, error) {
	return a.providerMgr.TestConnection(name)
}

// ============================================================
// Plugin API
// ============================================================

// ListPlugins returns all registered plugins.
func (a *App) ListPlugins() []plugin.Plugin {
	return a.pluginMgr.ListPlugins()
}

// SetPluginEnabled enables or disables a plugin.
func (a *App) SetPluginEnabled(name string, enabled bool) error {
	return a.pluginMgr.SetEnabled(name, enabled)
}

// ============================================================
// Settings API
// ============================================================

// GetSetting retrieves a setting value.
func (a *App) GetSetting(key string) string {
	if a.db == nil {
		return ""
	}
	val, _ := a.db.GetSetting(key)
	return val
}

// SetSetting stores a setting value.
func (a *App) SetSetting(key, value string) error {
	if a.db == nil {
		return nil
	}
	return a.db.SetSetting(key, value)
}
