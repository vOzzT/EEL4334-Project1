import itertools
import os


def parse_file(file_path):
    """Determines the file format and parses accordingly."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    if ".model" in lines[0]:  # BLIF file
        return parse_blif(lines)
    else:  # PLA file
        return parse_pla(lines)


def parse_pla(lines):
    """Parses a PLA file and extracts minterms and outputs."""
    inputs, outputs = [], []
    for line in lines:
        if line.strip().startswith("#") or not line.strip():
            continue
        inputs.append(line.split()[0])
        outputs.append(line.split()[1])
    return inputs, outputs


def parse_blif(lines):
    """Parses a BLIF file and extracts minterms and outputs."""
    inputs = []
    outputs = []
    for line in lines:
        if line.startswith(".inputs") or line.startswith(".outputs"):
            continue
        if line.startswith(".names"):
            parts = line.split()
            num_inputs = len(parts) - 2
            for l in lines[lines.index(line) + 1 :]:
                if l.strip() == "" or l.startswith(".end"):
                    break
                minterm = l.strip()[:num_inputs]
                output = l.strip()[-1]
                inputs.append(minterm)
                outputs.append(output)
    return inputs, outputs


def expand_dont_cares(minterm):
    """Expands a minterm with don't-care '-' into all possible binary combinations."""
    positions = [i for i, char in enumerate(minterm) if char == '-']
    combinations = []
    for values in itertools.product("01", repeat=len(positions)):
        expanded = list(minterm)
        for pos, value in zip(positions, values):
            expanded[pos] = value
        combinations.append("".join(expanded))
    return combinations


def group_minterms(minterms):
    """Groups minterms based on the number of 1s."""
    groups = {}
    for minterm in minterms:
        expanded_terms = expand_dont_cares(minterm)
        for expanded in expanded_terms:
            count = expanded.count("1")
            if count not in groups:
                groups[count] = []
            groups[count].append(expanded)
    return groups


def combine_terms(term1, term2):
    """Combines two terms if they differ by one bit."""
    diff_count = 0
    combined = []
    for a, b in zip(term1, term2):
        if a != b:
            diff_count += 1
            combined.append("-")
        else:
            combined.append(a)
    if diff_count == 1:
        return "".join(combined)
    return None


def find_prime_implicants(groups):
    """Finds all prime implicants from grouped terms."""
    prime_implicants = set()
    while groups:
        next_groups = {}
        marked = set()
        for group1, group2 in zip(groups.values(), list(groups.values())[1:]):
            for term1 in group1:
                for term2 in group2:
                    combined = combine_terms(term1, term2)
                    if combined:
                        marked.update([term1, term2])
                        next_group_key = combined.count("1")
                        if next_group_key not in next_groups:
                            next_groups[next_group_key] = []
                        next_groups[next_group_key].append(combined)
        prime_implicants.update({term for group in groups.values() for term in group if term not in marked})
        groups = next_groups
    return prime_implicants


def write_pla(output_file, inputs, outputs):
    """Writes simplified terms to a PLA file."""
    with open(output_file, "w") as f:
        for inp, out in zip(inputs, outputs):
            f.write(f"{inp} {out}\n")


if __name__ == "__main__":
    # Example usage
    input_file = "example.blif"  # Can be a .pla or .blif file
    output_file = "output.pla"

    # Parse input file
    inputs, outputs = parse_file(input_file)

    # Expand don't-cares and group minterms
    expanded_inputs = []
    expanded_outputs = []
    for inp, out in zip(inputs, outputs):
        if out == "-":
            continue  # Don't care outputs are ignored for prime implicants
        expanded_inputs.extend(expand_dont_cares(inp))
        expanded_outputs.extend([out] * (2 ** inp.count("-")))

    # Simplify Boolean function
    groups = group_minterms(expanded_inputs)
    prime_implicants = find_prime_implicants(groups)

    # Save simplified PLA
    write_pla(output_file, prime_implicants, ["1"] * len(prime_implicants))

    print(f"Simplified PLA written to {output_file}")
