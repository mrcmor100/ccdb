import sys
from ccdb.model import User
from ccdb.provider import AlchemyProvider
from ccdb.errors import UserExistsError
import shlex
import sys
import select
import argparse

def print_help():
    print("""
This utility can add users to ccdb database by user names.
The idea behind this utility is to recreate users list from cronjob.

Usage:
    <comma separated user names> | python users_create.py --recreate mysql://ccdb_user@localhost/ccdb

Flags:
    --recreate   - delete all users before create users.
    User deletion doesn't affect logs. The script does not delete system users: "anonymous", "test_user".

Examples:
    #recreate user list from halld group
    ypmatch halld group | python users_create.py --recreate mysql://ccdb_user@localhost/ccdb

    #just add 3 users
    echo "anna,bob,smith' | python users_create.py mysql://ccdb_user@localhost/ccdb

The scripts fails if no '--recreate' flag is given and a user exists.
    """)


def get_provider(con_str):
    """Gets alchemy provider connected with this connection string

    @return AlchemyProvider()"""
    provider = AlchemyProvider()
    provider.logging_enabled = False
    provider.connect(con_str)
    return provider


def delete_users(provider):
    god_list = ["anonymous", "test_user"]
    assert isinstance(provider, AlchemyProvider)

    users = provider.get_users()
    deleted_count = 0
    for user in users:
        if not user.name in god_list:
            provider.delete_user(user.name)
            deleted_count += 1
    print("Users deleted {}".format(deleted_count))


def get_names():
    import subprocess

    groupid = 267
    group_count = 0
    output = []

    # Execute the 'getent group' command
    proc = subprocess.Popen(['getent', 'group'], stdout=subprocess.PIPE, text=True)

    # Read the output line by line
    for line in proc.stdout:
        if f':{groupid}:' in line:
            group_count += 1
            if group_count > 1:
                output.append(',')
            # Split the line and get the part after the group ID
            parts = line.strip().split(f':{groupid}:')
            if len(parts) > 1:
                output.append(parts[1])

    # Join the output list into a single string and print
    print(''.join(output))
    return output

def get_user_names_from_ypmatch(ypstr):
    """
    ypmatch string is like "halld:*:267:marki,davidl,...,jrsteven". This function trim it and returns username as list

    @return: List of strings
    @rtype: [str]
    """

    line = ypstr
    assert isinstance(line,str)
    if ':' in line:
        line = line[line.rfind(':')+1:]

    if '\n' in line:
        line = line.replace('\n', '')

    lexer = shlex.shlex(line)
    lexer.whitespace += '.,'
    return [token for token in lexer]


def create_users(provider, user_names):
    """

    @param provider:Connected alchemy provider
    @param user_names: list of user names
    """
    count = 0
    for name in user_names:
        try:
            provider.create_user(name)
            count += 1
        except UserExistsError as err:
            print(err.message)

    print("Users created: {}".format(len(user_names)))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Utility to add users to the ccdb database from cronjobs.")
    parser.add_argument('connection_string', type=str, help='Connection string for the database, e.g., mysql://ccdb_user@localhost/ccdb')
    parser.add_argument('--recreate', action='store_true', help='Delete all users before creating new ones')
    args = parser.parse_args()
    return args.connection_string, args.recreate


def main():
    # Parse command line arguments
    connection_str, recreate = parse_arguments()

    connection_str = ""
    recreate = False

    # Check stdin for usernames
    names = get_names()
    if not names:
        print("No user names found in stdin (pipe). Script continues to delete somebody if --recreate flag is given...")
        exit(1)

    # light parse arguments
    for token in sys.argv[1:]:
        if token == "--recreate":
            recreate = True
        else:
            connection_str = token

    # check we have a connection string
    if not connection_str:
        print("Error! No connection string given!")
        print_help()
        sys.exit(1)
    print("Connecting to '" + connection_str + "'")

    provider = get_provider(connection_str)
    provider.get_root_directory()   # this will load directories and ensure that ccdb structure is in place

    # delete old users if needed
    if recreate:
        print ("Deleting users...")
        try:
            delete_users(provider)
        except Exception as ex:
            print("User deletion failed with error of type {} : {}".format(type(ex), str(ex)))
            sys.exit(2)

    # create new users
    try:
        create_users(provider, names)
    except Exception as ex:
        print("User creation failed with error of type {} : {}".format(type(ex), str(ex)))
        sys.exit(3)


if __name__ == "__main__":
    get_names()
    #main()
