export namespace chemistry {
	
	export class BalanceResult {
	    original: string;
	    balanced: string;
	    coefficients: number[];
	    isBalanced: boolean;
	    elements: string[];
	    subscript: string;
	    latex: string;
	    error?: string;
	
	    static createFrom(source: any = {}) {
	        return new BalanceResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.original = source["original"];
	        this.balanced = source["balanced"];
	        this.coefficients = source["coefficients"];
	        this.isBalanced = source["isBalanced"];
	        this.elements = source["elements"];
	        this.subscript = source["subscript"];
	        this.latex = source["latex"];
	        this.error = source["error"];
	    }
	}
	export class FormulaResult {
	    original: string;
	    elements: Record<string, number>;
	    molecularWeight: number;
	    subscript: string;
	    latex: string;
	    isValid: boolean;
	    error?: string;
	
	    static createFrom(source: any = {}) {
	        return new FormulaResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.original = source["original"];
	        this.elements = source["elements"];
	        this.molecularWeight = source["molecularWeight"];
	        this.subscript = source["subscript"];
	        this.latex = source["latex"];
	        this.isValid = source["isValid"];
	        this.error = source["error"];
	    }
	}
	export class Ion {
	    formula: string;
	    symbol: string;
	    charge: number;
	    isCation: boolean;
	
	    static createFrom(source: any = {}) {
	        return new Ion(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.formula = source["formula"];
	        this.symbol = source["symbol"];
	        this.charge = source["charge"];
	        this.isCation = source["isCation"];
	    }
	}
	export class IonicEquationResult {
	    molecular: string;
	    fullIonic: string;
	    netIonic: string;
	    spectators: string[];
	    chargeBalanced: boolean;
	    reactantCharges: number;
	    productCharges: number;
	
	    static createFrom(source: any = {}) {
	        return new IonicEquationResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.molecular = source["molecular"];
	        this.fullIonic = source["fullIonic"];
	        this.netIonic = source["netIonic"];
	        this.spectators = source["spectators"];
	        this.chargeBalanced = source["chargeBalanced"];
	        this.reactantCharges = source["reactantCharges"];
	        this.productCharges = source["productCharges"];
	    }
	}
	export class RenderResult {
	    latex: string;
	    markdown: string;
	    html: string;
	    unicode: string;
	
	    static createFrom(source: any = {}) {
	        return new RenderResult(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.latex = source["latex"];
	        this.markdown = source["markdown"];
	        this.html = source["html"];
	        this.unicode = source["unicode"];
	    }
	}

}

export namespace plugin {
	
	export class Plugin {
	    name: string;
	    version: string;
	    description: string;
	    category: string;
	    enabled: boolean;
	    initialized: boolean;
	    error?: string;
	
	    static createFrom(source: any = {}) {
	        return new Plugin(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.version = source["version"];
	        this.description = source["description"];
	        this.category = source["category"];
	        this.enabled = source["enabled"];
	        this.initialized = source["initialized"];
	        this.error = source["error"];
	    }
	}

}

export namespace provider {
	
	export class CompoundInfo {
	    name: string;
	    nameCn: string;
	    formula: string;
	    molecularWeight: number;
	    casNumber: string;
	    smiles: string;
	    description: string;
	    source: string;
	
	    static createFrom(source: any = {}) {
	        return new CompoundInfo(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.nameCn = source["nameCn"];
	        this.formula = source["formula"];
	        this.molecularWeight = source["molecularWeight"];
	        this.casNumber = source["casNumber"];
	        this.smiles = source["smiles"];
	        this.description = source["description"];
	        this.source = source["source"];
	    }
	}
	export class Provider {
	    name: string;
	    type: string;
	    enabled: boolean;
	    priority: number;
	    baseUrl: string;
	    status: string;
	
	    static createFrom(source: any = {}) {
	        return new Provider(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.type = source["type"];
	        this.enabled = source["enabled"];
	        this.priority = source["priority"];
	        this.baseUrl = source["baseUrl"];
	        this.status = source["status"];
	    }
	}

}

