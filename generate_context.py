import os
import argparse
from SnapshotGenerator import SnapshotGenerator

# Common folders to avoid
COMMON_AVOID_FOLDERS = [
    "node_modules", "venv", "env", "__pycache__", "site-packages", "myenv",
    "target", "bin", "build", "obj", "vendor"
]

def main(root_dir, additional_avoid_folders, output_file, output_folder, compress, amount_of_chunks, size_of_chunk):
    # Combine common avoid folders with additional avoid folders
    avoid_folders = COMMON_AVOID_FOLDERS + additional_avoid_folders

    # Create a temporary instance of SnapshotGenerator to access the language_extensions
    temp_config = {
        "root_dir": root_dir,
        "avoid_folders": avoid_folders,
        "include_extensions": [],
        "key_files": [],
        "output_file": "",
        "compress": 0,
        "amount_of_chunks": 0,
        "size_of_chunk": 0,
    }
    temp_generator = SnapshotGenerator(temp_config)
    language_extensions = set()
    for extensions in temp_generator.language_extensions.values():
        language_extensions.update(extensions)

    config = {
        "root_dir": root_dir,
        "avoid_folders": avoid_folders,
        "include_extensions": list(language_extensions),
        "key_files": temp_generator.key_files,  # Using existing key files from the class
        "output_file": output_file,
        "compress": compress,
        "amount_of_chunks": amount_of_chunks,
        "size_of_chunk": size_of_chunk,
    }

    generator = SnapshotGenerator(config)
    generator.generate_context_file()

    if compress:
        if amount_of_chunks:
            parts_dir = generator.split_file(output_file, num_chunks=amount_of_chunks)
        elif size_of_chunk:
            parts_dir = generator.split_file(output_file, chunk_size=size_of_chunk)

        # Use the specified output folder or default to /brainboost/brainboost_context
        output_folder = output_folder or '/brainboost/brainboost_context'
        os.makedirs(output_folder, exist_ok=True)
        new_parts_dir = os.path.join(output_folder, os.path.basename(parts_dir))
        os.rename(parts_dir, new_parts_dir)
        print(f"Parts directory moved to: {new_parts_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a single context for a project.")
    parser.add_argument("--root_dir", required=True, help="Root directory of the project to scan")
    parser.add_argument("--output_file", required=True, help="Output file for the snapshot")
    parser.add_argument("--output_folder", required=False, default="", help="Output folder for the parts directory")
    parser.add_argument("--additional-avoid-folders", required=False, default="", help="Comma separated list of additional folders to avoid")
    parser.add_argument("--compress", type=int, choices=[0, 1], default=0, help="Whether to compress the output (0 or 1)")
    parser.add_argument("--amount-of-chunks", type=int, help="Number of chunks to split the file into")
    parser.add_argument("--size-of-chunk", type=int, help="Size of each chunk in bytes")

    args = parser.parse_args()

    main(
        args.root_dir,
        args.additional_avoid_folders.split(',') if args.additional_avoid_folders else [],
        args.output_file,
        args.output_folder,
        args.compress,
        args.amount_of_chunks,
        args.size_of_chunk
    )
