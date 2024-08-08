import os
import argparse
from alive_progress import alive_bar

INCLUDE_EXTENSIONS = [
    ".js", ".mjs", ".jsx", ".ts", ".tsx", ".py", ".java", ".cs", ".csproj",
    ".cpp", ".hpp", ".h", ".cc", ".c", ".rb", ".erb", ".rake", ".php", ".phtml",
    ".php3", ".php4", ".php5", ".phps", ".swift", ".kt", ".kts", ".go", ".R", 
    ".r", ".pl", ".pm", ".t", ".sh", ".bash", ".html", ".htm", ".css", ".scss",
    ".sass", ".less", ".sql", ".scala", ".sc", ".hs", ".lhs", ".lua", ".rs",
    ".dart", ".m", ".jl", ".vb", ".vbs", ".asm", ".s", ".fs", ".fsi", ".fsx",
    ".groovy", ".gvy", ".gy", ".gsh", ".erl", ".hrl", ".ex", ".exs", ".cob",
    ".cbl", ".f", ".for", ".f90", ".f95", ".adb", ".ads", ".pro", ".P", ".lisp",
    ".lsp", ".scm", ".ss", ".rkt", ".v", ".vh", ".vhdl", ".vhd", ".md", ".markdown",
    ".pas", ".dpr", ".dfm", ".ml", ".mli", ".vue", ".ipynb", ".json"
]

def find_source_code_directories(start_path, output_path):
    with open(output_path, 'a') as output_file:
        with alive_bar(title="Scanning directories") as bar:
            for dirpath, _, filenames in os.walk(start_path):
                for file in filenames:
                    if any(file.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                        print(f"Source code directory found: {dirpath}")
                        output_file.write(f"{dirpath}\n")
                        break  # Found a source code file, move to next directory
                bar()

def main(start_path, output_path):
    find_source_code_directories(start_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List directories containing source code files.')
    parser.add_argument('--start-path', type=str, required=True, help='Path to start scanning')
    parser.add_argument('--output-path', type=str, required=True, help='Path to save the output file')
    args = parser.parse_args()
    
    main(args.start_path, args.output_path)
