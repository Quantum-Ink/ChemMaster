package chemistry

import (
	"fmt"
	"regexp"
	"strings"
)

// ReactionAST is the core data structure for a chemical reaction.
type ReactionAST struct {
	Reactants  []ReactionSpecies `json:"reactants"`
	Products   []ReactionSpecies `json:"products"`
	Reversible bool              `json:"reversible"`
	Conditions []Condition       `json:"conditions"`
	Separator  string            `json:"separator"`
}

// ReactionSpecies represents one species in a reaction.
type ReactionSpecies struct {
	Formula    string `json:"formula"`
	Coefficient int   `json:"coefficient"`
	State      string `json:"state,omitempty"`      // (s), (l), (g), (aq)
	Charge     int    `json:"charge,omitempty"`
	IsGas      bool   `json:"isGas,omitempty"`
	IsPpt      bool   `json:"isPpt,omitempty"`
}

// Condition represents a reaction condition.
type Condition struct {
	Type  string `json:"type"`  // "heat", "light", "catalyst", "temperature", "pressure", "solvent"
	Value string `json:"value"`
}

// IonicEquationResult holds the three forms of an ionic equation.
type IonicEquationResult struct {
	Molecular    string   `json:"molecular"`
	FullIonic    string   `json:"fullIonic"`
	NetIonic     string   `json:"netIonic"`
	Spectators   []string `json:"spectators"`
	ChargeOK     bool     `json:"chargeBalanced"`
	ReactantChg  int      `json:"reactantCharges"`
	ProductChg   int      `json:"productCharges"`
}

// stateRegex matches state markers like (s), (l), (g), (aq).
var stateRegex = regexp.MustCompile(`\(([sgla]q?)\)\s*$`)

// ReactionEngine provides high-level reaction processing.
type ReactionEngine struct {
	fe       *FormulaEngine
	balancer *EquationBalancer
}

// NewReactionEngine creates a new ReactionEngine.
func NewReactionEngine() *ReactionEngine {
	return &ReactionEngine{
		fe:       NewFormulaEngine(),
		balancer: NewEquationBalancer(),
	}
}

// ParseReaction parses a reaction string into a ReactionAST.
func (re *ReactionEngine) ParseReaction(input string) (*ReactionAST, error) {
	ast := &ReactionAST{}

	// Detect separator
	separators := []string{"<=>", "⇌", "⇋", "->", "→", "⟶", "="}
	var sep string
	var parts []string
	for _, s := range separators {
		if strings.Contains(input, s) {
			sep = s
			parts = strings.SplitN(input, s, 2)
			break
		}
	}
	if parts == nil {
		return nil, fmt.Errorf("no reaction separator found")
	}

	ast.Separator = sep
	ast.Reversible = sep == "<=>" || sep == "⇌" || sep == "⇋"

	// Parse conditions from above/below arrow
	// For now, parse reactants and products
	rawReactants := splitTerms(parts[0])
	rawProducts := splitTerms(parts[1])

	for _, term := range rawReactants {
		species := re.parseSpecies(term)
		ast.Reactants = append(ast.Reactants, species)
	}
	for _, term := range rawProducts {
		species := re.parseSpecies(term)
		ast.Products = append(ast.Products, species)
	}

	return ast, nil
}

// parseSpecies parses a single reaction term into a ReactionSpecies.
func (re *ReactionEngine) parseSpecies(term string) ReactionSpecies {
	term = strings.TrimSpace(term)
	s := ReactionSpecies{Coefficient: 1}

	if m := stateRegex.FindStringSubmatch(term); m != nil {
		s.State = m[1]
		term = strings.TrimSpace(term[:len(term)-len(m[0])])
	}

	// Extract arrow markers (↑, ↓)
	if strings.HasSuffix(term, "↑") {
		s.IsGas = true
		term = strings.TrimSuffix(term, "↑")
	}
	if strings.HasSuffix(term, "↓") {
		s.IsPpt = true
		term = strings.TrimSuffix(term, "↓")
	}

	// Extract coefficient
	coeff, formula := re.balancer.extractCoeff(term)
	s.Coefficient = coeff
	s.Formula = formula

	return s
}

// ProcessEquation is the high-level API for processing a chemical equation.
func (re *ReactionEngine) ProcessEquation(equation string) map[string]interface{} {
	result := make(map[string]interface{})
	result["original"] = equation

	// Balance
	balanceResult := re.balancer.Balance(equation)
	result["balanced"] = balanceResult.Balanced
	result["isBalanced"] = balanceResult.IsBalanced
	result["coefficients"] = balanceResult.Coefficients
	result["subscript"] = balanceResult.Subscript
	result["latex"] = balanceResult.Latex
	result["elements"] = balanceResult.Elements
	if balanceResult.Error != "" {
		result["error"] = balanceResult.Error
	}

	// Parse AST
	ast, err := re.ParseReaction(equation)
	if err == nil {
		result["ast"] = ast
	}

	return result
}
