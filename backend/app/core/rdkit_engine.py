from rdkit import Chem
from rdkit.Chem import Draw

def mol_info(smiles: str):
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return {"error": "invalid smiles"}

    return {
        "atoms": [a.GetSymbol() for a in mol.GetAtoms()],
        "bonds": mol.GetNumBonds(),
        "aromatic": any(a.GetIsAromatic() for a in mol.GetAtoms())
    }

def mol_svg(smiles: str):
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        return "<svg></svg>"

    return Draw.MolsToSVG(mol)