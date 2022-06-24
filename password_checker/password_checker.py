"""
Instructions: use 'python password_checker.py <password>' or
'python password_checker.py' to enter your password.

The password u enter will not be sent to the api only first 5 characters
in the hashed sting is sent to the api.
Api will respond back with all the compromised password hashes and is
matched with the hashed password you have entered to check if it is okey.
"""
import hashlib
import sys
import requests


class Password:
    """
    Class for defining the password attributes.
    """
    def __init__(self, password: str) -> None:
        self.password = password

    def get_hashed_password(self):
        """
        Return the hashed string of password
        """
        return hashlib.sha1(self.password.encode("utf-8")).hexdigest().upper()

    def get_query_strings(self):
        """
        Return the query string to be used as parameter in api.
        """
        hashed_password = self.get_hashed_password()
        return hashed_password[:5], hashed_password[5:]


class GetLeakedHashes:
    """
    Used to define the attributes of compromised password hashs
    """
    def __init__(self, password_obj: Password) -> None:
        self.query_char, self.tail = password_obj.get_query_strings()
        self.password_used_count: int = 0

    def call_api_for_password(self):
        """
        For calling the pwnedpasswords api
        """
        url = f"https://api.pwnedpasswords.com/range/{self.query_char}"
        res = requests.get(url)
        if res.status_code != 200:
            raise RuntimeError(
                f"Error fetching using api. status code{res.status_code}"
            )
        return res

    def check_if_password_is_okey(self):
        """
        For validating if the password is compromised
        """
        api_response = self.call_api_for_password()
        hashes = {
            line.split(":")[0]: line.split(":")[1]
            for line in api_response.text.splitlines()
        }
        if self.tail in hashes:
            self.password_used_count = hashes[self.tail]
            return


def main(password):
    """
    Main function
    """
    password_obj = Password(password)
    leaked_hashes = GetLeakedHashes(password_obj)
    leaked_hashes.check_if_password_is_okey()
    if leaked_hashes.password_used_count:
        print(f"This password was used {leaked_hashes.password_used_count} times")
    else:
        print("Password not found in database. You are good to go!")


if __name__ == "__main__":
    args = sys.argv
    password_input = args[1] if len(args) > 1 else input("Enter password:  ")
    sys.exit(main(password_input))
