"""Full mock of the builtin 'os' module for blazing-fast unit-testing."""
from pathlib import Path
import typing

from device import FakeDevice
from environment import FakeEnvironment
from filesystem import FakeFilesystem
from operating_system import OperatingSystem, Unix
from fakeuser import FakeUser, Root


class FakeOS(object):
    """I mock the 'os' module"""

    # pylint: disable=too-many-arguments
    def __init__(self, cwd: Path = None,
                 filesystem: FakeFilesystem = None,
                 environment: FakeEnvironment = None,
                 user: FakeUser = None,
                 operating_system: OperatingSystem = None,
                 fake_device: typing.Type[FakeDevice]=FakeDevice):

        self.cwd = cwd or Path(__file__)
        self.filesystem = filesystem or FakeFilesystem(user=user,
                                                       operating_system=operating_system)
        self.environment = environment or FakeEnvironment()
        self.device = fake_device
        self.user = user or Root()
        self.operating_system = operating_system or Unix()

    def mkdir(self, path: str, mode: int = 0o777):
        """Create a directory named path with numeric mode mode.

        If the directory already exists, FileExistsError is raised.
        If the parent directory does not exist, FileNotFound is raised.

        On some systems, mode is ignored.
        Where it is used, the current umask value is first masked out.
        If bits other than the last 9 (i.e. the last 3 digits of the
        octal representation of the mode) are set,
        their meaning is platform-dependent.
        On some platforms, they are ignored and you should call chmod()
        explicitly to set them."""
        self.filesystem.mkdir(Path(path), mode=mode)

    def listdir(self, path: str) -> list:
        """Return a list containing the names of the entries in the directory
        given by path. The list is in arbitrary order, and does not include the
        special entries '.' and '..' even if they are present in the
        directory."""
        file_objects = self.filesystem.listdir(Path(path))
        return [file_object.name for file_object in file_objects]

    def getcwd(self) -> str:
        """"Return a string representing the current working directory."""
        return str(self.cwd.absolute())

    def chdir(self, path: str):
        """Change the current working directory to path.
        If the directory does not exist FileNotFound is raised.
        If the file is not a directory, NotADirectory is raised."""
        if not self.filesystem.has(Path(path)):
            raise FileNotFoundError(path)

        if self.filesystem.has_file(Path(path)):
            raise NotADirectoryError(path)

        self.cwd = Path(path)

    def environ(self) -> dict:
        """A dictionary representing the string environment.
        For example, environ['HOME'] is the pathname of your home directory
        (on some platforms), and is equivalent to getenv("HOME") in C.
        This mapping is captured the first time the os module is imported,
        typically during Python startup as part of processing site.py.
        Changes to the environment made after this time are not reflected in
        os.environ, except for changes made by modifying os.environ directly."""
        return self.environment.environ()

    def getenv(self, key: str, default: str = None) -> str:
        """Return the value of the environment variable key if it exists,
        or default if it doesn’t. key, default and the result are str."""
        return self.environment.getenv(key, default)

    def putenv(self, key: str, value: str):
        """Set the environment variable named key to the string value.
        Such changes to the environment affect subprocesses started with
        os.system(), popen() or fork() and execv().
        Availability: most flavors of Unix, Windows.

        Note:
             On some platforms, including FreeBSD and Mac OS X, setting
             environ may cause memory leaks. Refer to the system documentation
             for putenv.
        """
        self.environment.putenv(key, value)

    def makedirs(self, name, mode: int = 0o77, exist_ok: bool = False):
        """Recursive directory creation function.
        Like mkdir(), but makes all intermediate-level directories needed
        to contain the leaf directory. The mode parameter is passed to mkdir()
        see the mkdir() description for how it is interpreted.
        If exist_ok is False (the default), an OSError is raised if the
        target directory already exists.
         """
        self.filesystem.makedirs(Path(name), mode=mode, exist_ok=exist_ok)

    def chown(self, path: str, uid: int = -1, gid: int = -1):
        """Change the owner and group id of path to the numeric uid and gid.
        To leave one of the ids unchanged, set it to -1.
        Availability: Unix.
        """
        self.filesystem.chown(Path(path), uid, gid)

    def chmod(self, path: str, mode: int):
        """"Change the mode of path to the numeric mode.
        mode may take one of the following values (as defined in
        the stat module) or bitwise ORed combinations of them:
            stat.S_ISUID
            stat.S_ISGID
            stat.S_ENFMT
            stat.S_ISVTX
            stat.S_IREAD
            stat.S_IWRITE
            stat.S_IEXEC
            stat.S_IRWXU
            stat.S_IRUSR
            stat.S_IWUSR
            stat.S_IXUSR
            stat.S_IRWXG
            stat.S_IRGRP
            stat.S_IWGRP
            stat.S_IXGRP
            stat.S_IRWXO
            stat.S_IROTH
            stat.S_IWOTH
            stat.S_IXOTH"""
        self.filesystem.chmod(Path(path), mode)

    def rmdir(self, path: str):
        """Remove (delete) the directory path. Only works when the directory
        is empty, otherwise, OSError is raised. """
        return self.filesystem.rmdir(Path(path))

    def remove(self, path: str):
        """Remove (delete) the file path. If path is a directory,
        OSError is raised. Use rmdir() to remove directories.
        This function is semantically identical to unlink()."""
        self.filesystem.remove(Path(path))

    def unlink(self, path: str):
        """Remove (delete) the file path. This function is semantically
        identical to remove(); the unlink name is its traditional Unix name.
        Please see the documentation for remove() for further information."""
        self.remove(path)

    def makedev(self, major: int, minor: int) -> int:
        """Compose a raw device number from the major and minor
        device numbers."""
        return self.device.from_major_and_minor(major, minor).device

    def major(self, device: int) -> int:
        """Extract the device major number from a raw device number
        (usually the st_dev or st_rdev field from stat)."""
        return self.device(device).major

    def minor(self, device: int) -> int:
        """Extract the device minor number from a raw device number
        (usually the st_dev or st_rdev field from stat)."""
        return self.device(device).minor

    def rename(self, src, dst):
        """Rename the file or directory src to dst. If dst is a directory,
         OSError will be raised. On Unix, if dst exists and is a file,
         it will be replaced silently if the user has permission. On Windows,
         if dst already exists, OSError will be raised even if it is a file.

         The operation may fail on some Unix flavors if src and dst are on
         different filesystems. If successful, the renaming will be an atomic
         operation (this is a POSIX requirement).

         If you want cross-platform overwriting of the destination,
         use replace()."""
        return self.filesystem.rename(Path(src), Path(dst))
