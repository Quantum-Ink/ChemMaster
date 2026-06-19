package chemistry

import (
	"fmt"
	"strings"
	"unicode"
)

// ElementData holds information about a chemical element.
type ElementData struct {
	Symbol       string
	NameEN       string
	NameCN       string
	AtomicNumber int
	AtomicMass   float64
}

// PeriodicTable contains all known elements.
var PeriodicTable = map[string]ElementData{
	"H":  {Symbol: "H", NameEN: "Hydrogen", NameCN: "氢", AtomicNumber: 1, AtomicMass: 1.008},
	"He": {Symbol: "He", NameEN: "Helium", NameCN: "氦", AtomicNumber: 2, AtomicMass: 4.003},
	"Li": {Symbol: "Li", NameEN: "Lithium", NameCN: "锂", AtomicNumber: 3, AtomicMass: 6.941},
	"Be": {Symbol: "Be", NameEN: "Beryllium", NameCN: "铍", AtomicNumber: 4, AtomicMass: 9.012},
	"B":  {Symbol: "B", NameEN: "Boron", NameCN: "硼", AtomicNumber: 5, AtomicMass: 10.81},
	"C":  {Symbol: "C", NameEN: "Carbon", NameCN: "碳", AtomicNumber: 6, AtomicMass: 12.011},
	"N":  {Symbol: "N", NameEN: "Nitrogen", NameCN: "氮", AtomicNumber: 7, AtomicMass: 14.007},
	"O":  {Symbol: "O", NameEN: "Oxygen", NameCN: "氧", AtomicNumber: 8, AtomicMass: 15.999},
	"F":  {Symbol: "F", NameEN: "Fluorine", NameCN: "氟", AtomicNumber: 9, AtomicMass: 18.998},
	"Ne": {Symbol: "Ne", NameEN: "Neon", NameCN: "氖", AtomicNumber: 10, AtomicMass: 20.180},
	"Na": {Symbol: "Na", NameEN: "Sodium", NameCN: "钠", AtomicNumber: 11, AtomicMass: 22.990},
	"Mg": {Symbol: "Mg", NameEN: "Magnesium", NameCN: "镁", AtomicNumber: 12, AtomicMass: 24.305},
	"Al": {Symbol: "Al", NameEN: "Aluminium", NameCN: "铝", AtomicNumber: 13, AtomicMass: 26.982},
	"Si": {Symbol: "Si", NameEN: "Silicon", NameCN: "硅", AtomicNumber: 14, AtomicMass: 28.086},
	"P":  {Symbol: "P", NameEN: "Phosphorus", NameCN: "磷", AtomicNumber: 15, AtomicMass: 30.974},
	"S":  {Symbol: "S", NameEN: "Sulfur", NameCN: "硫", AtomicNumber: 16, AtomicMass: 32.065},
	"Cl": {Symbol: "Cl", NameEN: "Chlorine", NameCN: "氯", AtomicNumber: 17, AtomicMass: 35.453},
	"Ar": {Symbol: "Ar", NameEN: "Argon", NameCN: "氩", AtomicNumber: 18, AtomicMass: 39.948},
	"K":  {Symbol: "K", NameEN: "Potassium", NameCN: "钾", AtomicNumber: 19, AtomicMass: 39.098},
	"Ca": {Symbol: "Ca", NameEN: "Calcium", NameCN: "钙", AtomicNumber: 20, AtomicMass: 40.078},
	"Sc": {Symbol: "Sc", NameEN: "Scandium", NameCN: "钪", AtomicNumber: 21, AtomicMass: 44.956},
	"Ti": {Symbol: "Ti", NameEN: "Titanium", NameCN: "钛", AtomicNumber: 22, AtomicMass: 47.867},
	"V":  {Symbol: "V", NameEN: "Vanadium", NameCN: "钒", AtomicNumber: 23, AtomicMass: 50.942},
	"Cr": {Symbol: "Cr", NameEN: "Chromium", NameCN: "铬", AtomicNumber: 24, AtomicMass: 51.996},
	"Mn": {Symbol: "Mn", NameEN: "Manganese", NameCN: "锰", AtomicNumber: 25, AtomicMass: 54.938},
	"Fe": {Symbol: "Fe", NameEN: "Iron", NameCN: "铁", AtomicNumber: 26, AtomicMass: 55.845},
	"Co": {Symbol: "Co", NameEN: "Cobalt", NameCN: "钴", AtomicNumber: 27, AtomicMass: 58.933},
	"Ni": {Symbol: "Ni", NameEN: "Nickel", NameCN: "镍", AtomicNumber: 28, AtomicMass: 58.693},
	"Cu": {Symbol: "Cu", NameEN: "Copper", NameCN: "铜", AtomicNumber: 29, AtomicMass: 63.546},
	"Zn": {Symbol: "Zn", NameEN: "Zinc", NameCN: "锌", AtomicNumber: 30, AtomicMass: 65.380},
	"Ga": {Symbol: "Ga", NameEN: "Gallium", NameCN: "镓", AtomicNumber: 31, AtomicMass: 69.723},
	"Ge": {Symbol: "Ge", NameEN: "Germanium", NameCN: "锗", AtomicNumber: 32, AtomicMass: 72.630},
	"As": {Symbol: "As", NameEN: "Arsenic", NameCN: "砷", AtomicNumber: 33, AtomicMass: 74.922},
	"Se": {Symbol: "Se", NameEN: "Selenium", NameCN: "硒", AtomicNumber: 34, AtomicMass: 78.971},
	"Br": {Symbol: "Br", NameEN: "Bromine", NameCN: "溴", AtomicNumber: 35, AtomicMass: 79.904},
	"Kr": {Symbol: "Kr", NameEN: "Krypton", NameCN: "氪", AtomicNumber: 36, AtomicMass: 83.798},
	"Rb": {Symbol: "Rb", NameEN: "Rubidium", NameCN: "铷", AtomicNumber: 37, AtomicMass: 85.468},
	"Sr": {Symbol: "Sr", NameEN: "Strontium", NameCN: "锶", AtomicNumber: 38, AtomicMass: 87.620},
	"Y":  {Symbol: "Y", NameEN: "Yttrium", NameCN: "钇", AtomicNumber: 39, AtomicMass: 88.906},
	"Zr": {Symbol: "Zr", NameEN: "Zirconium", NameCN: "锆", AtomicNumber: 40, AtomicMass: 91.224},
	"Nb": {Symbol: "Nb", NameEN: "Niobium", NameCN: "铌", AtomicNumber: 41, AtomicMass: 92.906},
	"Mo": {Symbol: "Mo", NameEN: "Molybdenum", NameCN: "钼", AtomicNumber: 42, AtomicMass: 95.950},
	"Tc": {Symbol: "Tc", NameEN: "Technetium", NameCN: "锝", AtomicNumber: 43, AtomicMass: 98.000},
	"Ru": {Symbol: "Ru", NameEN: "Ruthenium", NameCN: "钌", AtomicNumber: 44, AtomicMass: 101.07},
	"Rh": {Symbol: "Rh", NameEN: "Rhodium", NameCN: "铑", AtomicNumber: 45, AtomicMass: 102.91},
	"Pd": {Symbol: "Pd", NameEN: "Palladium", NameCN: "钯", AtomicNumber: 46, AtomicMass: 106.42},
	"Ag": {Symbol: "Ag", NameEN: "Silver", NameCN: "银", AtomicNumber: 47, AtomicMass: 107.87},
	"Cd": {Symbol: "Cd", NameEN: "Cadmium", NameCN: "镉", AtomicNumber: 48, AtomicMass: 112.41},
	"In": {Symbol: "In", NameEN: "Indium", NameCN: "铟", AtomicNumber: 49, AtomicMass: 114.82},
	"Sn": {Symbol: "Sn", NameEN: "Tin", NameCN: "锡", AtomicNumber: 50, AtomicMass: 118.71},
	"Sb": {Symbol: "Sb", NameEN: "Antimony", NameCN: "锑", AtomicNumber: 51, AtomicMass: 121.76},
	"Te": {Symbol: "Te", NameEN: "Tellurium", NameCN: "碲", AtomicNumber: 52, AtomicMass: 127.60},
	"I":  {Symbol: "I", NameEN: "Iodine", NameCN: "碘", AtomicNumber: 53, AtomicMass: 126.90},
	"Xe": {Symbol: "Xe", NameEN: "Xenon", NameCN: "氙", AtomicNumber: 54, AtomicMass: 131.29},
	"Cs": {Symbol: "Cs", NameEN: "Caesium", NameCN: "铯", AtomicNumber: 55, AtomicMass: 132.91},
	"Ba": {Symbol: "Ba", NameEN: "Barium", NameCN: "钡", AtomicNumber: 56, AtomicMass: 137.33},
	"La": {Symbol: "La", NameEN: "Lanthanum", NameCN: "镧", AtomicNumber: 57, AtomicMass: 138.91},
	"Ce": {Symbol: "Ce", NameEN: "Cerium", NameCN: "铈", AtomicNumber: 58, AtomicMass: 140.12},
	"Pr": {Symbol: "Pr", NameEN: "Praseodymium", NameCN: "镨", AtomicNumber: 59, AtomicMass: 140.91},
	"Nd": {Symbol: "Nd", NameEN: "Neodymium", NameCN: "钕", AtomicNumber: 60, AtomicMass: 144.24},
	"Pm": {Symbol: "Pm", NameEN: "Promethium", NameCN: "钷", AtomicNumber: 61, AtomicMass: 145.00},
	"Sm": {Symbol: "Sm", NameEN: "Samarium", NameCN: "钐", AtomicNumber: 62, AtomicMass: 150.36},
	"Eu": {Symbol: "Eu", NameEN: "Europium", NameCN: "铕", AtomicNumber: 63, AtomicMass: 151.96},
	"Gd": {Symbol: "Gd", NameEN: "Gadolinium", NameCN: "钆", AtomicNumber: 64, AtomicMass: 157.25},
	"Tb": {Symbol: "Tb", NameEN: "Terbium", NameCN: "铽", AtomicNumber: 65, AtomicMass: 158.93},
	"Dy": {Symbol: "Dy", NameEN: "Dysprosium", NameCN: "镝", AtomicNumber: 66, AtomicMass: 162.50},
	"Ho": {Symbol: "Ho", NameEN: "Holmium", NameCN: "钬", AtomicNumber: 67, AtomicMass: 164.93},
	"Er": {Symbol: "Er", NameEN: "Erbium", NameCN: "铒", AtomicNumber: 68, AtomicMass: 167.26},
	"Tm": {Symbol: "Tm", NameEN: "Thulium", NameCN: "铥", AtomicNumber: 69, AtomicMass: 168.93},
	"Yb": {Symbol: "Yb", NameEN: "Ytterbium", NameCN: "镱", AtomicNumber: 70, AtomicMass: 173.05},
	"Lu": {Symbol: "Lu", NameEN: "Lutetium", NameCN: "镥", AtomicNumber: 71, AtomicMass: 174.97},
	"Hf": {Symbol: "Hf", NameEN: "Hafnium", NameCN: "铪", AtomicNumber: 72, AtomicMass: 178.49},
	"Ta": {Symbol: "Ta", NameEN: "Tantalum", NameCN: "钽", AtomicNumber: 73, AtomicMass: 180.95},
	"W":  {Symbol: "W", NameEN: "Tungsten", NameCN: "钨", AtomicNumber: 74, AtomicMass: 183.84},
	"Re": {Symbol: "Re", NameEN: "Rhenium", NameCN: "铼", AtomicNumber: 75, AtomicMass: 186.21},
	"Os": {Symbol: "Os", NameEN: "Osmium", NameCN: "锇", AtomicNumber: 76, AtomicMass: 190.23},
	"Ir": {Symbol: "Ir", NameEN: "Iridium", NameCN: "铱", AtomicNumber: 77, AtomicMass: 192.22},
	"Pt": {Symbol: "Pt", NameEN: "Platinum", NameCN: "铂", AtomicNumber: 78, AtomicMass: 195.08},
	"Au": {Symbol: "Au", NameEN: "Gold", NameCN: "金", AtomicNumber: 79, AtomicMass: 196.97},
	"Hg": {Symbol: "Hg", NameEN: "Mercury", NameCN: "汞", AtomicNumber: 80, AtomicMass: 200.59},
	"Tl": {Symbol: "Tl", NameEN: "Thallium", NameCN: "铊", AtomicNumber: 81, AtomicMass: 204.38},
	"Pb": {Symbol: "Pb", NameEN: "Lead", NameCN: "铅", AtomicNumber: 82, AtomicMass: 207.20},
	"Bi": {Symbol: "Bi", NameEN: "Bismuth", NameCN: "铋", AtomicNumber: 83, AtomicMass: 208.98},
	"Po": {Symbol: "Po", NameEN: "Polonium", NameCN: "钋", AtomicNumber: 84, AtomicMass: 209.00},
	"At": {Symbol: "At", NameEN: "Astatine", NameCN: "砹", AtomicNumber: 85, AtomicMass: 210.00},
	"Rn": {Symbol: "Rn", NameEN: "Radon", NameCN: "氡", AtomicNumber: 86, AtomicMass: 222.00},
	"Fr": {Symbol: "Fr", NameEN: "Francium", NameCN: "钫", AtomicNumber: 87, AtomicMass: 223.00},
	"Ra": {Symbol: "Ra", NameEN: "Radium", NameCN: "镭", AtomicNumber: 88, AtomicMass: 226.00},
	"Ac": {Symbol: "Ac", NameEN: "Actinium", NameCN: "锕", AtomicNumber: 89, AtomicMass: 227.00},
	"Th": {Symbol: "Th", NameEN: "Thorium", NameCN: "钍", AtomicNumber: 90, AtomicMass: 232.04},
	"Pa": {Symbol: "Pa", NameEN: "Protactinium", NameCN: "镤", AtomicNumber: 91, AtomicMass: 231.04},
	"U":  {Symbol: "U", NameEN: "Uranium", NameCN: "铀", AtomicNumber: 92, AtomicMass: 238.03},
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
			// Extract bracketed content
			content, endIdx, err := fe.extractBracket(formula, i)
			if err != nil {
				return nil, err
			}
			// Get multiplier after bracket
			multiplier, newIdx := fe.extractNumber(formula, endIdx)
			// Recursively parse inner content
			inner, err := fe.parseFormula(content)
			if err != nil {
				return nil, err
			}
			// Multiply counts
			for elem, count := range inner {
				result[elem] += count * multiplier
			}
			i = newIdx
		} else if formula[i] >= 'A' && formula[i] <= 'Z' {
			// Extract element symbol
			elem, newI := fe.extractElement(formula, i)
			count, newI2 := fe.extractNumber(formula, newI)
			result[elem] += count
			i = newI2
		} else {
			i++
		}
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
