def build_user_payload(login, email, first_name, last_name, password):
    """
    Build a payload dict for creating a user in OpenProject.
    """
    return {
        "login": login,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "password": password
    }
