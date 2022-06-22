"""
Instructions: use 'python password/ checker.py <password>' or
'python password/ checker.py' to enter your password.

The password u enter will not be sent to the api only first 5 characters
in the hashed sting is sent to the api.
Api will respond back with all the compromised password hashes and is 
matched with the hashed password you have entered to check if it is okey. 
"""
import hashlib
import requests
import sys


class Password:
    def __init__(self, password: str) -> None:
        self.password = password

    def get_hashed_password(self):
        return hashlib.sha1(self.password.encode("utf-8")).hexdigest().upper()

    def get_query_strings(self):
        hashed_password = self.get_hashed_password()
        return hashed_password[:5], hashed_password[5:]


class GetLeakedHashes:
    def __init__(self, password_obj: Password) -> None:
        self.query_char, self.tail =  password_obj.get_query_strings()
        self.password_used_count: int = 0

    def call_api_for_password(self):
        url = f"https://api.pwnedpasswords.com/range/{self.query_char}"
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError(
                f"Error fetching using api. status code{res.status_code}"
            )
        return res

    def check_if_password_is_okey(self):
        api_response = self.call_api_for_password()
        hashes = (line.split(":") for line in api_response.text.splitlines())
        for tail, count in hashes:
            if tail == self.tail:
                self.password_used_count = count
                return

def main(password):
    password_obj = Password(password)
    leaked_hashes = GetLeakedHashes(password_obj)
    leaked_hashes.check_if_password_is_okey()
    if leaked_hashes.password_used_count:
        print(f"This password was used {leaked_hashes.password_used_count} times")
    else:
        print("Password not found in database. You are good to go!")

if __name__ == '__main__':
    args = sys.argv
    password = args[1] if len(args) > 1 else input("Enter password:  ")
    sys.exit(main(password))
    