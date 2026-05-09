from pathlib import Path
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

USERS_FILE = Path("users.yaml")


def load_authenticator():
    with open(USERS_FILE) as f:
        config = yaml.load(f, Loader=SafeLoader)
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    ), config


def add_user(username: str, name: str, email: str, password: str):
    """Añade un nuevo usuario al fichero YAML con contraseña cifrada."""
    import bcrypt
    with open(USERS_FILE) as f:
        config = yaml.load(f, Loader=SafeLoader)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    config["credentials"]["usernames"][username] = {
        "email": email,
        "name": name,
        "password": hashed,
    }
    with open(USERS_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
