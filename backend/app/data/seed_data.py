"""
ChemMaster 种子数据
内置元素周期表 + 常见化合物
确保无网络环境下基本化学功能完全可用
"""

import logging

logger = logging.getLogger("chemmaster.seed")


# ====== 元素周期表（118 种元素） ======

ELEMENTS = [
    # (symbol, name_zh, name_en, atomic_number, atomic_mass, category)
    ("H", "氢", "Hydrogen", 1, 1.008, "非金属"),
    ("He", "氦", "Helium", 2, 4.003, "稀有气体"),
    ("Li", "锂", "Lithium", 3, 6.941, "碱金属"),
    ("Be", "铍", "Beryllium", 4, 9.012, "碱土金属"),
    ("B", "硼", "Boron", 5, 10.81, "类金属"),
    ("C", "碳", "Carbon", 6, 12.011, "非金属"),
    ("N", "氮", "Nitrogen", 7, 14.007, "非金属"),
    ("O", "氧", "Oxygen", 8, 15.999, "非金属"),
    ("F", "氟", "Fluorine", 9, 18.998, "卤素"),
    ("Ne", "氖", "Neon", 10, 20.180, "稀有气体"),
    ("Na", "钠", "Sodium", 11, 22.990, "碱金属"),
    ("Mg", "镁", "Magnesium", 12, 24.305, "碱土金属"),
    ("Al", "铝", "Aluminium", 13, 26.982, "金属"),
    ("Si", "硅", "Silicon", 14, 28.086, "类金属"),
    ("P", "磷", "Phosphorus", 15, 30.974, "非金属"),
    ("S", "硫", "Sulfur", 16, 32.065, "非金属"),
    ("Cl", "氯", "Chlorine", 17, 35.453, "卤素"),
    ("Ar", "氩", "Argon", 18, 39.948, "稀有气体"),
    ("K", "钾", "Potassium", 19, 39.098, "碱金属"),
    ("Ca", "钙", "Calcium", 20, 40.078, "碱土金属"),
    ("Sc", "钪", "Scandium", 21, 44.956, "过渡金属"),
    ("Ti", "钛", "Titanium", 22, 47.867, "过渡金属"),
    ("V", "钒", "Vanadium", 23, 50.942, "过渡金属"),
    ("Cr", "铬", "Chromium", 24, 51.996, "过渡金属"),
    ("Mn", "锰", "Manganese", 25, 54.938, "过渡金属"),
    ("Fe", "铁", "Iron", 26, 55.845, "过渡金属"),
    ("Co", "钴", "Cobalt", 27, 58.933, "过渡金属"),
    ("Ni", "镍", "Nickel", 28, 58.693, "过渡金属"),
    ("Cu", "铜", "Copper", 29, 63.546, "过渡金属"),
    ("Zn", "锌", "Zinc", 30, 65.380, "过渡金属"),
    ("Ga", "镓", "Gallium", 31, 69.723, "金属"),
    ("Ge", "锗", "Germanium", 32, 72.630, "类金属"),
    ("As", "砷", "Arsenic", 33, 74.922, "类金属"),
    ("Se", "硒", "Selenium", 34, 78.971, "非金属"),
    ("Br", "溴", "Bromine", 35, 79.904, "卤素"),
    ("Kr", "氪", "Krypton", 36, 83.798, "稀有气体"),
    ("Rb", "铷", "Rubidium", 37, 85.468, "碱金属"),
    ("Sr", "锶", "Strontium", 38, 87.620, "碱土金属"),
    ("Y", "钇", "Yttrium", 39, 88.906, "过渡金属"),
    ("Zr", "锆", "Zirconium", 40, 91.224, "过渡金属"),
    ("Nb", "铌", "Niobium", 41, 92.906, "过渡金属"),
    ("Mo", "钼", "Molybdenum", 42, 95.950, "过渡金属"),
    ("Tc", "锝", "Technetium", 43, 98.000, "过渡金属"),
    ("Ru", "钌", "Ruthenium", 44, 101.07, "过渡金属"),
    ("Rh", "铑", "Rhodium", 45, 102.91, "过渡金属"),
    ("Pd", "钯", "Palladium", 46, 106.42, "过渡金属"),
    ("Ag", "银", "Silver", 47, 107.87, "过渡金属"),
    ("Cd", "镉", "Cadmium", 48, 112.41, "过渡金属"),
    ("In", "铟", "Indium", 49, 114.82, "金属"),
    ("Sn", "锡", "Tin", 50, 118.71, "金属"),
    ("Sb", "锑", "Antimony", 51, 121.76, "类金属"),
    ("Te", "碲", "Tellurium", 52, 127.60, "类金属"),
    ("I", "碘", "Iodine", 53, 126.90, "卤素"),
    ("Xe", "氙", "Xenon", 54, 131.29, "稀有气体"),
    ("Cs", "铯", "Caesium", 55, 132.91, "碱金属"),
    ("Ba", "钡", "Barium", 56, 137.33, "碱土金属"),
    ("La", "镧", "Lanthanum", 57, 138.91, "镧系"),
    ("Ce", "铈", "Cerium", 58, 140.12, "镧系"),
    ("Pr", "镨", "Praseodymium", 59, 140.91, "镧系"),
    ("Nd", "钕", "Neodymium", 60, 144.24, "镧系"),
    ("Pm", "钷", "Promethium", 61, 145.00, "镧系"),
    ("Sm", "钐", "Samarium", 62, 150.36, "镧系"),
    ("Eu", "铕", "Europium", 63, 151.96, "镧系"),
    ("Gd", "钆", "Gadolinium", 64, 157.25, "镧系"),
    ("Tb", "铽", "Terbium", 65, 158.93, "镧系"),
    ("Dy", "镝", "Dysprosium", 66, 162.50, "镧系"),
    ("Ho", "钬", "Holmium", 67, 164.93, "镧系"),
    ("Er", "铒", "Erbium", 68, 167.26, "镧系"),
    ("Tm", "铥", "Thulium", 69, 168.93, "镧系"),
    ("Yb", "镱", "Ytterbium", 70, 173.05, "镧系"),
    ("Lu", "镥", "Lutetium", 71, 174.97, "镧系"),
    ("Hf", "铪", "Hafnium", 72, 178.49, "过渡金属"),
    ("Ta", "钽", "Tantalum", 73, 180.95, "过渡金属"),
    ("W", "钨", "Tungsten", 74, 183.84, "过渡金属"),
    ("Re", "铼", "Rhenium", 75, 186.21, "过渡金属"),
    ("Os", "锇", "Osmium", 76, 190.23, "过渡金属"),
    ("Ir", "铱", "Iridium", 77, 192.22, "过渡金属"),
    ("Pt", "铂", "Platinum", 78, 195.08, "过渡金属"),
    ("Au", "金", "Gold", 79, 196.97, "过渡金属"),
    ("Hg", "汞", "Mercury", 80, 200.59, "过渡金属"),
    ("Tl", "铊", "Thallium", 81, 204.38, "金属"),
    ("Pb", "铅", "Lead", 82, 207.20, "金属"),
    ("Bi", "铋", "Bismuth", 83, 208.98, "金属"),
    ("Po", "钋", "Polonium", 84, 209.00, "金属"),
    ("At", "砹", "Astatine", 85, 210.00, "卤素"),
    ("Rn", "氡", "Radon", 86, 222.00, "稀有气体"),
    ("Fr", "钫", "Francium", 87, 223.00, "碱金属"),
    ("Ra", "镭", "Radium", 88, 226.00, "碱土金属"),
    ("Ac", "锕", "Actinium", 89, 227.00, "锕系"),
    ("Th", "钍", "Thorium", 90, 232.04, "锕系"),
    ("Pa", "镤", "Protactinium", 91, 231.04, "锕系"),
    ("U", "铀", "Uranium", 92, 238.03, "锕系"),
    ("Np", "镎", "Neptunium", 93, 237.00, "锕系"),
    ("Pu", "钚", "Plutonium", 94, 244.00, "锕系"),
    ("Am", "镅", "Americium", 95, 243.00, "锕系"),
    ("Cm", "锔", "Curium", 96, 247.00, "锕系"),
    ("Bk", "锫", "Berkelium", 97, 247.00, "锕系"),
    ("Cf", "锎", "Californium", 98, 251.00, "锕系"),
    ("Es", "锿", "Einsteinium", 99, 252.00, "锕系"),
    ("Fm", "镄", "Fermium", 100, 257.00, "锕系"),
    ("Md", "钔", "Mendelevium", 101, 258.00, "锕系"),
    ("No", "锘", "Nobelium", 102, 259.00, "锕系"),
    ("Lr", "铹", "Lawrencium", 103, 266.00, "锕系"),
    ("Rf", "𨧀", "Rutherfordium", 104, 267.00, "过渡金属"),
    ("Db", "𨭎", "Dubnium", 105, 268.00, "过渡金属"),
    ("Sg", "𨭆", "Seaborgium", 106, 269.00, "过渡金属"),
    ("Bh", "𨨏", "Bohrium", 107, 270.00, "过渡金属"),
    ("Hs", "𨭆", "Hassium", 108, 277.00, "过渡金属"),
    ("Mt", "鿏", "Meitnerium", 109, 278.00, "过渡金属"),
    ("Ds", "𫟼", "Darmstadtium", 110, 281.00, "过渡金属"),
    ("Rg", "𬬭", "Roentgenium", 111, 282.00, "过渡金属"),
    ("Cn", "鿔", "Copernicium", 112, 285.00, "过渡金属"),
    ("Nh", "鿭", "Nihonium", 113, 286.00, "金属"),
    ("Fl", "𫓧", "Flerovium", 114, 289.00, "金属"),
    ("Mc", "镆", "Moscovium", 115, 290.00, "金属"),
    ("Lv", "𫟷", "Livermorium", 116, 293.00, "金属"),
    ("Ts", "鿬", "Tennessine", 117, 294.00, "卤素"),
    ("Og", "鿫", "Oganesson", 118, 294.00, "稀有气体"),
]


# ====== 常见化合物（100+ 种） ======

COMPOUNDS = [
    # (name_zh, name_en, formula, smiles, molecular_weight, cas_number)
    ("水", "Water", "H2O", "O", 18.015, "7732-18-5"),
    ("二氧化碳", "Carbon Dioxide", "CO2", "O=C=O", 44.010, "124-38-9"),
    ("氯化钠", "Sodium Chloride", "NaCl", "[Na+].[Cl-]", 58.443, "7647-14-5"),
    ("硫酸", "Sulfuric Acid", "H2SO4", "OS(O)(=O)=O", 98.079, "7664-93-9"),
    ("盐酸", "Hydrochloric Acid", "HCl", "Cl", 36.461, "7647-01-0"),
    ("硝酸", "Nitric Acid", "HNO3", "O[N+](=O)[O-]", 63.013, "7697-37-2"),
    ("氢氧化钠", "Sodium Hydroxide", "NaOH", "[Na+].[OH-]", 40.000, "1310-73-2"),
    ("氢氧化钙", "Calcium Hydroxide", "Ca(OH)2", "[Ca+2].[OH-].[OH-]", 74.093, "1305-62-0"),
    ("碳酸钙", "Calcium Carbonate", "CaCO3", "C(=O)([O-])[O-].[Ca+2]", 100.087, "471-34-1"),
    ("碳酸钠", "Sodium Carbonate", "Na2CO3", "C(=O)([O-])[O-].[Na+].[Na+]", 105.989, "497-19-8"),
    ("碳酸氢钠", "Sodium Bicarbonate", "NaHCO3", "OC(=O)[O-].[Na+]", 84.007, "144-55-8"),
    ("氯化钾", "Potassium Chloride", "KCl", "[K+].[Cl-]", 74.551, "7447-40-7"),
    ("氯化钙", "Calcium Chloride", "CaCl2", "[Ca+2].[Cl-].[Cl-]", 110.984, "10043-52-4"),
    ("硫酸铜", "Copper Sulfate", "CuSO4", "[Cu+2].S(=O)(=O)[O-].[O-]", 159.609, "7758-98-7"),
    ("硫酸亚铁", "Ferrous Sulfate", "FeSO4", "[Fe+2].S(=O)(=O)[O-].[O-]", 151.908, "7782-63-0"),
    ("硝酸银", "Silver Nitrate", "AgNO3", "[Ag+].[N+](=O)([O-])[O-]", 169.873, "7761-88-8"),
    ("高锰酸钾", "Potassium Permanganate", "KMnO4", "[K+].[O-][Mn](=O)(=O)=O", 158.034, "7722-64-7"),
    ("过氧化氢", "Hydrogen Peroxide", "H2O2", "OO", 34.015, "7722-84-1"),
    ("氨", "Ammonia", "NH3", "N", 17.031, "7664-41-7"),
    ("甲烷", "Methane", "CH4", "C", 16.043, "74-82-8"),
    ("乙烷", "Ethane", "C2H6", "CC", 30.069, "74-84-0"),
    ("乙烯", "Ethylene", "C2H4", "C=C", 28.054, "74-85-1"),
    ("乙炔", "Acetylene", "C2H2", "C#C", 26.038, "74-86-2"),
    ("丙烷", "Propane", "C3H8", "CCC", 44.096, "74-98-6"),
    ("丁烷", "Butane", "C4H10", "CCCC", 58.122, "106-97-8"),
    ("苯", "Benzene", "C6H6", "c1ccccc1", 78.114, "71-43-2"),
    ("甲苯", "Toluene", "C7H8", "Cc1ccccc1", 92.141, "108-88-3"),
    ("甲醇", "Methanol", "CH3OH", "CO", 32.042, "67-56-1"),
    ("乙醇", "Ethanol", "C2H5OH", "CCO", 46.068, "64-17-5"),
    ("丙醇", "Propanol", "C3H7OH", "CCCO", 60.095, "71-23-8"),
    ("乙二醇", "Ethylene Glycol", "C2H6O2", "OCCO", 62.068, "107-21-1"),
    ("丙三醇", "Glycerol", "C3H8O3", "OCC(O)CO", 92.094, "56-81-5"),
    ("甲醛", "Formaldehyde", "CH2O", "C=O", 30.026, "50-00-0"),
    ("乙醛", "Acetaldehyde", "C2H4O", "CC=O", 44.053, "75-07-0"),
    ("丙酮", "Acetone", "C3H6O", "CC(=O)C", 58.079, "67-64-1"),
    ("乙酸", "Acetic Acid", "C2H4O2", "CC(=O)O", 60.052, "64-19-7"),
    ("草酸", "Oxalic Acid", "C2H2O4", "OC(=O)C(=O)O", 90.035, "144-62-7"),
    ("柠檬酸", "Citric Acid", "C6H8O7", "OC(=O)CC(O)(CC(=O)O)C(=O)O", 192.124, "77-92-9"),
    ("苯酚", "Phenol", "C6H6O", "Oc1ccccc1", 94.113, "108-95-2"),
    ("苯甲酸", "Benzoic Acid", "C7H6O2", "OC(=O)c1ccccc1", 122.123, "65-85-0"),
    ("乙酸乙酯", "Ethyl Acetate", "C4H8O2", "CCOC(=O)C", 88.106, "141-78-6"),
    ("乙酸钠", "Sodium Acetate", "NaC2H3O2", "CC(=O)[O-].[Na+]", 82.034, "127-09-3"),
    ("尿素", "Urea", "CH4N2O", "NC(=O)N", 60.056, "57-13-6"),
    ("葡萄糖", "Glucose", "C6H12O6", "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O", 180.156, "50-99-7"),
    ("蔗糖", "Sucrose", "C12H22O11", "OC[C@H]1OC(O[C@@]2(CO)OC[C@@H](O)[C@H]2O)[C@H](O)[C@@H](O)[C@@H]1O", 342.296, "57-50-1"),
    ("淀粉", "Starch", "(C6H10O5)n", None, None, "9005-25-8"),
    ("纤维素", "Cellulose", "(C6H10O5)n", None, None, "9004-34-6"),
    ("氨基酸(甘氨酸)", "Glycine", "C2H5NO2", "NCC(=O)O", 75.033, "56-40-6"),
    ("氨基酸(丙氨酸)", "Alanine", "C3H7NO2", "CC(N)C(=O)O", 89.093, "56-41-7"),
    ("胆固醇", "Cholesterol", "C27H46O", "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C", 386.654, "57-88-5"),
    ("阿司匹林", "Aspirin", "C9H8O4", "CC(=O)Oc1ccccc1C(=O)O", 180.159, "50-78-2"),
    ("咖啡因", "Caffeine", "C8H10N4O2", "Cn1c(=O)c2c(ncn2C)n(C)c1=O", 194.191, "58-08-2"),
    ("维生素C", "Vitamin C", "C6H8O6", "OC[C@H](O)[C@H]1OC(=O)C(O)=C1O", 176.124, "50-81-7"),
    ("氯仿", "Chloroform", "CHCl3", "ClC(Cl)Cl", 119.378, "67-66-3"),
    ("四氯化碳", "Carbon Tetrachloride", "CCl4", "ClC(Cl)(Cl)Cl", 153.823, "56-23-5"),
    ("二氯甲烷", "Dichloromethane", "CH2Cl2", "ClCCl", 84.933, "75-09-2"),
    ("氯乙烯", "Vinyl Chloride", "C2H3Cl", "C=CCl", 62.498, "75-01-4"),
    ("溴乙烷", "Bromoethane", "C2H5Br", "CCBr", 108.965, "74-96-4"),
    ("碘甲烷", "Iodomethane", "CH3I", "CI", 141.939, "74-88-4"),
    ("环己烷", "Cyclohexane", "C6H12", "C1CCCCC1", 84.162, "110-82-7"),
    ("环戊烷", "Cyclopentane", "C5H10", "C1CCCC1", 70.135, "287-92-3"),
    ("萘", "Naphthalene", "C10H8", "c1ccc2ccccc2c1", 128.174, "91-20-3"),
    ("蒽", "Anthracene", "C14H10", "c1ccc2cc3ccccc3cc2c1", 178.234, "120-12-7"),
    ("吡啶", "Pyridine", "C5H5N", "c1ccncc1", 79.101, "110-86-1"),
    ("呋喃", "Furan", "C4H4O", "c1ccoc1", 68.074, "110-00-9"),
    ("噻吩", "Thiophene", "C4H4S", "c1ccsc1", 84.140, "110-02-1"),
    ("吡咯", "Pyrrole", "C4H5N", "c1cc[nH]c1", 67.090, "109-97-7"),
    ("吲哚", "Indole", "C8H7N", "c1ccc2[nH]ccc2c1", 117.151, "120-72-9"),
    ("喹啉", "Quinoline", "C9H7N", "c1ccc2ncccc2c1", 129.161, "91-22-5"),
    ("硝基苯", "Nitrobenzene", "C6H5NO2", "c1ccc(cc1)[N+](=O)[O-]", 123.111, "98-95-3"),
    ("苯胺", "Aniline", "C6H7N", "Nc1ccccc1", 93.129, "62-53-3"),
    ("氯苯", "Chlorobenzene", "C6H5Cl", "Clc1ccccc1", 112.559, "108-90-7"),
    ("氟化氢", "Hydrogen Fluoride", "HF", "F", 20.006, "7664-39-3"),
    ("硫化氢", "Hydrogen Sulfide", "H2S", "S", 34.081, "7783-06-4"),
    ("一氧化碳", "Carbon Monoxide", "CO", "[C-]#[O+]", 28.010, "630-08-0"),
    ("一氧化氮", "Nitric Oxide", "NO", "[N]=O", 30.006, "10102-43-9"),
    ("二氧化氮", "Nitrogen Dioxide", "NO2", "[O][N]=O", 46.006, "10102-44-0"),
    ("二氧化硫", "Sulfur Dioxide", "SO2", "O=S=O", 64.064, "7446-09-5"),
    ("三氧化硫", "Sulfur Trioxide", "SO3", "O=S(=O)=O", 80.063, "7446-11-9"),
    ("五氧化二磷", "Phosphorus Pentoxide", "P2O5", "O=P1(OP(=O)(O1)O)O", 141.944, "1314-56-3"),
    ("氧化钙", "Calcium Oxide", "CaO", "O=[Ca]", 56.077, "1305-78-8"),
    ("氧化铁", "Iron(III) Oxide", "Fe2O3", "O=[Fe]O[Fe]=O", 159.687, "1309-37-1"),
    ("氧化铝", "Aluminium Oxide", "Al2O3", "O=[Al]O[Al]=O", 101.961, "1344-28-1"),
    ("氧化铜", "Copper(II) Oxide", "CuO", "[Cu]=O", 79.545, "1317-38-0"),
    ("氢氧化铝", "Aluminium Hydroxide", "Al(OH)3", "[Al+3].[OH-].[OH-].[OH-]", 78.004, "21645-51-2"),
    ("氢氧化铁", "Iron(III) Hydroxide", "Fe(OH)3", "[Fe+3].[OH-].[OH-].[OH-]", 106.867, "1309-33-7"),
    ("硫化铜", "Copper(II) Sulfide", "CuS", "[Cu+2].[S-2]", 95.611, "1317-40-4"),
    ("硫化铅", "Lead(II) Sulfide", "PbS", "[Pb+2].[S-2]", 239.300, "1314-87-0"),
    ("氯化银", "Silver Chloride", "AgCl", "[Ag+].[Cl-]", 143.321, "7783-90-6"),
    ("溴化银", "Silver Bromide", "AgBr", "[Ag+].[Br-]", 187.772, "7785-23-1"),
    ("碘化银", "Silver Iodide", "AgI", "[Ag+].[I-]", 234.773, "7783-96-2"),
    ("硫酸钡", "Barium Sulfate", "BaSO4", "[Ba+2].S(=O)(=O)[O-].[O-]", 233.390, "7727-43-7"),
    ("硫酸钙", "Calcium Sulfate", "CaSO4", "[Ca+2].S(=O)(=O)[O-].[O-]", 136.141, "7778-18-9"),
    ("磷酸钙", "Calcium Phosphate", "Ca3(PO4)2", "[Ca+2].[Ca+2].[Ca+2].[O-]P(=O)([O-])[O-].[O-]P(=O)([O-])[O-]", 310.177, "7758-87-4"),
    ("氯化铵", "Ammonium Chloride", "NH4Cl", "[NH4+].[Cl-]", 53.491, "12125-02-9"),
    ("碳酸铵", "Ammonium Carbonate", "(NH4)2CO3", "[NH4+].[NH4+].C(=O)([O-])[O-]", 96.086, "506-87-6"),
    ("硝酸铵", "Ammonium Nitrate", "NH4NO3", "[NH4+].[N+](=O)([O-])[O-]", 80.043, "6484-52-2"),
    ("硫酸铵", "Ammonium Sulfate", "(NH4)2SO4", "[NH4+].[NH4+].S(=O)(=O)[O-].[O-]", 132.134, "7783-20-2"),
    ("磷酸", "Phosphoric Acid", "H3PO4", "OP(=O)(O)O", 97.995, "7664-38-2"),
    ("硅酸", "Silicic Acid", "H4SiO4", "O[Si](O)(O)O", 96.115, "10193-36-9"),
    ("次氯酸", "Hypochlorous Acid", "HClO", "OCl", 52.460, "7790-92-3"),
    ("氯酸", "Chloric Acid", "HClO3", "OCl(=O)=O", 84.459, "7790-93-4"),
    ("高氯酸", "Perchloric Acid", "HClO4", "OCl(=O)(=O)=O", 100.459, "7601-90-3"),
    ("重铬酸钾", "Potassium Dichromate", "K2Cr2O7", "[K+].[K+].[O-][Cr](=O)(=O)O[Cr](=O)(=O)[O-]", 294.185, "7778-50-9"),
    ("氯化铁", "Iron(III) Chloride", "FeCl3", "[Fe+3].[Cl-].[Cl-].[Cl-]", 162.204, "7705-08-0"),
    ("氯化亚铁", "Iron(II) Chloride", "FeCl2", "[Fe+2].[Cl-].[Cl-]", 126.751, "7758-94-3"),
    ("硫酸镁", "Magnesium Sulfate", "MgSO4", "[Mg+2].S(=O)(=O)[O-].[O-]", 120.368, "7487-88-9"),
    ("氯化镁", "Magnesium Chloride", "MgCl2", "[Mg+2].[Cl-].[Cl-]", 95.211, "7786-30-3"),
]

# ====== 常见反应方程式 ======

REACTIONS = [
    # (equation, reaction_type)
    ("2H2 + O2 -> 2H2O", "combustion"),
    ("CH4 + 2O2 -> CO2 + 2H2O", "combustion"),
    ("2C2H6 + 7O2 -> 4CO2 + 6H2O", "combustion"),
    ("C2H5OH + 3O2 -> 2CO2 + 3H2O", "combustion"),
    ("Fe + CuSO4 -> FeSO4 + Cu", "displacement"),
    ("Zn + H2SO4 -> ZnSO4 + H2", "displacement"),
    ("Na + H2O -> NaOH + H2", "displacement"),
    ("HCl + NaOH -> NaCl + H2O", "neutralization"),
    ("H2SO4 + 2NaOH -> Na2SO4 + 2H2O", "neutralization"),
    ("CaCO3 -> CaO + CO2", "decomposition"),
    ("2H2O -> 2H2 + O2", "decomposition"),
    ("2KMnO4 -> K2MnO4 + MnO2 + O2", "decomposition"),
    ("CaO + H2O -> Ca(OH)2", "synthesis"),
    ("2Mg + O2 -> 2MgO", "synthesis"),
    ("4Fe + 3O2 -> 2Fe2O3", "synthesis"),
    ("BaCl2 + Na2SO4 -> BaSO4 + 2NaCl", "double_displacement"),
    ("AgNO3 + NaCl -> AgCl + NaNO3", "double_displacement"),
    ("Fe2O3 + 3CO -> 2Fe + 3CO2", "redox"),
    ("CuO + H2 -> Cu + H2O", "redox"),
    ("Zn + CuSO4 -> ZnSO4 + Cu", "displacement"),
]


async def seed_database(db) -> None:
    """
    向数据库填充种子数据
    仅在表为空时执行（不会覆盖已有数据）
    """
    # 检查是否已有数据
    element_count = await db.count("elements")
    if element_count > 0:
        logger.info(f"Database already has {element_count} elements, skipping seed")
        return

    logger.info("Seeding database with initial data...")

    # 插入元素
    await db.executemany(
        "INSERT OR IGNORE INTO elements (symbol, name_zh, name_en, atomic_number, atomic_mass, category) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ELEMENTS
    )

    # 插入化合物
    await db.executemany(
        "INSERT OR IGNORE INTO compounds (name_zh, name, formula, smiles, molecular_weight, cas_number) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(c[0], c[1], c[2], c[3], c[4], c[5]) for c in COMPOUNDS]
    )

    # 插入反应方程式
    await db.executemany(
        "INSERT OR IGNORE INTO reactions (equation, reaction_type) VALUES (?, ?)",
        [(r[0], r[1]) for r in REACTIONS]
    )

    logger.info(f"Seeded: {len(ELEMENTS)} elements, {len(COMPOUNDS)} compounds, {len(REACTIONS)} reactions")
