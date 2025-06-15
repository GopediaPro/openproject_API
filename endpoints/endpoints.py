def get_user_endpoint(openproject_url):
    """
    Returns the API endpoint for users.
    """
    return f"{openproject_url}/api/v3/users"

def get_group_endpoint(openproject_url):
    """
    Returns the API endpoint for groups.
    """
    return f"{openproject_url}/api/v3/groups"

def get_work_package_endpoint(openproject_url):
    """
    Returns the API endpoint for work packages.
    """
    return f"{openproject_url}/api/v3/work_packages"
