import os
import re
from datetime import datetime
import json
from collections import defaultdict

class SnapshotGenerator:
    def __init__(self, config):
        self.root_dir = config['root_dir']
        self.avoid_folders = config['avoid_folders']
        self.include_extensions = set(config['include_extensions'])
        self.key_files = config['key_files']
        self.output_file = config['output_file']
        self.compress = config['compress']
        self.amount_of_chunks = config['amount_of_chunks']
        self.size_of_chunk = config['size_of_chunk']
        self.imports = defaultdict(int)
        self.project_name = os.path.basename(self.root_dir)
        self.language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.mjs', '.jsx'],
            'typescript': ['.ts', '.tsx'],
            'java': ['.java'],
            'csharp': ['.cs', '.csproj'],
            'cpp': ['.cpp', '.hpp', '.h', '.cc'],
            'c': ['.c', '.h'],
            'ruby': ['.rb', '.erb', '.rake'],
            'php': ['.php', '.phtml', '.php3', '.php4', '.php5', '.phps'],
            'swift': ['.swift'],
            'kotlin': ['.kt', '.kts'],
            'go': ['.go'],
            'r': ['.R', '.r'],
            'perl': ['.pl', '.pm', '.t'],
            'bash': ['.sh', '.bash'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass', '.less'],
            'sql': ['.sql'],
            'scala': ['.scala', '.sc'],
            'haskell': ['.hs', '.lhs'],
            'lua': ['.lua'],
            'rust': ['.rs'],
            'dart': ['.dart'],
            'matlab': ['.m'],
            'julia': ['.jl'],
            'vb': ['.vb', '.vbs'],
            'asm': ['.asm', '.s'],
            'fsharp': ['.fs', '.fsi', '.fsx'],
            'groovy': ['.groovy', '.gvy', '.gy', '.gsh'],
            'erlang': ['.erl', '.hrl'],
            'elixir': ['.ex', '.exs'],
            'cobol': ['.cob', '.cbl'],
            'fortran': ['.f', '.for', '.f90', '.f95'],
            'ada': ['.adb', '.ads'],
            'prolog': ['.pl', '.pro', '.P'],
            'lisp': ['.lisp', '.lsp'],
            'scheme': ['.scm', '.ss'],
            'racket': ['.rkt'],
            'verilog': ['.v', '.vh'],
            'vhdl': ['.vhdl', '.vhd'],
            'markdown': ['.md', '.markdown'],
            'vue': ['.vue'],
            'svelte': ['.svelte'],
            'json': ['.json'],
            'yaml': ['.yaml', '.yml'],
            'xml': ['.xml'],
            'git': ['.gitignore', '.gitattributes'],
            'cicd': ['.travis.yml', 'Jenkinsfile', '.circleci/config.yml', '.gitlab-ci.yml', 'azure-pipelines.yml']
        }
        self.detected_language = None

    def exclude_directories(self, dirs):
        exclude_set = set(self.avoid_folders)
        return [d for d in dirs if d not in exclude_set]

    def detect_programming_language(self, file):
        for language, extensions in self.language_extensions.items():
            if file.endswith(tuple(extensions)):
                return language
        return None

    def build_tree_structure(self, root_dir):
        tree = {"directory_name": os.path.basename(root_dir), "children": []}
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = self.exclude_directories(dirs)
            path = root.split(os.sep)
            subdir = tree
            for part in path:
                for child in subdir["children"]:
                    if child.get("directory_name") == part:
                        subdir = child
                        break
                else:
                    new_dir = {"directory_name": part, "children": []}
                    subdir["children"].append(new_dir)
                    subdir = new_dir
            for file in files:
                if file.endswith(tuple(self.include_extensions)) or file in self.key_files:
                    subdir["children"].append({"file_name": file})
        return tree

    def extract_imports(self, content, extension):
        patterns = {
            ".py": r"^\s*(?:import|from)\s+([\w\.]+)",
            ".js": r"^\s*import\s+.*?\s+from\s+['\"]([\w\-\/]+)['\"]",
            ".java": r"^\s*import\s+([\w\.]+)",
            ".cpp": r"^\s*#\s*include\s*<([\w\.\/]+)>",
            ".c": r"^\s*#\s*include\s*<([\w\.\/]+)>",
            ".cs": r"^\s*using\s+([\w\.]+)",
            ".rb": r"^\s*require\s+['\"]([\w\/]+)['\"]",
            ".php": r"^\s*use\s+([\w\\]+)",
            ".go": r"^\s*import\s+['\"]([\w\/]+)['\"]",
            ".rs": r"^\s*extern\s+crate\s+([\w_]+)",
            ".dart": r"^\s*import\s+['\"]([\w\/]+)['\"]",
            ".ts": r"^\s*import\s+.*?\s+from\s+['\"]([\w\-\/]+)['\"]",
            ".swift": r"^\s*import\s+([\w]+)",
            ".kt": r"^\s*import\s+([\w\.]+)"
        }

        pattern = patterns.get(extension)
        if not pattern:
            return []

        regex = re.compile(pattern, re.MULTILINE)
        matches = regex.findall(content)
        for match in matches:
            self.imports[match] += 1
        return matches

    def generate_context_file(self):
        print(f"Generating context file: {self.output_file}")
        project_data = {
            'project_name': self.project_name,
            'programming_language': '',  # Will be detected later
            'project_tree_structure': self.build_tree_structure(self.root_dir),
            'project_sources': [],
            'external_libraries': [],
            'observations': []
        }

        for root, dirs, files in os.walk(self.root_dir, topdown=True):
            dirs[:] = self.exclude_directories(dirs)
            if files:
                for file in files:
                    if file.endswith(tuple(self.include_extensions)) or file in self.key_files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f_in:
                                content = f_in.read()
                                file_info = os.stat(file_path)
                                source_data = {
                                    'file': {
                                        'File': file,
                                        'Full Path': file_path,
                                        'Relative Path': os.path.relpath(file_path, self.root_dir),
                                        'Size': file_info.st_size,
                                        'Last Modified': datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                        'Lines': len(content.splitlines()),
                                        'Source_Code': content
                                    }
                                }
                                project_data['project_sources'].append(source_data)

                                extension = os.path.splitext(file)[1]
                                self.extract_imports(content, extension)

                                # Detect programming language
                                if not self.detected_language:
                                    self.detected_language = self.detect_programming_language(file)

                        except UnicodeDecodeError as e:
                            print(f"Skipping file {file_path} due to decoding error: {e}")
                        except Exception as e:
                            print(f"Skipping file {file_path} due to an unexpected error: {e}")

        project_data['programming_language'] = self.detected_language or 'unknown'
        project_data['external_libraries'] = [{"import_name": imp, "count": count} for imp, count in self.imports.items()]

        if not self.imports:
            project_data['observations'].append("No external libraries or imports were detected in the source code.")

        with open(self.output_file, 'w', encoding='utf-8') as f_out:
            json.dump(project_data, f_out, indent=4)

        os.chmod(self.output_file, 0o666)
        print(f"Context file generated at: {self.output_file}")

    def split_file(self, file_path, num_chunks=None, chunk_size=None):
        output_dir = f"{os.path.splitext(file_path)[0]}_parts"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Splitting file {file_path} into parts in directory {output_dir}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if num_chunks:
            chunk_size = len(content) // num_chunks + (len(content) % num_chunks > 0)

        chunk_size = chunk_size or len(content)
        part_num = 0

        for i in range(0, len(content), chunk_size):
            part_filename = os.path.join(output_dir, f"{os.path.basename(file_path)}.part{part_num}")
            with open(part_filename, 'w', encoding='utf-8') as part_file:
                part_file.write(content[i:i + chunk_size])
            os.chmod(part_filename, 0o666)
            print(f"Created part file: {part_filename}")
            part_num += 1

        new_output_file_path = os.path.join(output_dir, os.path.basename(file_path))
        os.rename(file_path, new_output_file_path)
        os.chmod(new_output_file_path, 0o666)
        print(f"Moved original context file to: {new_output_file_path}")

        return output_dir
