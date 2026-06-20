package chemistry

import (
	"fmt"
	"strings"
	"unicode"

	"chemmaster/internal/database"
)

// ElementData holds information about a chemical element.
type ElementData struct {
	Symbol       string
	NameEN       string
	NameCN       string
	AtomicNumber int
	AtomicMass   float64
}

// PeriodicTable is built from database.AllElements at init time.
var PeriodicTable map[string]ElementData

func init() {
	PeriodicTable = make(map[string]ElementData, len(database.AllElements))
	for _, e := range database.AllElements {
		PeriodicTable[e.Symbol] = ElementData{
			Symbol:       e.Symbol,
			NameEN:       e.NameEN,
			NameCN:       e.NameCN,
			AtomicNumber: e.AtomicNumber,
			AtomicMass:   e.AtomicMass,
		}
	}
}

// SubscriptDigits maps digits to Unicode subscript characters.
var SubscriptDigits = map[byte]string{
	'0': "₀", '1': "₁", '2': "₂", '3': "₃", '4': "₄",
	'5': "₅", '6': "₆", '7': "₇", '8': "₈", '9': "₉",
}

// SuperscriptDigits maps digits to Unicode superscript characters.
var SuperscriptDigits = map[byte]string{
	'0': "⁰", '1': "¹", '2': "²", '3': "³", '4': "⁴",
	'5': "⁵", '6': "⁶", '7': "⁷", '8': "⁸", '9': "⁹",
}

// FormulaEngine parses chemical formulas and provides conversions.
type FormulaEngine struct{}

// NewFormulaEngine creates a new FormulaEngine.
func NewFormulaEngine() *FormulaEngine {
	return &FormulaEngine{}
}

// FormulaResult is the result of parsing a chemical formula.
type FormulaResult struct {
	Original     string         `json:"original"`
	Elements     map[string]int `json:"elements"`
	MolecularWt  float64        `json:"molecularWeight"`
	Subscript    string         `json:"subscript"`
	Latex        string         `json:"latex"`
	IsValid      bool           `json:"isValid"`
	Error        string         `json:"error,omitempty"`
}

// Parse parses a chemical formula and returns element counts.
func (fe *FormulaEngine) Parse(formula string) FormulaResult {
	result := FormulaResult{
		Original: formula,
		Elements: make(map[string]int),
	}

	elements, err := fe.parseFormula(formula)
	if err != nil {
		result.IsValid = false
		result.Error = err.Error()
		return result
	}

	result.Elements = elements
	result.IsValid = true

	// Calculate molecular weight
	var mw float64
	for elem, count := range elements {
		if data, ok := PeriodicTable[elem]; ok {
			mw += data.AtomicMass * float64(count)
		}
	}
	result.MolecularWt = mw

	// Generate subscript format
	result.Subscript = fe.ToSubscript(formula)

	// Generate LaTeX
	result.Latex = fe.ToLatex(formula, "mhchem")

	return result
}

// parseFormula recursively parses a chemical formula into element counts.
func (fe *FormulaEngine) parseFormula(formula string) (map[string]int, error) {
	result := make(map[string]int)
	i := 0
	n := len(formula)

	for i < n {
		if formula[i] == '(' || formula[i] == '[' {
			content, endIdx, err := fe.extractBracket(formula, i)
			if err != nil {
				return nil, err
			}
			multiplier, newIdx := fe.extractNumber(formula, endIdx)
			inner, err := fe.parseFormula(content)
			if err != nil {
				return nil, err
			}
			for elem, count := range inner {
				result[elem] += count * multiplier
			}
			i = newIdx
		} else if formula[i] >= 'A' && formula[i] <= 'Z' {
			elem, newI := fe.extractElement(formula, i)
			if _, ok := PeriodicTable[elem]; !ok {
				return nil, fmt.Errorf("unknown element: %s", elem)
			}
			count, newI2 := fe.extractNumber(formula, newI)
			result[elem] += count
			i = newI2
		} else if formula[i] == '+' || formula[i] == '-' {
			// Skip charge markers (e.g. NH4+, SO4 2-)
			i++
			for i < n && (formula[i] >= '0' && formula[i] <= '9') {
				i++
			}
		} else if formula[i] == ' ' {
			i++
		} else {
			return nil, fmt.Errorf("unexpected character '%c' at position %d", formula[i], i)
		}
	}

	if len(result) == 0 {
		return nil, fmt.Errorf("empty formula")
	}

	return result, nil
}

// extractBracket extracts content between matching brackets.
func (fe *FormulaEngine) extractBracket(s string, start int) (string, int, error) {
	openChar := s[start]
	var closeChar byte
	if openChar == '(' {
		closeChar = ')'
	} else {
		closeChar = ']'
	}

	depth := 0
	for i := start; i < len(s); i++ {
		if s[i] == openChar {
			depth++
		} else if s[i] == closeChar {
			depth--
			if depth == 0 {
				return s[start+1 : i], i + 1, nil
			}
		}
	}
	return "", 0, fmt.Errorf("unmatched bracket at position %d", start)
}

// extractElement extracts an element symbol starting at position start.
func (fe *FormulaEngine) extractElement(s string, start int) (string, int) {
	if start >= len(s) {
		return "", start
	}
	elem := string(s[start])
	i := start + 1
	for i < len(s) && unicode.IsLower(rune(s[i])) {
		elem += string(s[i])
		i++
	}
	if _, ok := PeriodicTable[elem]; !ok {
		return elem, i // Return even if unknown; caller can check
	}
	return elem, i
}

// extractNumber extracts a number starting at position start.
func (fe *FormulaEngine) extractNumber(s string, start int) (int, int) {
	num := 0
	found := false
	i := start
	for i < len(s) && s[i] >= '0' && s[i] <= '9' {
		num = num*10 + int(s[i]-'0')
		found = true
		i++
	}
	if !found {
		return 1, i
	}
	return num, i
}

// ToSubscript converts a chemical formula to Unicode subscript format.
func (fe *FormulaEngine) ToSubscript(formula string) string {
	var result strings.Builder
	i := 0
	n := len(formula)

	for i < n {
		ch := formula[i]
		if ch == '(' || ch == '[' {
			result.WriteByte(ch)
			i++
		} else if ch == ')' || ch == ']' {
			result.WriteByte(ch)
			i++
			// Convert digits after bracket to subscript
			for i < n && formula[i] >= '0' && formula[i] <= '9' {
				if sub, ok := SubscriptDigits[formula[i]]; ok {
					result.WriteString(sub)
				}
				i++
			}
		} else if ch >= 'A' && ch <= 'Z' {
			result.WriteByte(ch)
			i++
			for i < n && formula[i] >= 'a' && formula[i] <= 'z' {
				result.WriteByte(formula[i])
				i++
			}
			// Convert digits after element to subscript
			for i < n && formula[i] >= '0' && formula[i] <= '9' {
				if sub, ok := SubscriptDigits[formula[i]]; ok {
					result.WriteString(sub)
				}
				i++
			}
		} else if ch == '+' || ch == '-' {
			// Convert charge to superscript
			for i < n && (formula[i] == '+' || formula[i] == '-' || (formula[i] >= '0' && formula[i] <= '9')) {
				if sup, ok := SuperscriptDigits[formula[i]]; ok {
					result.WriteString(sup)
				} else if formula[i] == '+' {
					result.WriteString("⁺")
				} else if formula[i] == '-' {
					result.WriteString("⁻")
				}
				i++
			}
		} else {
			result.WriteByte(ch)
			i++
		}
	}
	return result.String()
}

// ToLatex converts a chemical formula to LaTeX format.
func (fe *FormulaEngine) ToLatex(formula string, pkg string) string {
	if pkg == "mhchem" {
		return fmt.Sprintf("\\ce{%s}", formula)
	}
	// Standard LaTeX format
	var result strings.Builder
	i := 0
	n := len(formula)

	for i < n {
		if formula[i] >= 'A' && formula[i] <= 'Z' {
			result.WriteByte(formula[i])
			i++
			for i < n && formula[i] >= 'a' && formula[i] <= 'z' {
				result.WriteByte(formula[i])
				i++
			}
			if i < n && formula[i] >= '0' && formula[i] <= '9' {
				num := ""
				for i < n && formula[i] >= '0' && formula[i] <= '9' {
					num += string(formula[i])
					i++
				}
				result.WriteString(fmt.Sprintf("_{%s}", num))
			}
		} else if formula[i] == '+' || formula[i] == '-' {
			charge := ""
			for i < n && (formula[i] == '+' || formula[i] == '-' || (formula[i] >= '0' && formula[i] <= '9')) {
				charge += string(formula[i])
				i++
			}
			result.WriteString(fmt.Sprintf("^{%s}", charge))
		} else {
			result.WriteByte(formula[i])
			i++
		}
	}
	return result.String()
}
