# bitwarden2keepass
bitwarden json to keepass 2.x XML converter

## install
```
git clone ...
cd ...
pip install -r requirements.txt
```

## usage
```
# export bitwarden_export_*.json from bitwarden
python keepassxml.py > passwords.xml
keepassxc-cli import passwords.xml passwords.kdbx
```