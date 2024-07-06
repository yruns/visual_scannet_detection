import platform

def get_system_type():
    system = platform.system()
    if system == "Linux":
        return "Linux"
    elif system == "Darwin":
        return "macOS"
    else:
        return "Other"

system_type = get_system_type()
print(f"The current system is: {system_type}")
