import argparse
import os
import re
import tarfile
from itertools import chain
from pathlib import Path
from time import sleep
from typing import Any, Generator, Iterable

import requests
from requests.auth import HTTPBasicAuth


class Uploader:
    def upload_file(self, input_lines: Generator[str, Any, Any]):
        upload_file = self.work_dir.joinpath("tmp.ndjson")
        with open(file=upload_file, mode="w") as fh_write:
            for line in input_lines:
                fh_write.writelines(['{"create": {}}\n', line])
            fh_write.write("\n")
        with open(file=upload_file, mode="rb") as fh:
            resp = requests.post(
                self.build_es_url(self.es_datastream, "_bulk"),
                headers={"Content-Type": "application/x-ndjson"},
                auth=self.es_auth,
                data=fh,
            )
            if resp.status_code >= 400:
                print(resp.json())
                resp.raise_for_status()
            data = resp.json()
            if "errors" in data and data["errors"]:
                print("[ERROR] Error occured uploading file")
                print(data)
                exit(1)

    def get_ndjson_tar_gz_lines(self, file: Path) -> Generator[str, Any, Any]:
        with tarfile.open(file, "r") as tar_file:
            for tar_object in tar_file:
                fh_read = tar_file.extractfile(tar_object)
                if not fh_read:
                    raise ValueError("Unexpected missing file")
                for line in fh_read:
                    yield line.decode()
                fh_read.close()

    def get_ndjson_lines(self, file: Path) -> Generator[str, Any, Any]:
        with open(file=file) as fh_read:
            for line in fh_read:
                yield line

    def build_es_url(self, *path: str):
        return f"http://{self.es_host}:{self.es_port}/{'/'.join(path)}"

    def upload(self):
        parser = argparse.ArgumentParser(
            description=(
                "Upload metricbeat ndjson files in a given input directory to an ES"
                " cluster"
            ),
        )

        parser.add_argument(
            "--input",
            help="input directory to process",
            required=True,
        )

        parser.add_argument(
            "--interval",
            type=int,
            help="interval in seconds between input content polling",
            default=10,
        )

        parser.add_argument(
            "--es-host", help="hostname of the ES cluster", default="localhost"
        )

        parser.add_argument(
            "--es-port", help="port of the ES cluster", type=int, default="9200"
        )

        parser.add_argument(
            "--es-username", help="username of the ES cluster", default="elastic"
        )

        parser.add_argument(
            "--es-password",
            help="password of the ES cluster (default to ELASTIC_PASSWORD environment "
            "variable)",
            default=os.getenv("ELASTIC_PASSWORD", None),
        )

        parser.add_argument(
            "--es-datastream",
            help="datastream to push files (default based on STACK_VERSION environment "
            "variable)",
            default=f"metricbeat-{os.getenv('STACK_VERSION')}"
            if "STACK_VERSION" in os.environ
            else None,
        )

        parser.add_argument(
            "--work-dir",
            help="directory where temporary files might be created",
            required=True,
        )

        parsed_args = parser.parse_args()

        self.input_path = Path(parsed_args.input).absolute()
        print(f"Input path: {self.input_path}")

        self.es_host = parsed_args.es_host
        print(f"ES host: {self.es_host}")

        self.es_port = parsed_args.es_port
        print(f"ES port: {self.es_port}")

        self.es_username = parsed_args.es_username
        print(f"ES username: {self.es_username}")

        self.es_password = parsed_args.es_password
        if not self.es_password:
            print("[ERROR] Elasticsearch password is not set")
            exit(1)

        self.es_datastream = parsed_args.es_datastream
        if not self.es_datastream:
            print("[ERROR] Elasticsearch datastream is not set")
            exit(1)
        print(f"ES datastream: {self.es_datastream}")

        self.work_dir = Path(parsed_args.work_dir).absolute()
        print(f"Work directory: {self.work_dir}")

        self.es_auth = HTTPBasicAuth(
            username=self.es_username, password=self.es_password
        )
        resp = requests.get(self.build_es_url("_data_stream"), auth=self.es_auth)
        if True not in (
            stream["name"] == self.es_datastream
            for stream in resp.json()["data_streams"]
        ):
            print("[ERROR] datastream does not exists in ES")

        while True:
            files_to_process = self.sort_files(
                chain(
                    self.input_path.glob("**/*.ndjson"),
                    self.input_path.glob("**/*.ndjson.tar.gz"),
                )
            )

            for file in files_to_process:
                done_file = Path(file.parent.joinpath(f"{file.name}.done"))
                if done_file.exists():
                    continue
                print(f"Uploading {file}")
                if file.suffixes == [".ndjson", ".tar", ".gz"]:
                    self.upload_file(self.get_ndjson_tar_gz_lines(file=file))
                elif file.suffixes == [".ndjson"]:
                    self.upload_file(self.get_ndjson_lines(file=file))
                else:
                    print("[ERROR] Unexpected file, this is a bug")
                    exit(1)
                with open(done_file, "w"):
                    pass

            print(f"Sleeping for {parsed_args.interval} seconds")
            sleep(parsed_args.interval)

    def convert_text(self, text: str) -> int | str:
        return int(text) if text.isdigit() else text

    def get_alphanum_key(self, file: Path) -> list[int | str]:
        return [self.convert_text(c) for c in re.split("([0-9]+)", file.stem)]

    def sort_files(self, list: Iterable[Path]) -> list[Path]:
        """Sort the given iterable in the way that humans expect."""
        return sorted(list, key=self.get_alphanum_key)


if __name__ == "__main__":
    Uploader().upload()
