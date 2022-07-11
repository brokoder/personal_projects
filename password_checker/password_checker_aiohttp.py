"""
This is a script used for checking if the password used is a common password.
Using such a password doesn't mean your account can be hacked because
password salting is a commonly used standard in most of the services but it
is not advisable.

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
import aiohttp


def start():
    """
    To be executed at the start
    """
    parser = argparse.ArgumentParser(
        description="This script is used for checking the list of passwords asynchronously. \
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

def get_tasks(session, format_passwords):
    """
    Getting the async tasks
    """
    tasks = []
    for hashed_pw in format_passwords.values():
        url = f"https://api.pwnedpasswords.com/range/{hashed_pw[:5]}"
        tasks.append(asyncio.create_task(session.get(url, ssl=False)))
    return tasks


async def main(passwords):
    """
    Main task
    """
    format_passwords = {
        password: hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        for password in passwords
    }
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, format_passwords)
        responses = await asyncio.gather(*tasks)
        for index, password in enumerate(passwords):
            response_txt = await responses[index].text()
            compromised_passwords = response_txt.splitlines()
            hashes = {
                line.split(":")[0]: line.split(":")[1] for line in compromised_passwords
            }
            if format_passwords[password][5:] in hashes:
                print(
                    f"The password {password} is exposed\
                        {hashes[format_passwords[password][5:]]} times"
                )
    return


if __name__ == "__main__":
    passwords_input: list = start()
    if passwords_input == []:
        raise EOFError("Please input the passwords to check")
    asyncio.run(main(passwords_input))
