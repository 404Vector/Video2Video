import os
import datetime
import argparse

TAG_ENV_NAME = "GITHUB_ACTION_TAG_NAME"
VERSION_TEXT = "0.0.0"


def parse_args():
    paser = argparse.ArgumentParser()
    paser.add_argument("-i", "--version_file_path", required=True, type=str)

    return paser.parse_args()


def get_version() -> str:
    if TAG_ENV_NAME in os.environ:
        return os.environ[TAG_ENV_NAME]
    else:
        return f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y.%m.%d.%H.%M.%S')}"


def main(args: argparse.Namespace):
    file_path = args.version_file_path
    assert os.path.exists(file_path)
    assert os.path.isfile(file_path)
    version = get_version()
    with open(file=file_path, mode="r") as f:
        file_text = str(f.read())
    assert file_text.find(VERSION_TEXT) > -1
    print(f"Build Version : {version}")
    file_text = file_text.replace(VERSION_TEXT, version)
    with open(file=file_path, mode="w") as f:
        result = f.write(file_text)
        print(result)


if __name__ == "__main__":
    args = parse_args()
    main(args)
