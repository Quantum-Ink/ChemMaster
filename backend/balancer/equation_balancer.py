import re
from sympy import Matrix, lcm

def parse_molecule(formula):
    """
    简化版分子解析：Fe2O3 → {'Fe':2,'O':3}
    """
    tokens = re.findall(r'([A-Z][a-z]?)(\d*)', formula)
    result = {}
    for elem, num in tokens:
        result[elem] = result.get(elem, 0) + (int(num) if num else 1)
    return result


def parse_side(side):
    return [parse_molecule(m.strip()) for m in side.split("+")]


def get_elements(molecules):
    elements = set()
    for mol in molecules:
        elements.update(mol.keys())
    return sorted(elements)


def build_matrix(reactants, products, elements):
    matrix = []

    for elem in elements:
        row = []

        # 反应物（+）
        for m in reactants:
            row.append(m.get(elem, 0))

        # 生成物（-）
        for m in products:
            row.append(-m.get(elem, 0))

        matrix.append(row)

    return Matrix(matrix)


def balance(equation):
    left, right = equation.split("->")

    reactants = parse_side(left)
    products = parse_side(right)

    elements = get_elements(reactants + products)

    matrix = build_matrix(reactants, products, elements)

    # 求零空间
    nullspace = matrix.nullspace()

    if not nullspace:
        return "无法配平"

    vec = nullspace[0]

    lcm_val = lcm([r.q for r in vec])  # 分母最小公倍数
    coeffs = vec * lcm_val
    coeffs = [abs(int(x)) for x in coeffs]

    left_count = len(reactants)

    left_side = coeffs[:left_count]
    right_side = coeffs[left_count:]

    def format_side(molecules, coeffs):
        return " + ".join(f"{c}{m}" for c, m in zip(coeffs, molecules))

    left_str = format_side([m for m in left.split("+")], left_side)
    right_str = format_side([m for m in right.split("+")], right_side)

    return f"{left_str} -> {right_str}"


if __name__ == "__main__":
    tests = [
        "Fe + O2 -> Fe2O3",
        "H2 + O2 -> H2O",
        "C + O2 -> CO2"
    ]

    for t in tests:
        print(balance(t))