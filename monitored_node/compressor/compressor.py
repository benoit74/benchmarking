import argparse
import re
import tarfile
from pathlib import Path
from time import sleep


def compressor():
    parser = argparse.ArgumentParser(
        description=(
            "Continuously compress old metricbeat files except current one"
            "in a given input directory"
        ),
    )

    parser.add_argument(
        "--input",
        help="input directory to watch",
        required=True,
    )

    parser.add_argument(
        "--interval",
        type=int,
        help="interval in seconds between input content polling",
        default=10,
    )

    parsed_args = parser.parse_args()

    input_path = Path(parsed_args.input).absolute()

    print(f"Polling {input_path}")
    while True:
        print(f"Sleeping for {parsed_args.interval} seconds")
        sleep(parsed_args.interval)

        if not input_path.exists():
            print("--input must exist")
            exit(1)

        if not input_path.is_dir():
            print("--input must be a directory")
            exit(1)

        all_files_names = sort_files_produced(
            list(map(lambda path: path.name[:-7], input_path.glob("*.ndjson")))
        )

        for name in all_files_names[:-1]:
            orig_path = input_path.joinpath(f"{name}.ndjson")
            dest_path = input_path.joinpath(f"{name}.ndjson.tar.gz")
            print(f"Compressing {orig_path.name} to {dest_path.name}")
            with tarfile.open(dest_path, "w:gz") as archive:
                archive.add(orig_path)
            orig_path.unlink()


def convert_text(text: str) -> int | str:
    return int(text) if text.isdigit() else text


def get_alphanum_key(key: str) -> list[int | str]:
    return [convert_text(c) for c in re.split("([0-9]+)", key)]


def sort_files_produced(list: list[str]) -> list[str]:
    """Sort the given iterable in the way that humans expect."""
    # convert = lambda text: int(text) if text.isdigit() else text
    # alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(list, key=get_alphanum_key)


if __name__ == "__main__":
    compressor()
