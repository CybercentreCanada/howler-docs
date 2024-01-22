from pathlib import Path
import re
import shlex
import subprocess

SUBSTITUTIONS = [
    (r"\(/help/auth\)", "(/howler-docs/ingestion/authentication/)"),
    ("/home/\w+/repos/howler-api-public", "/example_dir/howler-api"),
]

root_dir = Path(__file__).parent.parent
parent_dir = Path(__file__).parent.parent.parent

print("Generating Howler API documentation")


def _input(prompt: str):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        exit(1)


print("Trying to find howler-api-public")
howler_api_dir = parent_dir / "howler-api-public"
if not howler_api_dir.exists():
    howler_api_dir = parent_dir / "howler-api-public"
    if howler_api_dir.exists():
        print(
            "WARN: Please run this against the public repository. Based on the directory location, this may be the internal repository."
        )
        answer = _input("Is this the public repo ? [y/N] ")
        if answer.lower() != "y":
            exit(0)
    else:
        howler_api_dir = Path(input("Enter complete path to howler-api:\n> "))

print(f"\tExecuting from {howler_api_dir}")

venv_dir = next(howler_api_dir.glob("*env"))

output = subprocess.check_output(
    shlex.split(
        f"{venv_dir}/bin/python {howler_api_dir}/build_scripts/generate_md_docs.py"
    )
)

warned_files = []

yaml_output = ["- Data Ontology:"]
yaml_output_ontology_keys = []
handled_first = False
for md in output.decode().strip().split("\n\n\n\n"):
    file_name = md.split("\n")[0]
    relative_path = root_dir.relative_to(parent_dir) / file_name
    print(f"\t\tWriting to {relative_path}")

    (parent_dir / relative_path).parent.mkdir(parents=True, exist_ok=True)

    processed_md = "\n".join(md.split("\n")[1:]) + "\n"

    for old, new in SUBSTITUTIONS:
        processed_md = re.sub(old, new, processed_md)

    (parent_dir / relative_path).write_text(processed_md)

    entry = relative_path.relative_to("howler-docs/docs")
    if str(entry).startswith("odm/class"):
        yaml_output_ontology_keys.append(f"    - {entry}")
    else:
        warned_files.append(entry)
yaml_output.extend(sorted(yaml_output_ontology_keys))

print("Generating Howler UI documentation")

print("Trying to find howler-ui-public")
howler_ui_dir = parent_dir / "howler-ui-public"
if not howler_ui_dir.exists():
    howler_ui_dir = parent_dir / "howler-ui-public"
    if howler_ui_dir.exists():
        print(
            "WARN: Please run this against the public repository. Based on the directory location, this may be the internal repository."
        )
        answer = _input("Is this the public repo ? [y/N] ")
        if answer.lower() != "y":
            exit(0)
    else:
        howler_ui_dir = Path(input("Enter complete path to howler-ui:\n> "))

print(f"\tExecuting from {howler_ui_dir}")

ui_yaml = []


for md_file in howler_ui_dir.rglob("src/components/routes/help/**/*.md"):
    if "node_modules" in str(md_file):
        continue

    file_data = md_file.read_text()
    if not file_data.startswith("<!-- docs"):
        continue

    file_path = Path(re.sub(r"<!-- (.+) -->", r"\1", file_data.split("\n")[0]))

    file_data = re.sub(
        r"```alert\n([\s\S]+?)\n```",
        lambda m1: '??? "Note"\n    ' + "\n    ".join(m1[1].split("\n")),
        file_data,
    )

    for old, new in SUBSTITUTIONS:
        file_data = re.sub(old, new, file_data)

    print(f"\t\tWriting to {file_path}")

    (root_dir / file_path).parent.mkdir(parents=True, exist_ok=True)
    (root_dir / file_path).write_text(file_data)

    if "fr" not in file_path.name:
        ui_yaml.append(f"- {str(file_path.relative_to('docs/').parent).capitalize()}:")
        ui_yaml.append(f"  - {str(file_path.relative_to('docs/'))}")

yaml_output.extend(list(dict.fromkeys(ui_yaml)))

print("\nAdd the following below nav in mkdocs.yml:")
print("\n".join(yaml_output) + "\n")

if len(warned_files) > 0:
    print(
        "Warn: The following files were copied, but could not be placed in the nav automatically:"
    )
    for warn in warned_files:
        print(f"\t{warn}")
