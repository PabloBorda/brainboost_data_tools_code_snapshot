import os
import argparse
from datetime import datetime
import json
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from SnapshotGenerator import SnapshotGenerator
from GitHubBatchCloner import GitHubBatchCloner
from collections import defaultdict

# List of file extensions to include
INCLUDE_EXTENSIONS = [
    # Programming Languages
    ".js", ".mjs", ".jsx",     # JavaScript
    ".ts", ".tsx",             # TypeScript
    ".py",                     # Python
    ".java",                   # Java
    ".cs", ".csproj",          # C#
    ".cpp", ".hpp", ".h", ".cc", # C++
    ".c", ".h",                # C
    ".rb", ".erb", ".rake",    # Ruby
    ".php", ".phtml", ".php3", ".php4", ".php5", ".phps", # PHP
    ".swift",                  # Swift
    ".kt", ".kts",             # Kotlin
    ".go",                     # Go
    ".R", ".r",                # R
    ".pl", ".pm", ".t",        # Perl
    ".sh", ".bash",            # Shell Scripting
    ".html", ".htm",           # HTML
    ".css", ".scss", ".sass", ".less", # CSS and preprocessors
    ".sql",                    # SQL
    ".scala", ".sc",           # Scala
    ".hs", ".lhs",             # Haskell
    ".lua",                    # Lua
    ".rs",                     # Rust
    ".dart",                   # Dart
    ".m",                      # MATLAB, Objective-C
    ".jl",                     # Julia
    ".vb", ".vbs",             # Visual Basic
    ".asm", ".s",              # Assembly Language
    ".fs", ".fsi", ".fsx",     # F#
    ".groovy", ".gvy", ".gy", ".gsh", # Groovy
    ".erl", ".hrl",            # Erlang
    ".ex", ".exs",             # Elixir
    ".cob", ".cbl",            # COBOL
    ".f", ".for", ".f90", ".f95", # Fortran
    ".adb", ".ads",            # Ada
    ".pl", ".pro", ".P",       # Prolog
    ".lisp", ".lsp",           # Lisp
    ".scm", ".ss",             # Scheme
    ".rkt",                    # Racket
    ".v", ".vh",               # Verilog
    ".vhdl", ".vhd",           # VHDL
    ".md", ".markdown",        # Markdown

    # Frameworks and Libraries
    ".vue",                    # Vue.js
    ".ts", ".html", ".css", ".scss", # Angular
    ".py", ".html",            # Django, Flask
    ".java", ".xml", ".properties", ".yml", # Spring Boot
    ".rb", ".html.erb", ".js.erb", # Ruby on Rails
    ".php", ".blade.php",      # Laravel
    ".cs", ".cshtml", ".vbhtml", # ASP.NET
    ".svelte",                 # Svelte
    ".py", ".ipynb",           # TensorFlow, PyTorch
    ".java", ".xml",           # Hadoop
    ".scala", ".py", ".java", ".r", # Spark
    ".dart",                   # Flutter

    # Configuration and Other Relevant Files
    ".json",                   # JSON
    ".yaml", ".yml",           # YAML
    ".xml",                    # XML
    ".gitignore", ".gitattributes", # Git
    ".travis.yml", "Jenkinsfile", ".circleci/config.yml", ".gitlab-ci.yml", "azure-pipelines.yml" # CI/CD
]

# Key framework files to include
KEY_FILES = [
    "Dockerfile", ".dockerignore",
    "package.json", "requirements.txt", "Pipfile", "composer.json", "Gemfile", "build.gradle", "pom.xml", "Cargo.toml",
    "Makefile"
]

# Common folders to avoid
COMMON_AVOID_FOLDERS = [
    "node_modules",
    "venv", "env", "__pycache__", "site-packages", "myenv,"
    "target", "bin", "build",
    "obj",
    "vendor",
]

# List of substrings to filter out non-external libraries
EXCLUDE_SUBSTRINGS = [
    "com_goldenthinker_",
    "brainboost",
    "goldenthinker",
    "smartband",
    "papitomarket",
    "pelucadorada",
    "formate"
]

def is_external_library(lib_name):
    for substring in EXCLUDE_SUBSTRINGS:
        if substring in lib_name:
            return False
    return True

def aggregate_imports(snapshots_dir):
    imports_agg = defaultdict(lambda: defaultdict(int))
    file_counts = defaultdict(int)

    for root, dirs, files in os.walk(snapshots_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    programming_language = data.get('programming_language', '').lower()
                    if programming_language:  # Only process if programming_language is not empty
                        file_counts[programming_language] += 1
                        for lib in data.get('external_libraries', []):
                            if isinstance(lib, dict) and 'import_name' in lib and 'count' in lib and is_external_library(lib['import_name']):
                                imports_agg[programming_language][lib['import_name']] += lib['count']
                            else:
                                print(f"Skipping malformed or non-external library entry in {file_path}: {lib}")

    overall_data = []
    for lang, libs in imports_agg.items():
        libs_list = [{'library_name': lib, 'times_imported': count} for lib, count in sorted(libs.items(), key=lambda item: item[1], reverse=True)]
        overall_data.append({'programming_language': lang, 'libraries_used': libs_list, 'file_count': file_counts[lang]})

    overall_data.sort(key=lambda x: x['file_count'], reverse=True)
    return overall_data

def draw_pie_chart(data, title, file_path):
    labels = [item['library_name'] for item in data]
    sizes = [item['times_imported'] for item in data]
    
    plt.figure(figsize=(10, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title)
    plt.savefig(file_path)
    plt.close()

def draw_bar_chart(data, title, file_path):
    labels = [item['library_name'] for item in data]
    sizes = [item['times_imported'] for item in data]
    
    plt.figure(figsize=(12, 8))
    plt.bar(labels, sizes, color='skyblue')
    plt.xlabel('Libraries')
    plt.ylabel('Number of Imports')
    plt.title(title)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def generate_pdf_report(json_data, pdf_output_path):
    pdf = canvas.Canvas(pdf_output_path, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica", 14)
    pdf.drawString(30, height - 30, f"GitHub User: {json_data['github_user_name']} - Overall Statistics")

    current_y = height - 60

    for lang_data in json_data['programming_languages']:
        programming_language = lang_data['programming_language'].capitalize()
        file_count = lang_data['file_count']
        libraries_used = lang_data['libraries_used']

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(30, current_y, f"Programming Language: {programming_language} (Files: {file_count})")
        current_y -= 20

        if libraries_used:
            pie_chart_path = f"./tmp/pie_chart_{programming_language}.png"
            bar_chart_path = f"./tmp/bar_chart_{programming_language}.png"

            draw_pie_chart(libraries_used, f"Library Usage for {programming_language}", pie_chart_path)
            draw_bar_chart(libraries_used, f"Library Usage for {programming_language}", bar_chart_path)

            pdf.drawImage(pie_chart_path, 30, current_y - 200, width=200, height=200)
            pdf.drawImage(bar_chart_path, 250, current_y - 200, width=300, height=200)

            current_y -= 220

        pdf.setFont("Helvetica", 10)
        for lib in libraries_used:
            pdf.drawString(30, current_y, f"{lib['library_name']}: {lib['times_imported']} imports")
            current_y -= 15

        current_y -= 20

        if current_y < 100:
            pdf.showPage()
            current_y = height - 30

    pdf.save()

def main(github_username, additional_avoid_folders, compress, amount_of_chunks, size_of_chunk):
    # Step 1: Clone or update repositories
    github_clone_client = GitHubBatchCloner()
    usernames = [github_username]
    repo_count, clone_urls = github_clone_client.get_github_repos(usernames)

    if repo_count > 0:
        source_code_dir = 'source_code_for_analysis'
        github_clone_client.clone_repos(clone_urls, source_code_dir)

        # Combine common avoid folders with additional avoid folders
        avoid_folders = COMMON_AVOID_FOLDERS + additional_avoid_folders

        # Step 2: Generate snapshots
        projects = [d for d in os.listdir(source_code_dir) if os.path.isdir(os.path.join(source_code_dir, d))]
        for project in projects:
            project_path = os.path.join(source_code_dir, project)
            snapshot_dir = os.path.join('snapshots', project)
            os.makedirs(snapshot_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d%H%M")
            snapshot_output_dir = os.path.join(snapshot_dir, timestamp)
            os.makedirs(snapshot_output_dir, exist_ok=True)

            output_file_path = os.path.join(snapshot_output_dir, "snapshot.json")

            config = {
                "root_dir": project_path,
                "avoid_folders": avoid_folders,
                "include_extensions": INCLUDE_EXTENSIONS,
                "key_files": KEY_FILES,
                "output_file": output_file_path,
                "compress": compress,
                "amount_of_chunks": amount_of_chunks,
                "size_of_chunk": size_of_chunk,
            }

            generator = SnapshotGenerator(config)
            generator.generate_context_file()

            if compress:
                if amount_of_chunks:
                    parts_dir = generator.split_file(output_file_path, num_chunks=amount_of_chunks)
                elif size_of_chunk:
                    parts_dir = generator.split_file(output_file_path, chunk_size=size_of_chunk)
                
                new_parts_dir = os.path.join(snapshot_output_dir, os.path.basename(parts_dir))
                os.rename(parts_dir, new_parts_dir)
                print(f"Parts directory moved to: {new_parts_dir}")

            print(f"Snapshot for project {project} saved in {snapshot_output_dir}")

        # Step 3: Generate overall JSON file
        overall_data = aggregate_imports('snapshots')
        overall_summary = {
            'github_user_name': github_username,
            'programming_languages': overall_data
        }

        overall_output_file = 'overall_summary.json'
        with open(overall_output_file, 'w', encoding='utf-8') as f:
            json.dump(overall_summary, f, indent=4)

        print(f"Overall summary saved in {overall_output_file}")

        # Step 4: Generate PDF report
        generate_pdf_report(overall_summary, 'github_user_report.pdf')
        print(f"PDF report generated at: github_user_report.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a tech report for a GitHub user's repositories.")
    parser.add_argument("github_username", help="GitHub username to fetch repositories for")
    parser.add_argument("--additional-avoid-folders", required=False, default="", help="Comma separated list of additional folders to avoid")
    parser.add_argument("--compress", type=int, choices=[0, 1], default=0, help="Whether to compress the output (0 or 1)")
    parser.add_argument("--amount-of-chunks", type=int, help="Number of chunks to split the file into")
    parser.add_argument("--size-of-chunk", type=int, help="Size of each chunk in bytes")

    args = parser.parse_args()

    main(
        args.github_username,
        args.additional_avoid_folders.split(',') if args.additional_avoid_folders else [],
        args.compress,
        args.amount_of_chunks,
        args.size_of_chunk
    )
