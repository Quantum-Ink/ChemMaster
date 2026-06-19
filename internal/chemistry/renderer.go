package chemistry

import (
	"fmt"
	"strings"
)

// Renderer handles LaTeX and export rendering for chemical formulas and equations.
type Renderer struct {
	fe *FormulaEngine
}

// NewRenderer creates a new Renderer.
func NewRenderer() *Renderer {
	return &Renderer{fe: NewFormulaEngine()}
}

// RenderResult contains multiple render formats.
type RenderResult struct {
	Latex    string `json:"latex"`
	Markdown string `json:"markdown"`
	HTML     string `json:"html"`
	Unicode  string `json:"unicode"`
}

// RenderFormula renders a chemical formula in multiple formats.
func (r *Renderer) RenderFormula(formula string) RenderResult {
	return RenderResult{
		Latex:    r.fe.ToLatex(formula, "mhchem"),
		Markdown: formula,
		HTML:     r.formulaToHTML(formula),
		Unicode:  r.fe.ToSubscript(formula),
	}
}

// RenderEquation renders a chemical equation in multiple formats.
func (r *Renderer) RenderEquation(equation string) RenderResult {
	balancer := NewEquationBalancer()
	balanceResult := balancer.Balance(equation)
	balanced := balanceResult.Balanced
	if balanced == "" {
		balanced = equation
	}

	return RenderResult{
		Latex:    r.equationToLatex(balanced),
		Markdown: r.equationToMarkdown(balanced),
		HTML:     r.equationToHTML(balanced),
		Unicode:  r.equationToUnicode(balanced),
	}
}

// ToLatexMhchem converts an equation to mhchem LaTeX format.
func (r *Renderer) ToLatexMhchem(equation string) string {
	return fmt.Sprintf("\\ce{%s}", equation)
}

// formulaToHTML converts a chemical formula to HTML with subscripts/superscripts.
func (r *Renderer) formulaToHTML(formula string) string {
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
			digits := ""
			for i < n && formula[i] >= '0' && formula[i] <= '9' {
				digits += string(formula[i])
				i++
			}
			if digits != "" {
				result.WriteString(fmt.Sprintf("<sub>%s</sub>", digits))
			}
		} else if ch >= 'A' && ch <= 'Z' {
			result.WriteByte(ch)
			i++
			for i < n && formula[i] >= 'a' && formula[i] <= 'z' {
				result.WriteByte(formula[i])
				i++
			}
			digits := ""
			for i < n && formula[i] >= '0' && formula[i] <= '9' {
				digits += string(formula[i])
				i++
			}
			if digits != "" {
				result.WriteString(fmt.Sprintf("<sub>%s</sub>", digits))
			}
		} else if ch == '+' || ch == '-' {
			charge := ""
			for i < n && (formula[i] == '+' || formula[i] == '-' || (formula[i] >= '0' && formula[i] <= '9')) {
				charge += string(formula[i])
				i++
			}
			result.WriteString(fmt.Sprintf("<sup>%s</sup>", charge))
		} else {
			result.WriteByte(ch)
			i++
		}
	}
	return result.String()
}

// equationToLatex converts an equation to LaTeX.
func (r *Renderer) equationToLatex(equation string) string {
	// Replace separators for mhchem
	result := equation
	result = strings.ReplaceAll(result, "->", "\\to")
	result = strings.ReplaceAll(result, "⇌", "\\rightleftharpoons")
	return fmt.Sprintf("\\ce{%s}", result)
}

// equationToMarkdown converts an equation to Markdown.
func (r *Renderer) equationToMarkdown(equation string) string {
	return equation
}

// equationToHTML converts an equation to HTML.
func (r *Renderer) equationToHTML(equation string) string {
	separators := []string{"<=>", "⇌", "⇋", "->", "→", "⟶"}
	sep := "->"
	for _, s := range separators {
		if strings.Contains(equation, s) {
			sep = s
			break
		}
	}

	parts := strings.SplitN(equation, sep, 2)
	if len(parts) != 2 {
		return equation
	}

	htmlSep := "→"
	if sep == "<=>" || sep == "⇌" || sep == "⇋" {
		htmlSep = "⇌"
	}

	reactants := splitTerms(parts[0])
	products := splitTerms(parts[1])

	var rParts []string
	for _, t := range reactants {
		c, formula := NewEquationBalancer().extractCoeff(t)
		html := r.formulaToHTML(formula)
		if c > 1 {
			rParts = append(rParts, fmt.Sprintf("%d%s", c, html))
		} else {
			rParts = append(rParts, html)
		}
	}

	var pParts []string
	for _, t := range products {
		c, formula := NewEquationBalancer().extractCoeff(t)
		html := r.formulaToHTML(formula)
		if c > 1 {
			pParts = append(pParts, fmt.Sprintf("%d%s", c, html))
		} else {
			pParts = append(pParts, html)
		}
	}

	return strings.Join(rParts, " + ") + " " + htmlSep + " " + strings.Join(pParts, " + ")
}

// equationToUnicode converts an equation to Unicode.
func (r *Renderer) equationToUnicode(equation string) string {
	fe := NewFormulaEngine()
	balancer := NewEquationBalancer()

	separators := []string{"<=>", "⇌", "⇋", "->", "→", "⟶"}
	sep := "->"
	for _, s := range separators {
		if strings.Contains(equation, s) {
			sep = s
			break
		}
	}

	parts := strings.SplitN(equation, sep, 2)
	if len(parts) != 2 {
		return equation
	}

	unicodeSep := "→"
	if sep == "<=>" || sep == "⇌" || sep == "⇋" {
		unicodeSep = "⇌"
	}

	reactants := splitTerms(parts[0])
	products := splitTerms(parts[1])

	var rParts []string
	for _, t := range reactants {
		c, formula := balancer.extractCoeff(t)
		sub := fe.ToSubscript(formula)
		if c > 1 {
			rParts = append(rParts, fmt.Sprintf("%d%s", c, sub))
		} else {
			rParts = append(rParts, sub)
		}
	}

	var pParts []string
	for _, t := range products {
		c, formula := balancer.extractCoeff(t)
		sub := fe.ToSubscript(formula)
		if c > 1 {
			pParts = append(pParts, fmt.Sprintf("%d%s", c, sub))
		} else {
			pParts = append(pParts, sub)
		}
	}

	return strings.Join(rParts, " + ") + " " + unicodeSep + " " + strings.Join(pParts, " + ")
}
