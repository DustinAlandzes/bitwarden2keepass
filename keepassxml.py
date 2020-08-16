#!/usr/bin/env python3
from typing import List, Tuple, Optional

import xmltodict
import glob
import json
import logging

LOGGER = logging.getLogger(__name__)


def parse_folders(bitwarden_folders: List[dict]) -> dict:
    folders = {}
    for folder in bitwarden_folders:
        if folder["id"]:
            folders[folder["id"]] = folder["name"]
    return folders


def create_kp_group(name: str) -> dict:
    group = {
        "Name": name,
        "Entry": [],
    }
    return group


def get_kp_entry(title: str,
                 username: Optional[Tuple[str, ...]],
                 password: Optional[Tuple[str, ...]],
                 url: str,
                 notes: str,
                 otp: str) -> dict:
    return {
        "String": [
            {"Key": "Title", "Value": title},
            {"Key": "UserName", "Value": username},
            {"Key": "Password", "Value": password},
            {"Key": "URL", "Value": url},
            {"Key": "Notes", "Value": notes},
            {"Key": "TOTP Seed", "Value": otp},
            {"Key": "TOTP Settings", "Value": "30;6"},
        ]
    }


def parse() -> any:
    bitwarden_export_json_files = glob.glob("bitwarden_export_*.json")
    if len(bitwarden_export_json_files) < 1:
        raise Exception("Couldn't find the json file.")

    filename = bitwarden_export_json_files[0]
    if len(bitwarden_export_json_files) > 1:
        LOGGER.warning("Found multiple bitwarden backups, using %s", filename)

    for item in j["items"]:
        group = "root"
    with open(filename) as f:
        parsed_json: dict = json.loads(f.read())

    folders: dict = parse_folders(parsed_json["folders"])
    groups: dict = {"root": {"Entry": []}}
    for key, folder in folders.items():
        groups[folder] = create_kp_group(str(folder).title())

    for item in parsed_json["items"]:
        group = None
        if item["folderId"]:
            group = folders[item["folderId"]]
        title = item["name"]
        username = None
        password = None
        uris = []
        totp = None
        notes = []

        if "notes" in item and item["notes"]:
            notes.append(item["notes"])
        if "fields" in item:
            for field in item["fields"]:
                notes.append("%s: %s" % (field["name"], field["value"]))

        if "login" in item:
            login = item["login"]
            if "username" in login:
                username = (login["username"],)
            if "password" in login:
                password = (login["password"],)
            if "uris" in login and login["uris"]:
                for uri in login["uris"]:
                    uris.append(uri["uri"])
            if "totp" in login:
                totp = login["totp"]

            # take just the first URL
            url = ""
            if uris:
                url = uris[0]

            groups[group]["Entry"].append(
                get_kp_entry(
                    title,
                    username=username,
                    password=password,
                    url=url,
                    otp=totp,
                    notes="\n".join(notes),
                )
            )
    return groups.values()


def main():
    groups = parse()
    root = {"Group": {"Name": "Root", "Group": groups}}

    # xml document contents
    xml = dict(KeePassFile=dict(Root=root))

    # write XML document to stdout
    print(xmltodict.unparse(xml, pretty=True))


if __name__ == "__main__":
    main()
