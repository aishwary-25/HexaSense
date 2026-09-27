from pathlib import Path


def seed_demo_docs():
    """Create a few sample documents for the hackathon demo."""
    sample_dir = Path("data/sample_docs")
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_docs = {
        "notes.txt": """Project status:\n- Launch date is set for Q3, after user testing.\n- Client priorities: privacy, speed, and local AI.\n- Contact: alice@example.com should be informed before deployment.\n""",
        "contract.md": """# Vendor agreement\n\nThe client agrees to pay 30% upfront and 70% on delivery.\nThe product must run locally without cloud dependency.\n\nSensitive terms: support email hello@company.com\n""",
        "research.txt": """Research notes:\n- Snapdragon X Elite is well suited for on-device local inference.\n- Privacy-first AI is a major user need.\n- All local memory systems need selective forgetting.\n""",
    }

    for name, text in sample_docs.items():
        path = sample_dir / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")
