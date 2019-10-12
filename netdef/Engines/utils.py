import os
import binascii
import subprocess
import shutil
import werkzeug.security

def create_pass(password):
    return werkzeug.security.generate_password_hash(password).replace("$", "$$")

def create_new_secret():
    return binascii.hexlify(os.urandom(16)).decode('ascii')

def check_user_and_pass(app, password):
    # check if pwhash is used
    admin_pw_hash = app.config["ADMIN_PASSWORD_HASH"]
    admin_pw_hash = admin_pw_hash.replace("$$", "$")

    if admin_pw_hash:
        if werkzeug.security.check_password_hash(admin_pw_hash, password):
            return True
    else:
        # fallback til plaintext
        admin_password = app.config["ADMIN_PASSWORD"]
        if password == admin_password:
            return True
    return False

# default cert filenames:
default_pem_file = "certificate.pem"
default_key_file = "certificate.pem.key"
default_der_file = "certificate.der"
default_derkey_file = "certificate.der.key"

def can_generate_certs():
    if shutil.which("openssl") is None:
        return False
    else:
        return True


def generate_overwrite_certificates(pem_file, key_file, der_file, derkey_file, common_name):
    cmd_req_pem = [
        "openssl", "req", "-x509", "-sha256", "-newkey", "rsa:2048", "-keyout",
        key_file, "-out", pem_file, "-days", "3650", "-nodes"
        ]

    cmd_der = [
        "openssl", "x509", "-outform", "der", "-in", pem_file, "-out", der_file
        ]
    cmd_der_key = [
        "openssl", "rsa", "-outform", "der", "-in", key_file, "-out", derkey_file
        ]

    if common_name:
        cmd_req_pem.append("-subj")
        cmd_req_pem.append("/CN={:s}".format(common_name))
    else:
        cmd_req_pem.append("-batch")
    
    subprocess.run(cmd_req_pem)
    subprocess.run(cmd_der)
    subprocess.run(cmd_der_key)
