from pathlib import Path
import shlex
import subprocess

root_dir = Path(__file__).parent.parent
parent_dir = Path(__file__).parent.parent.parent

print("Generating Howler API documentation")

howler_api_dir = parent_dir / "howler-api"
if not (parent_dir / "howler-api").exists():
    howler_api_dir = Path(input("Enter complete path to howler-api:\n> "))

print(f"\tExecuting from {howler_api_dir}")

venv_dir = next(howler_api_dir.glob("*env"))

output = subprocess.check_output(
    shlex.split(
        f"{venv_dir}/bin/python {howler_api_dir}/build_scripts/generate_md_docs.py"
    )
)

yaml_output_preface = ["- Data Ontology:"]
yaml_output = []
handled_first = False
for md in output.decode().strip().split("\n\n\n\n"):
    file_name = md.split("\n")[0]
    relative_path = root_dir.relative_to(parent_dir) / file_name
    print(f"\t\tWriting to {relative_path}")

    (parent_dir / relative_path).parent.mkdir(parents=True, exist_ok=True)
    (parent_dir / relative_path).write_text("\n".join(md.split("\n")[1:]))
    if not handled_first:
        yaml_output_preface.append(
            f"  - Getting Started: {relative_path.relative_to('howler-docs/docs')}"
        )
        yaml_output_preface.append("  - Classes:")
        handled_first = True
    else:
        yaml_output.append(f"    - {relative_path.relative_to('howler-docs/docs')}")

print("\n\tAdd the following below nav in mkdocs.yml:")

print()
print("\n".join(yaml_output_preface))
print("\n".join(sorted(yaml_output)))
