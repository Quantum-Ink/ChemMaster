package chemistry

import (
	"fmt"
	"math"
	"regexp"
	"sort"
	"strings"
)

// EquationBalancer balances chemical equations using matrix null-space method.
type EquationBalancer struct {
	fe *FormulaEngine
}

// NewEquationBalancer creates a new EquationBalancer.
func NewEquationBalancer() *EquationBalancer {
	return &EquationBalancer{fe: NewFormulaEngine()}
}

// BalanceResult is the result of balancing a chemical equation.
type BalanceResult struct {
	Original      string   `json:"original"`
	Balanced      string   `json:"balanced"`
	Coefficients  []int    `json:"coefficients"`
	IsBalanced    bool     `json:"isBalanced"`
	Elements      []string `json:"elements"`
	Subscript     string   `json:"subscript"`
	Latex         string   `json:"latex"`
	Error         string   `json:"error,omitempty"`
}

// sepRegex matches reaction separators.
var sepRegex = regexp.MustCompile(`(->|→|⟶|<=>|⇌|⇋|={1,2})`)

// coeffRegex matches a leading coefficient.
var coeffRegex = regexp.MustCompile(`^(\d+)\s*(.+)$`)

// Balance balances a chemical equation.
func (eb *EquationBalancer) Balance(equation string) BalanceResult {
	result := BalanceResult{Original: equation}

	// Parse equation
	reactants, products, separator, err := eb.parseEquation(equation)
	if err != nil {
		result.Error = err.Error()
		return result
	}

	// Collect all elements
	elementSet := make(map[string]bool)
	reactantFormulas := make([]map[string]int, len(reactants))
	productFormulas := make([]map[string]int, len(products))

	for i, term := range reactants {
		_, formula := eb.extractCoeff(term)
		elements, err := eb.fe.parseFormula(formula)
		if err != nil {
			result.Error = fmt.Sprintf("parsing '%s': %v", formula, err)
			return result
		}
		reactantFormulas[i] = elements
		for e := range elements {
			elementSet[e] = true
		}
	}

	for i, term := range products {
		_, formula := eb.extractCoeff(term)
		elements, err := eb.fe.parseFormula(formula)
		if err != nil {
			result.Error = fmt.Sprintf("parsing '%s': %v", formula, err)
			return result
		}
		productFormulas[i] = elements
		for e := range elements {
			elementSet[e] = true
		}
	}

	// Sort elements for deterministic ordering
	elements := make([]string, 0, len(elementSet))
	for e := range elementSet {
		elements = append(elements, e)
	}
	sort.Strings(elements)
	result.Elements = elements

	numElements := len(elements)
	numCompounds := len(reactants) + len(products)

	if numCompounds == 0 {
		result.Error = "empty equation"
		return result
	}

	// Build matrix: rows = elements, cols = compounds
	// Reactants positive, products negative
	matrix := make([][]float64, numElements)
	for i, elem := range elements {
		matrix[i] = make([]float64, numCompounds)
		for j, formula := range reactantFormulas {
			matrix[i][j] = float64(formula[elem])
		}
		for j, formula := range productFormulas {
			matrix[i][j+len(reactants)] = -float64(formula[elem])
		}
	}

	// Solve null space
	coeffs := eb.solveNullSpace(matrix, numCompounds)
	if coeffs == nil {
		result.Error = "cannot balance this equation"
		return result
	}

	// Convert to integer coefficients
	intCoeffs := eb.toIntegerCoefficients(coeffs)
	result.Coefficients = intCoeffs

	// Build balanced equation
	balancedR := make([]string, len(reactants))
	for i, term := range reactants {
		_, formula := eb.extractCoeff(term)
		c := intCoeffs[i]
		if c == 1 {
			balancedR[i] = formula
		} else {
			balancedR[i] = fmt.Sprintf("%d%s", c, formula)
		}
	}

	balancedP := make([]string, len(products))
	for i, term := range products {
		_, formula := eb.extractCoeff(term)
		c := intCoeffs[i+len(reactants)]
		if c == 1 {
			balancedP[i] = formula
		} else {
			balancedP[i] = fmt.Sprintf("%d%s", c, formula)
		}
	}

	balanced := strings.Join(balancedR, " + ") + " " + separator + " " + strings.Join(balancedP, " + ")
	result.Balanced = balanced
	result.IsBalanced = true

	// Generate subscript and LaTeX
	result.Subscript = eb.toSubscriptEquation(balancedR, balancedP, separator)
	result.Latex = eb.toLatexEquation(balancedR, balancedP, separator)

	return result
}

// parseEquation splits an equation into reactants, products, and separator.
func (eb *EquationBalancer) parseEquation(equation string) ([]string, []string, string, error) {
	loc := sepRegex.FindStringIndex(equation)
	if loc == nil {
		return nil, nil, "", fmt.Errorf("no reaction separator found in: %s", equation)
	}

	sep := equation[loc[0]:loc[1]]
	parts := strings.SplitN(equation, sep, 2)
	if len(parts) != 2 {
		return nil, nil, "", fmt.Errorf("invalid equation format")
	}

	reactants := splitTerms(parts[0])
	products := splitTerms(parts[1])

	return reactants, products, sep, nil
}

// splitTerms splits a string by '+' and trims whitespace.
func splitTerms(s string) []string {
	parts := strings.Split(s, "+")
	result := make([]string, 0, len(parts))
	for _, p := range parts {
		trimmed := strings.TrimSpace(p)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

// extractCoeff extracts the leading coefficient and formula from a term.
func (eb *EquationBalancer) extractCoeff(term string) (int, string) {
	matches := coeffRegex.FindStringSubmatch(strings.TrimSpace(term))
	if matches != nil {
		coeff := 0
		fmt.Sscanf(matches[1], "%d", &coeff)
		return coeff, matches[2]
	}
	return 1, strings.TrimSpace(term)
}

// solveNullSpace finds a basis vector for the null space of the matrix.
func (eb *EquationBalancer) solveNullSpace(matrix [][]float64, n int) []float64 {
	rows := len(matrix)
	if rows == 0 {
		return nil
	}

	// Create a copy for Gaussian elimination
	A := make([][]float64, rows)
	for i := range matrix {
		A[i] = make([]float64, n)
		copy(A[i], matrix[i])
	}

	// Gaussian elimination with partial pivoting
	pivotCols := []int{}
	pivotRow := 0

	for col := 0; col < n; col++ {
		// Find pivot
		found := false
		for row := pivotRow; row < rows; row++ {
			if math.Abs(A[row][col]) > 1e-10 {
				// Swap rows
				A[pivotRow], A[row] = A[row], A[pivotRow]
				found = true
				break
			}
		}
		if !found {
			continue
		}

		// Normalize pivot row
		pivot := A[pivotRow][col]
		for j := 0; j < n; j++ {
			A[pivotRow][j] /= pivot
		}

		// Eliminate column
		for row := 0; row < rows; row++ {
			if row != pivotRow && math.Abs(A[row][col]) > 1e-10 {
				factor := A[row][col]
				for j := 0; j < n; j++ {
					A[row][j] -= factor * A[pivotRow][j]
				}
			}
		}

		pivotCols = append(pivotCols, col)
		pivotRow++
	}

	// Find free variables
	pivotSet := make(map[int]bool)
	for _, c := range pivotCols {
		pivotSet[c] = true
	}

	freeVars := []int{}
	for i := 0; i < n; i++ {
		if !pivotSet[i] {
			freeVars = append(freeVars, i)
		}
	}

	if len(freeVars) == 0 {
		return nil
	}

	// Build solution: set first free variable to 1
	solution := make([]float64, n)
	freeIdx := freeVars[0]
	solution[freeIdx] = 1.0

	// Back-substitute
	for i, col := range pivotCols {
		solution[col] = -A[i][freeIdx]
	}

	return solution
}

// frac represents a rational number as numerator/denominator.
type frac struct {
	num, den int64
}

// toIntegerCoefficients converts float coefficients to smallest positive integers.
func (eb *EquationBalancer) toIntegerCoefficients(coeffs []float64) []int {
	fracs := make([]frac, len(coeffs))
	for i, c := range coeffs {
		fracs[i] = floatToFraction(c, 10000)
	}

	// Find LCM of denominators
	lcm := fracs[0].den
	for _, f := range fracs[1:] {
		lcm = lcmInt(lcm, f.den)
	}

	// Scale to integers
	intCoeffs := make([]int, len(fracs))
	for i, f := range fracs {
		intCoeffs[i] = int(f.num * (lcm / f.den))
	}

	// Ensure all positive
	if intCoeffs[0] < 0 {
		for i := range intCoeffs {
			intCoeffs[i] = -intCoeffs[i]
		}
	}

	// GCD reduction
	g := intCoeffs[0]
	for _, c := range intCoeffs[1:] {
		g = gcdInt(g, c)
	}
	if g > 1 {
		for i := range intCoeffs {
			intCoeffs[i] /= g
		}
	}

	return intCoeffs
}

func floatToFraction(f float64, maxDen int64) frac {
	if f == 0 {
		return frac{0, 1}
	}
	sign := int64(1)
	if f < 0 {
		sign = -1
		f = -f
	}

	bestNum, bestDen := int64(0), int64(1)
	bestErr := math.Abs(f)

	for d := int64(1); d <= maxDen; d++ {
		n := int64(math.Round(f * float64(d)))
		err := math.Abs(f - float64(n)/float64(d))
		if err < bestErr {
			bestErr = err
			bestNum = n
			bestDen = d
			if err < 1e-10 {
				break
			}
		}
	}

	return frac{sign * bestNum, bestDen}
}

func gcdInt(a, b int) int {
	if a < 0 {
		a = -a
	}
	if b < 0 {
		b = -b
	}
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func lcmInt(a, b int64) int64 {
	if a < 0 {
		a = -a
	}
	if b < 0 {
		b = -b
	}
	return a * b / int64(gcdInt(int(a), int(b)))
}

func (eb *EquationBalancer) toSubscriptEquation(reactants, products []string, sep string) string {
	fe := NewFormulaEngine()
	var parts []string
	for _, r := range reactants {
		c, formula := eb.extractCoeff(r)
		sub := fe.ToSubscript(formula)
		if c > 1 {
			parts = append(parts, fmt.Sprintf("%d%s", c, sub))
		} else {
			parts = append(parts, sub)
		}
	}
	result := strings.Join(parts, " + ") + " " + sep + " "
	parts = nil
	for _, p := range products {
		c, formula := eb.extractCoeff(p)
		sub := fe.ToSubscript(formula)
		if c > 1 {
			parts = append(parts, fmt.Sprintf("%d%s", c, sub))
		} else {
			parts = append(parts, sub)
		}
	}
	return result + strings.Join(parts, " + ")
}

func (eb *EquationBalancer) toLatexEquation(reactants, products []string, sep string) string {
	fe := NewFormulaEngine()
	var parts []string
	for _, r := range reactants {
		c, formula := eb.extractCoeff(r)
		latex := fe.ToLatex(formula, "mhchem")
		if c > 1 {
			parts = append(parts, fmt.Sprintf("%d%s", c, latex))
		} else {
			parts = append(parts, latex)
		}
	}
	result := strings.Join(parts, " + ") + " " + sep + " "
	parts = nil
	for _, p := range products {
		c, formula := eb.extractCoeff(p)
		latex := fe.ToLatex(formula, "mhchem")
		if c > 1 {
			parts = append(parts, fmt.Sprintf("%d%s", c, latex))
		} else {
			parts = append(parts, latex)
		}
	}
	return result + strings.Join(parts, " + ")
}
