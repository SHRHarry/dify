import base64
import binascii
import hashlib
import re
import os
import logging
from ldap3 import Server, Connection, ALL

password_pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"


def valid_password(password):
    # Define a regex pattern for password rules
    pattern = password_pattern
    # Check if the password matches the pattern
    if re.match(pattern, password) is not None:
        return password

    raise ValueError("Password must contain letters and numbers, and the length must be greater than 8.")


def hash_password(password_str, salt_byte):
    dk = hashlib.pbkdf2_hmac("sha256", password_str.encode("utf-8"), salt_byte, 10000)
    return binascii.hexlify(dk)


def compare_password(password_str, password_hashed_base64, salt_base64):
    # compare password for login
    return hash_password(password_str, base64.b64decode(salt_base64)) == base64.b64decode(password_hashed_base64)

def verify_password_from_ldap(user_name, user_password) -> bool:
    # Set username to lower case
    user_name = user_name.lower()

    # Set up LDAP server connection information
    server_uri = os.getenv("LDAP_SERVER_HOST", "localhost")
    manager_dn = os.getenv("LDAP_MANAGER_DN", "cn=admin,dc=example,dc=org")
    manager_password = os.getenv("LDAP_MANAGER_PASSWORD", "manager_password")
    user_search_base = os.getenv("LDAP_SEARCH_BASE", "ou=users,dc=example,dc=org")
    
    print('server_uri:', server_uri)
    logging.info(f"server_uri: {server_uri} username: {user_name} user_password: {user_password}")
    
    # Establish a connection to the LDAP server
    server = Server(server_uri)
    conn = Connection(server, manager_dn, manager_password)
    
    try:
        # Bind as the manager
        if not conn.bind():
            logging.error('Error: Could not bind as manager.')
            return False

        # Search for the user's dn
        conn.search(user_search_base, f'(uid={user_name})', attributes=['cn'])
        if not conn.entries:
            logging.error('Error: User not found.')
            return False
        user_dn = conn.entries[0].entry_dn

        # Attempt to bind as the user
        user_conn = Connection(server, user_dn, user_password)
        if user_conn.bind():
            logging.error('Success: Password verified.')
            return True
        else:
            logging.error('Error: Password verification failed.')
            return False
    finally:
        # Ensure the connection is closed
        conn.unbind()
        
def extract_account(email):
    try:
        # Check if '@' is in the email address
        if '@' not in email:
            raise ValueError("Invalid email address: missing '@' character.")
        
        # Split the email at '@' and return the first part
        account = email.split('@')[0]
        
        # Check if the account part is empty
        if not account:
            raise ValueError("Invalid email address: missing account part before '@'.")
        
        return account
    except Exception as e:
        return f"Error: {e}"        