from ansible.errors import AnsibleModuleError

MODULE_EXCEPTIONS = (ModuleNotFoundError, ImportError)


class ModuleSoftError(Exception):
    pass


def exit_bug(msg: str):
    raise AnsibleModuleError(f"THIS MIGHT BE A MODULE-BUG: {msg}")


def exit_debug(msg: str):
    raise AnsibleModuleError(f"DEBUG INFO: {msg}")


def exit_env(msg: str):
    raise AnsibleModuleError(f"ENVIRONMENTAL ERROR: {msg}")


def module_dependency_error() -> None:
    exit_env(
        'For this Ansible-module to work you must install its dependencies first: '
        "'python3 -m pip install httpx'"
    )
