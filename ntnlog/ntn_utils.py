import os


def get_working_dir() -> str:
    """Return the current working directory as an absolute path."""
    return os.getcwd()


def resolve_path(path: str, must_exist: bool = False) -> str:
    """
    Resolve *path* relative to the working directory and verify it stays within it.

    Containment is decided on real paths (symbolic links resolved) and compared
    component-wise. A sibling directory whose name only shares the working
    directory's string prefix, and a symlink that points outside the working
    directory, are both rejected.

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
        Resolved absolute path. Symbolic links in the returned path are not
        expanded; the real path is used only for the containment check.

    Raises
    ------
    ValueError
        If the resolved path escapes the working directory.
    FileNotFoundError
        If ``must_exist`` is ``True`` and the path does not exist.
    """
    cwd = get_working_dir()
    resolved = os.path.normpath(os.path.join(cwd, path))

    # ``startswith`` treats ``/tmp/home/xy`` as inside ``/tmp/home/x`` and
    # does not follow symlinks. Compare real path components instead.
    cwd_real = os.path.realpath(cwd)
    resolved_real = os.path.realpath(resolved)
    if os.path.commonpath([cwd_real, resolved_real]) != cwd_real:
        raise ValueError(
            f"Path '{path}' escapes the working directory '{cwd}'"
        )

    if must_exist and not os.path.exists(resolved):
        raise FileNotFoundError(
            f"Path '{resolved}' does not exist"
        )

    return resolved
