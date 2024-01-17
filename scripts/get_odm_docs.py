from pathlib import Path
import shlex
import subprocess

import yaml

root_dir = Path(__file__).parent.parent
parent_dir = Path(__file__).parent.parent.parent

howler_dir = parent_dir / "howler-api"
if not (parent_dir / "howler-api").exists():
    howler_dir = Path(input("Enter complete path to howler-api:\n> "))

print(f"Executing from {howler_dir}")

venv_dir = next(howler_dir.glob("*env"))

output = subprocess.check_output(
    shlex.split(f"{venv_dir}/bin/python {howler_dir}/build_scripts/generate_md_docs.py")
)

yaml_output = []
for md in output.decode().strip().split("\n\n\n\n"):
    class_name = md.split("\n")[0]

    relative_path = (
        root_dir.relative_to(parent_dir) / "docs/odm/class" / (class_name + ".md")
    )
    print(f"Writing to {relative_path}")

    (parent_dir / relative_path).parent.mkdir(parents=True, exist_ok=True)
    (parent_dir / relative_path).write_text("\n".join(md.split("\n")[1:]))
    yaml_output.append(f"    - {relative_path.relative_to('howler-docs/docs')}")

print('\nAdd the following below "Data Ontology" in mkdocs.yml:')

print("  - Classes:")
print("\n".join(sorted(yaml_output)))
