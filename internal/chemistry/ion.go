package chemistry

import (
	"fmt"
	"math"
	"regexp"
	"sort"
	"strings"
)

// Ion represents a chemical ion.
type Ion struct {
	Formula  string `json:"formula"`
	Symbol   string `json:"symbol"`
	Charge   int    `json:"charge"`
	IsCation bool   `json:"isCation"`
}

// Strong acids that fully dissociate.
var strongAcids = map[string]bool{
	"HCl": true, "HBr": true, "HI": true, "HNO3": true,
	"H2SO4": true, "HClO4": true, "HClO3": true,
}

// Strong bases that fully dissociate.
var strongBases = map[string]bool{
	"NaOH": true, "KOH": true, "Ca(OH)2": true, "Ba(OH)2": true,
}

// Soluble salts that fully dissociate.
var solubleSalts = map[string]bool{
	"NaCl": true, "NaBr": true, "NaI": true, "NaNO3": true, "Na2SO4": true,
	"Na2CO3": true, "NaOH": true, "NaHCO3": true, "Na2SO3": true,
	"KCl": true, "KBr": true, "KI": true, "KNO3": true, "K2SO4": true,
	"K2CO3": true, "KOH": true, "KMnO4": true, "K2CrO4": true,
	"NH4Cl": true, "NH4NO3": true, "(NH4)2SO4": true,
	"AgNO3": true, "Ca(NO3)2": true, "Mg(NO3)2": true,
	"Fe(NO3)2": true, "Fe(NO3)3": true, "Cu(NO3)2": true,
	"Zn(NO3)2": true, "Pb(NO3)2": true, "Al(NO3)3": true,
	"CaCl2": true, "MgCl2": true, "FeCl2": true, "FeCl3": true,
	"CuCl2": true, "ZnCl2": true, "AlCl3": true, "BaCl2": true,
	"MgSO4": true, "FeSO4": true, "CuSO4": true, "ZnSO4": true,
	"Na3PO4": true, "K3PO4": true,
	"CH3COONa": true, "NaCH3COO": true,
}

// Insoluble compounds (precipitates).
var insoluble = map[string]bool{
	"AgCl": true, "AgBr": true, "AgI": true, "Ag2S": true,
	"BaSO4": true, "BaCO3": true, "BaSO3": true,
	"CaCO3": true, "CaSO3": true, "Ca3(PO4)2": true,
	"PbCl2": true, "PbI2": true, "PbS": true, "PbSO4": true,
	"CuS": true, "Cu(OH)2": true, "CuCO3": true,
	"Fe(OH)3": true, "Fe(OH)2": true, "FeS": true,
	"Al(OH)3": true, "Al2O3": true,
	"Mg(OH)2": true, "MgCO3": true,
	"ZnS": true, "Zn(OH)2": true, "ZnCO3": true,
	"HgS": true, "Hg2Cl2": true,
	"MnS": true, "Mn(OH)2": true,
}

// Gases that don't dissociate.
var gases = map[string]bool{
	"H2": true, "O2": true, "N2": true, "Cl2": true, "CO2": true,
	"CO": true, "SO2": true, "SO3": true, "NO": true, "NO2": true,
	"NH3": true, "HCl": true, "HBr": true, "HI": true, "HF": true,
	"CH4": true, "H2S": true,
}

// Weak electrolytes.
var weakElectrolytes = map[string]bool{
	"H2O": true, "HF": true, "HCN": true, "H2S": true,
	"H2CO3": true, "H2SO3": true, "H3PO4": true,
	"CH3COOH": true, "NH3·H2O": true,
}

// ionSuffixRegex matches ion patterns like SO4^2-, Fe3+.
// Pre-compiled to avoid recompilation in hot paths.
var ionSuffixRegex = regexp.MustCompile(`\^[0-9]*[+-]`)

// chargeRegex matches charge patterns at end of string.
var chargeRegex = regexp.MustCompile(`\^?(\d*)([+-])$`)

// ionParseRegex matches ion strings for ParseIon.
var ionParseRegex = regexp.MustCompile(`^(.+?)(\d*)([+-])$`)

// DissociationMap maps compounds to their ions.
var dissociationMap = map[string][]string{
	"HCl": {"H+", "Cl-"}, "HBr": {"H+", "Br-"}, "HI": {"H+", "I-"},
	"HNO3": {"H+", "NO3-"}, "H2SO4": {"2H+", "SO4^2-"},
	"HClO4": {"H+", "ClO4-"}, "HClO3": {"H+", "ClO3-"},
	"NaOH": {"Na+", "OH-"}, "KOH": {"K+", "OH-"},
	"Ca(OH)2": {"Ca^2+", "2OH-"}, "Ba(OH)2": {"Ba^2+", "2OH-"},
	"NaCl": {"Na+", "Cl-"}, "NaBr": {"Na+", "Br-"}, "NaI": {"Na+", "I-"},
	"NaNO3": {"Na+", "NO3-"}, "Na2SO4": {"2Na+", "SO4^2-"},
	"Na2CO3": {"2Na+", "CO3^2-"}, "Na3PO4": {"3Na+", "PO4^3-"},
	"NaHCO3": {"Na+", "HCO3-"}, "Na2SO3": {"2Na+", "SO3^2-"},
	"CH3COONa": {"Na+", "CH3COO-"},
	"KCl": {"K+", "Cl-"}, "KBr": {"K+", "Br-"}, "KI": {"K+", "I-"},
	"KNO3": {"K+", "NO3-"}, "K2SO4": {"2K+", "SO4^2-"},
	"K2CO3": {"2K+", "CO3^2-"}, "K3PO4": {"3K+", "PO4^3-"},
	"KMnO4": {"K+", "MnO4-"}, "K2CrO4": {"2K+", "CrO4^2-"},
	"NH4Cl": {"NH4+", "Cl-"}, "NH4NO3": {"NH4+", "NO3-"},
	"(NH4)2SO4": {"2NH4+", "SO4^2-"},
	"AgNO3": {"Ag+", "NO3-"},
	"Ca(NO3)2": {"Ca^2+", "2NO3-"}, "Mg(NO3)2": {"Mg^2+", "2NO3-"},
	"Fe(NO3)2": {"Fe^2+", "2NO3-"}, "Fe(NO3)3": {"Fe^3+", "3NO3-"},
	"Cu(NO3)2": {"Cu^2+", "2NO3-"}, "Zn(NO3)2": {"Zn^2+", "2NO3-"},
	"Al(NO3)3": {"Al^3+", "3NO3-"},
	"CaCl2": {"Ca^2+", "2Cl-"}, "MgCl2": {"Mg^2+", "2Cl-"},
	"FeCl2": {"Fe^2+", "2Cl-"}, "FeCl3": {"Fe^3+", "3Cl-"},
	"CuCl2": {"Cu^2+", "2Cl-"}, "ZnCl2": {"Zn^2+", "2Cl-"},
	"AlCl3": {"Al^3+", "3Cl-"}, "BaCl2": {"Ba^2+", "2Cl-"},
	"MgSO4": {"Mg^2+", "SO4^2-"}, "FeSO4": {"Fe^2+", "SO4^2-"},
	"CuSO4": {"Cu^2+", "SO4^2-"}, "ZnSO4": {"Zn^2+", "SO4^2-"},
}

// IonEngine provides ionic equation processing.
type IonEngine struct {
	fe       *FormulaEngine
	balancer *EquationBalancer
}

// NewIonEngine creates a new IonEngine.
func NewIonEngine() *IonEngine {
	return &IonEngine{
		fe:       NewFormulaEngine(),
		balancer: NewEquationBalancer(),
	}
}

// Analyze converts a molecular equation to ionic forms.
func (ie *IonEngine) Analyze(equation string) (*IonicEquationResult, error) {
	// Parse equation
	reactants, products, sep, err := ie.balancer.parseEquation(equation)
	if err != nil {
		return nil, err
	}

	result := &IonicEquationResult{}

	// Build full ionic equation
	var fullIonicR, fullIonicP []string
	var netIonicR, netIonicP []string
	spectatorSet := make(map[string]bool)

	// Process reactants
	rIons := make([]string, 0)
	for _, term := range reactants {
		_, formula := ie.balancer.extractCoeff(term)
		ions := ie.dissociate(formula)
		fullIonicR = append(fullIonicR, ions...)
		for _, ion := range ions {
			if ie.isIon(ion) {
				rIons = append(rIons, ion)
			}
		}
	}

	// Process products
	pIons := make([]string, 0)
	for _, term := range products {
		_, formula := ie.balancer.extractCoeff(term)
		ions := ie.dissociate(formula)
		fullIonicP = append(fullIonicP, ions...)
		for _, ion := range ions {
			if ie.isIon(ion) {
				pIons = append(pIons, ion)
			}
		}
	}

	// Find spectator ions (appear on both sides)
	rIonSet := make(map[string]bool)
	for _, ion := range rIons {
		rIonSet[ion] = true
	}
	for _, ion := range pIons {
		if rIonSet[ion] {
			spectatorSet[ion] = true
		}
	}

	spectators := make([]string, 0, len(spectatorSet))
	for s := range spectatorSet {
		spectators = append(spectators, s)
	}
	sort.Strings(spectators)
	result.Spectators = spectators

	// Build net ionic (remove spectators)
	for _, ion := range fullIonicR {
		if !spectatorSet[ion] {
			netIonicR = append(netIonicR, ion)
		}
	}
	for _, ion := range fullIonicP {
		if !spectatorSet[ion] {
			netIonicP = append(netIonicP, ion)
		}
	}

	// Format equations
	result.Molecular = equation
	result.FullIonic = strings.Join(fullIonicR, " + ") + " " + sep + " " + strings.Join(fullIonicP, " + ")
	result.NetIonic = strings.Join(netIonicR, " + ") + " " + sep + " " + strings.Join(netIonicP, " + ")

	// Check charge balance
	rCharge := ie.totalCharge(fullIonicR)
	pCharge := ie.totalCharge(fullIonicP)
	result.ReactantChg = rCharge
	result.ProductChg = pCharge
	result.ChargeOK = rCharge == pCharge

	return result, nil
}

// dissociate splits a compound into ions if it's a strong electrolyte.
func (ie *IonEngine) dissociate(formula string) []string {
	if formula == "H2O" {
		return []string{"H2O"}
	}
	if weakElectrolytes[formula] || gases[formula] || insoluble[formula] {
		return []string{formula}
	}
	if ions, ok := dissociationMap[formula]; ok {
		return ions
	}
	return []string{formula}
}

// isIon checks if a term is an ion (e.g. "H+", "SO4^2-").
func (ie *IonEngine) isIon(term string) bool {
	return strings.HasSuffix(term, "+") || strings.HasSuffix(term, "-") ||
		ionSuffixRegex.MatchString(term)
}

// totalCharge calculates the total charge of a list of ionic terms.
func (ie *IonEngine) totalCharge(terms []string) int {
	total := 0
	for _, term := range terms {
		coeff, formula := ie.balancer.extractCoeff(term)
		charge := ie.getCharge(formula)
		total += charge * coeff
	}
	return total
}

// getCharge extracts the charge from an ion formula like "SO4^2-" → -2, "Fe3+" → 3.
func (ie *IonEngine) getCharge(formula string) int {
	matches := chargeRegex.FindStringSubmatch(formula)
	if matches == nil {
		return 0
	}
	sign := 1
	if matches[2] == "-" {
		sign = -1
	}
	if matches[1] == "" {
		return sign
	}
	val := 0
	fmt.Sscanf(matches[1], "%d", &val)
	return val * sign
}

// BalanceIonEquation balances an ionic equation.
func (ie *IonEngine) BalanceIonEquation(equation string) BalanceResult {
	return ie.balancer.Balance(equation)
}

// ParseIon parses an ion string like "SO4^2-" into an Ion struct.
func (ie *IonEngine) ParseIon(ionStr string) Ion {
	ion := Ion{Formula: ionStr}

	matches := ionParseRegex.FindStringSubmatch(ionStr)
	if matches == nil {
		ion.Symbol = ionStr
		return ion
	}

	ion.Symbol = matches[1]
	sign := 1
	if matches[3] == "-" {
		sign = -1
	}
	if matches[2] == "" {
		ion.Charge = sign
	} else {
		val := 0
		fmt.Sscanf(matches[2], "%d", &val)
		ion.Charge = val * sign
	}
	ion.IsCation = ion.Charge > 0
	return ion
}

// ToUnicodeCharge formats a charge as Unicode superscript.
func ToUnicodeCharge(charge int) string {
	supMap := map[int]string{
		1: "⁺", 2: "²⁺", 3: "³⁺", 4: "⁴⁺",
		-1: "⁻", -2: "²⁻", -3: "³⁻", -4: "⁴⁻",
	}
	if s, ok := supMap[charge]; ok {
		return s
	}
	if charge > 0 {
		return fmt.Sprintf("%d⁺", charge)
	}
	return fmt.Sprintf("%d⁻", int(math.Abs(float64(charge))))
}
