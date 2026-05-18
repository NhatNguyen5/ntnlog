import os


def get_working_dir() -> str:
    """Return the current working directory as an absolute path."""
    return os.getcwd()


def resolve_path(path: str, must_exist: bool = False) -> str:
    """
    Resolve *path* relative to the working directory and verify it stays within it.

    Parameters
    ----------
    path : str
        Relative or absolute path to resolve.
    must_exist : bool
        If ``True``, raises ``FileNotFoundError`` when the resolved path does
        not exist on disk.

    Returns
    -------
    str
        Resolved absolute path.

    Raises
    ------
    ValueError
        If the resolved path escapes the working directory.
    FileNotFoundError
        If ``must_exist`` is ``True`` and the path does not exist.
    """
    cwd = get_working_dir()
    resolved = os.path.normpath(os.path.join(cwd, path))

    if not resolved.startswith(cwd):
        raise ValueError(
            f"Path '{path}' escapes the working directory '{cwd}'"
        )

    if must_exist and not os.path.exists(resolved):
        raise FileNotFoundError(
            f"Path '{resolved}' does not exist"
        )

    return resolved
