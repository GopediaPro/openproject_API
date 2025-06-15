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

def get_work_packages_list_endpoint(openproject_url, offset=None, page_size=None):
    """
    Returns the API endpoint for listing work packages with optional offset and pageSize.
    """
    base = f"{openproject_url}/api/v3/work_packages"
    params = []
    if offset is not None:
        params.append(f"offset={offset}")
    if page_size is not None:
        params.append(f"pageSize={page_size}")
    if params:
        return base + "?" + "&".join(params)
    return base
