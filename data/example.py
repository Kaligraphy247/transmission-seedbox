from getpass import getpass

username = input("Enter your username: ")
password = getpass("Enter your password: ")

print(f"connecting with username `{username}` and password `{password}`.")