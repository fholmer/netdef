import binascii
import os
import shutil
import subprocess

import werkzeug.security


def create_pass(password):
    return werkzeug.security.generate_password_hash(password).replace("$", "$$")


def create_new_secret():
    return binascii.hexlify(os.urandom(16)).decode("ascii")


def check_user_and_pass(app, user, password):
    # check if pwhash is used
    admin_users = app.config["ADMIN_USERS"]
    user_info = admin_users.get(user, None)
    if not user_info:
        return False

    admin_pw_hash = user_info["password_hash"]
    admin_pw_hash = admin_pw_hash.replace("$$", "$")

    if admin_pw_hash:
        if werkzeug.security.check_password_hash(admin_pw_hash, password):
            return True
    else:
        # fallback til plaintext
        admin_password = user_info["password"]
        if password == admin_password:
            return True
    return False


# default cert filenames:
default_pem_file = os.path.join("ssl", "certs", "certificate.pem")
default_key_file = os.path.join("ssl", "private", "certificate.pem.key")
default_der_file = os.path.join("ssl", "certs", "certificate.der")
default_derkey_file = os.path.join("ssl", "private", "certificate.der.key")


def can_generate_certs():
    if shutil.which("openssl") is None:
        return False
    else:
        return True


def generate_overwrite_certificates(
    pem_file, key_file, der_file, derkey_file, common_name, days=3650
):
    cmd_req_pem = [
        "openssl",
        "req",
        "-x509",
        "-sha256",
        "-newkey",
        "rsa:2048",
        "-keyout",
        key_file,
        "-out",
        pem_file,
        "-days",
        str(days),
        "-nodes",
    ]

    cmd_der = ["openssl", "x509", "-outform", "der", "-in", pem_file, "-out", der_file]
    cmd_der_key = [
        "openssl",
        "rsa",
        "-outform",
        "der",
        "-in",
        key_file,
        "-out",
        derkey_file,
    ]

    os.makedirs(os.path.join("ssl", "certs"), exist_ok=True)
    os.makedirs(os.path.join("ssl", "private"), exist_ok=True)

    if common_name:
        cmd_req_pem.append("-subj")
        cmd_req_pem.append("/CN={:s}".format(common_name))
    else:
        cmd_req_pem.append("-batch")

    res = subprocess.run(cmd_req_pem, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        return "{}\n{}".format(res.stdout, res.stderr)

    res = subprocess.run(cmd_der, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        return "{}\n{}".format(res.stdout, res.stderr)

    res = subprocess.run(cmd_der_key, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        return "{}\n{}".format(res.stdout, res.stderr)

    return ""
