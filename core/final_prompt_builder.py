def generate_final_prompt(user_requirement: str, decisions: list) -> str:
    lines = []

    lines.append("# Project Specification\n")
    lines.append("## User Requirement")
    lines.append(user_requirement.strip())
    lines.append("\n## Selected Technology Stack\n")

    for i, d in enumerate(decisions, 1):
        lines.append(f"### {i}. {d.choice}")
        lines.append(f"**Why chosen:** {d.rationale}")
        lines.append(f"**Purpose:** {d.purpose}\n")

    stack_summary = " → ".join([d.choice for d in decisions])

    lines.append("## Technology Stack Summary")
    lines.append(stack_summary)

    return "\n".join(lines)
