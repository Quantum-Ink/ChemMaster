package provider

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"time"

	"chemmaster/internal/database"
)

// ProviderType represents the type of data provider.
type ProviderType string

const (
	TypeLocal     ProviderType = "local"
	TypeAPI       ProviderType = "api"
	TypePublicWeb ProviderType = "public_web"
	TypeAuth      ProviderType = "authenticated"
)

// Provider represents a data source provider.
type Provider struct {
	Name     string       `json:"name"`
	Type     ProviderType `json:"type"`
	Enabled  bool         `json:"enabled"`
	Priority int          `json:"priority"`
	BaseURL  string       `json:"baseUrl"`
	Status   string       `json:"status"`
}

// CompoundInfo holds compound information from any provider.
type CompoundInfo struct {
	Name           string  `json:"name"`
	NameCN         string  `json:"nameCn"`
	Formula        string  `json:"formula"`
	MolecularWeight float64 `json:"molecularWeight"`
	CASNumber      string  `json:"casNumber"`
	SMILES         string  `json:"smiles"`
	Description    string  `json:"description"`
	Source         string  `json:"source"`
}

// Manager manages data providers.
type Manager struct {
	db        *database.DB
	providers []*Provider
	client    *http.Client
}

// NewManager creates a new provider manager.
func NewManager(db *database.DB) *Manager {
	m := &Manager{
		db: db,
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
	m.initProviders()
	return m
}

// initProviders initializes the default providers.
func (m *Manager) initProviders() {
	m.providers = []*Provider{
		{Name: "Local Database", Type: TypeLocal, Enabled: true, Priority: 1, Status: "ready"},
		{Name: "PubChem API", Type: TypeAPI, Enabled: true, Priority: 2, BaseURL: "https://pubchem.ncbi.nlm.nih.gov/rest/pug", Status: "ready"},
		{Name: "ChEBI API", Type: TypeAPI, Enabled: false, Priority: 3, BaseURL: "https://www.ebi.ac.uk/webservices/chebi", Status: "disabled"},
	}
}

// ListProviders returns all providers.
func (m *Manager) ListProviders() []Provider {
	result := make([]Provider, len(m.providers))
	for i, p := range m.providers {
		result[i] = *p
	}
	return result
}

// SearchCompound searches for a compound across providers.
func (m *Manager) SearchCompound(query string) ([]CompoundInfo, error) {
	// 1. Try local database first
	if m.db != nil {
		localResults, err := m.db.SearchCompounds(query)
		if err == nil && len(localResults) > 0 {
			var results []CompoundInfo
			for _, r := range localResults {
				results = append(results, CompoundInfo{
					Name:            r.Name,
					NameCN:          r.NameCN,
					Formula:         r.Formula,
					MolecularWeight: r.MolecularWeight,
					CASNumber:       r.CASNumber,
					Source:          "local",
				})
			}
			return results, nil
		}
	}

	// 2. Try cache
	if m.db != nil {
		if cached, ok := m.db.CacheGet("compound:" + query); ok {
			var results []CompoundInfo
			if json.Unmarshal([]byte(cached), &results) == nil {
				return results, nil
			}
		}
	}

	// 3. Try PubChem API
	results, err := m.searchPubChem(query)
	if err != nil {
		log.Printf("PubChem search error: %v", err)
	} else if len(results) > 0 {
		// Cache results
		if m.db != nil {
			data, _ := json.Marshal(results)
			m.db.CacheSet("compound:"+query, string(data), "pubchem", 86400)
		}
		return results, nil
	}

	return nil, fmt.Errorf("no results found for '%s'", query)
}

// PubChemResponse represents a PubChem API response.
type PubChemResponse struct {
	PropertyTable struct {
		Properties []struct {
			CID          int     `json:"CID"`
			MolecularFormula string `json:"MolecularFormula"`
			MolecularWeight  float64 `json:"MolecularWeight"`
			IUPAC㎎    string  `json:"IUPACName"`
			CAN          string  `json:"CanonicalSMILES"`
		} `json:"Properties"`
	} `json:"PropertyTable"`
}

// searchPubChem searches the PubChem API.
func (m *Manager) searchPubChem(query string) ([]CompoundInfo, error) {
	// Try name search
	url := fmt.Sprintf("%s/compound/name/%s/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON",
		m.providers[1].BaseURL, strings.ReplaceAll(query, " ", "%20"))

	resp, err := m.client.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("PubChem returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var pubchemResp PubChemResponse
	if err := json.Unmarshal(body, &pubchemResp); err != nil {
		return nil, err
	}

	var results []CompoundInfo
	for _, prop := range pubchemResp.PropertyTable.Properties {
		results = append(results, CompoundInfo{
			Name:            prop.IUPACName,
			Formula:         prop.MolecularFormula,
			MolecularWeight: prop.MolecularWeight,
			SMILES:          prop.CAN,
			Source:          "pubchem",
		})
	}

	return results, nil
}

// TestConnection tests a provider's connectivity.
func (m *Manager) TestConnection(name string) (string, error) {
	for _, p := range m.providers {
		if p.Name == name {
			if p.Type == TypeLocal {
				return "Local database connected", nil
			}
			if p.BaseURL == "" {
				return "No URL configured", nil
			}
			resp, err := m.client.Get(p.BaseURL)
			if err != nil {
				return "Connection failed: " + err.Error(), err
			}
			resp.Body.Close()
			return fmt.Sprintf("Connected (status %d)", resp.StatusCode), nil
		}
	}
	return "", fmt.Errorf("provider '%s' not found", name)
}
