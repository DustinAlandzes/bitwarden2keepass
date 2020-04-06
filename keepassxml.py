#!/usr/bin/env python3

import xmltodict
import glob
import json


def parseFolders(bitwardenFolders):
    folders = {}
    for folder in bitwardenFolders:
        folders[folder["id"]] = folder["name"]
    return folders


def readBitwardenJson(fname):
    with open(fname) as f:
        inJson = f.read()
        input = json.loads(inJson)
        return input


def parse():

    filename = glob.glob("bitwarden_export_*.json")[0]

    j = readBitwardenJson(filename)

    folders = parseFolders(j["folders"])
    groups = {}
    for folder in folders:
        group = folders[folder]
        # print("created group:", group)
        groups[group] = create_kp_group(str(group).title())
    # print("groups:", groups)

    for item in j["items"]:
        group = folders[item["folderId"]]
        title = item["name"]
        username = None
        password = None
        uris = []
        totp = None
        extra = []

        if "fields" in item:
            for field in item["fields"]:
                extra.append("%s: %s" % (field["name"], field["value"]))
                
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
            if uris:
                url = uris[0]
    
            groups[group]["Entry"].append(
                get_kp_entry(
                    title,
                    username=username,
                    password=password,
                    url=url,
                    otp=totp,
                    notes=', '.join(extra),
                )
            )

    return groups.values()


def create_kp_group(name):
    group = {
        "Name": name,
        "Entry": [],
    }
    return group


def get_kp_entry(title, username, password, url, notes, otp):
    entry = {
        "String": [
            {"Key": "Title", "Value": title},
            {"Key": "UserName", "Value": username},
            {"Key": "Password", "Value": password},
            {"Key": "URL", "Value": url},
            {"Key": "Notes", "Value": notes},
            {"Key": "otp", "Value": otp},
        ]
    }
    return entry


def main():
    groups = parse()
    root = {"Group": {"Name": "Root", "Group": groups}}

    # xml document contents
    xml = dict(KeePassFile=dict(Root=root))

    # write XML document to stdout
    print(xmltodict.unparse(xml, pretty=True))


if __name__ == "__main__":
    main()
