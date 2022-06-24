"""
Instructions: use 'python password_async_checker.py -p "<passwords>"' or
'python password_checker.py -l <location of the txt file with the passwords>'
to enter your password.

The password u enter will not be sent to the api only first 5 characters
in the hashed sting is sent to the api.
Api will respond back with all the compromised password hashes and is
matched with the hashed password you have entered to check if it is okey.
"""

import argparse
import asyncio
import hashlib
import requests


def start():
    """
    To be executed at the start
    """
    parser = argparse.ArgumentParser(
        description="This script is used for checking the list of passwords asynchronously.\
            If the password is safe to use, then it will not be printed"
    )
    parser.add_argument(
        "-p",
        "--passwords",
        help="Enter the list of password separated by space and inside quotes",
    )
    parser.add_argument(
        "-l",
        "--location",
        help="Enter the location of the txt file that contains the passwords",
    )
    args = parser.parse_args()
    passwords = []
    if args.passwords:
        passwords = args.passwords.split()
    if args.location:
        with open(args.location) as file:
            passwords_in_file = [i.rstrip("\n") for i in file.readlines()]
            passwords.extend(passwords_in_file)
    return passwords


def http_get_sync(url: str):
    """
    Function to be added to thread
    """
    response = requests.get(url)
    return response


async def http_get(url: str):
    """
    Returns the coroutine of the api request
    """
    return await asyncio.to_thread(http_get_sync, url)


async def call_api_for_password(password, hashed_pw):
    """
    Calling of api pwnedpasswords
    """
    url = f"https://api.pwnedpasswords.com/range/{hashed_pw[:5]}"
    res = await http_get(url)
    if res.status_code != 200:
        raise RuntimeError(f"Error fetching using api. status code{res.status_code}")
    return password, res.text.splitlines()


async def main(passwords):
    """
    Main function
    """
    format_passwords = {
        password: hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        for password in passwords
    }
    compromised_password_list = await asyncio.gather(
        *[
            call_api_for_password(password, hashed_pw)
            for password, hashed_pw in format_passwords.items()
        ]
    )
    compromised_password_dict = dict(compromised_password_list)
    for password in passwords:
        hashes = {
            line.split(":")[0]: line.split(":")[1]
            for line in compromised_password_dict[password]
        }
        if format_passwords[password][5:] in hashes:
            print(
                f"The password {password} is exposed {hashes[format_passwords[password][5:]]} times"
            )


if __name__ == "__main__":
    passwords_input: list = start()
    if passwords_input == []:
        raise EOFError("Please input the passwords to check")
    asyncio.run(main(passwords_input))
