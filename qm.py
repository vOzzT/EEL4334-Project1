import itertools
import numpy as np

def parse_pla(file_path):
    """Parses a PLA file and extracts minterms and outputs."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    inputs, outputs = [], []
    for line in lines:
        if line.strip().startswith("#") or not line.strip():
            continue
        inputs.append(line.split()[0])
        outputs.append(line.split()[1])
    return inputs, outputs


def group_minterms(minterms):
    """Groups minterms based on the number of 1s."""
    groups = {}
    for minterm in minterms:
        count = minterm.count("1")
        if count not in groups:
            groups[count] = []
        groups[count].append(minterm)
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
    input_file = "example.pla"
    output_file = "simplified.pla"

    # Parse input PLA
    inputs, outputs = parse_pla(input_file)

    # Simplify Boolean function
    groups = group_minterms(inputs)
    prime_implicants = find_prime_implicants(groups)

    # Save simplified PLA
    write_pla(output_file, prime_implicants, outputs)

    print(f"Simplified PLA written to {output_file}")
