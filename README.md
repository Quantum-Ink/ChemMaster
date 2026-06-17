# 🧪 ChemMaster

AI-powered chemistry equation editor supporting chemical formulas, equation balancing, LaTeX export, and Microsoft Word integration.

---

## 📌 Overview

ChemMaster is an open-source tool that helps users:

- Convert natural language into chemical equations
- Parse chemical formulas into structured formats
- Balance chemical equations automatically
- Export results to LaTeX format
- Integrate with Microsoft Word (Office Add-in ready)

---

## ✨ Features

### ⚗️ Chemical Formula Parsing

Convert raw formulas into structured representations:

- H2SO4 → H₂SO₄  
- Ca(OH)2 → Ca(OH)₂  
- NH4+ → NH₄⁺  

---

### ⚖️ Equation Balancing

Automatically balance chemical reactions:

- Example:
```
Fe + O2 -> Fe2O3
```
- Output:
```
4Fe + 3O2 -> 2Fe2O3
```
---

### 🧠 AI Reaction Generator

Convert natural language into chemical equations:

- Input:
```
硫酸和氢氧化钠反应
```
- Output:
```
H2SO4 + 2NaOH -> Na2SO4 + 2H2O
```
---

### 📐 LaTeX Export

Generate LaTeX-compatible chemical expressions:

---

### 📝 Word Integration (Planned)

Microsoft Word Office Add-in support for inserting formatted chemical equations directly into documents.

---

## 🏗️ Architecture
```
ChemMaster/
│
├── frontend/ React + TypeScript UI
├── backend/ FastAPI engine
├── ai/ Natural language processor
├── core/ parser + balancer
└── docs/
```
---

## 🚀 Tech Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI (Python)
- AI: OpenAI API / rule-based fallback
- Math: NumPy (for balancing equations)
- Export: LaTeX (mhchem format)
- Word: Office.js (planned)

---

## ⚙️ Installation

### 1、 Clone repository

```bash
git clone https://github.com/yourname/ChemMaster.git
cd ChemMaster
```
### 2、 Backend setup
- cd backend
- pip install -r requirements.txt
- uvicorn main:app --reload

### 3、 Frontend setup
- cd frontend
- npm install
- npm run dev

Frontend runs at:
  ```
  http://localhost:5173
  ```

## 🧪 Example Usage
- Input:
```
硫酸和氢氧化钠反应
```
- Output:
```
H2SO4 + 2NaOH -> Na2SO4 + 2H2O
```

## 📌 API Endpoints
- Parse chemical formula
- POST /parse
- Balance equation
- POST /balance
- AI generate equation
- POST /ai
- Convert to LaTeX
- POST /latex
  
## 🧠 Roadmap
- Full matrix-based equation balancing
- Real AI model integration (OpenAI / local LLM)
- Ionic equation decomposition
- Reaction classification engine
- Word Office Add-in support
- 3D molecular visualization (RDKit)
- Export to PDF / Word / LaTeX
  
## 🤝 Contributing
- Pull requests are welcome.
- If you want to contribute major changes, please open an issue first to discuss.

## 📜 License
  MIT License
