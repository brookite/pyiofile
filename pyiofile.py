import os
import shutil
import sys
import tempfile
import stat
import platform
import time

__VERSION__ = "1.0a.dev3"


class Path(os.PathLike):
    """
    An abstract representation of file and directory pathnames.
    The library uses the standard features of the Python
    language for working with paths. Wraps them in one class

    Constructor:
    Path(*args) - Collects all path elements in one path using a standard separator
    Path(pth) - Uses the passed argument as a string or bytes-like
    or path-like object as a path
    Path() - sets as default the current working directory

    expandvars - uses standard-library method os.path.expandvars

    Path attributes: name, size, last_access, last_modified, ctime, creation_time,
    path

    """
    _separator = os.sep

    def __init__(self, *args, expandvars=True):
        if len(args) == 0:
            args = [os.getcwd()]
        if str(args[0]).endswith(":"):
            args = list(args)
            args[0] = args[0] + self._separator
        self.__path = os.path.join(*args)
        if expandvars:
            self.__path = os.path.expandvars(self.__path)

    @staticmethod
    def separator():
        """
        Default path separator in current operating system
        """
        return Path._separator

    def absolute_path(self):
        """
        Returns absolute path of current path
        """
        return Path(os.path.abspath(self.path))

    @classmethod
    def cwd(cls):
        """
        Returns current (working) directory path object, equals os.getcwd()
        """
        return cls(os.getcwd())

    @classmethod
    def userdir(cls):
        """
        Returns current user home directory path object
        """
        return cls(os.path.expanduser("~"))

    @classmethod
    def home(cls):
        """
        Returns current user home directory path object
        """
        return cls(os.path.expanduser("~"))

    def __fspath__(self):
        return self.path

    @classmethod
    def currentfile_path(cls, globalvars=globals()):
        """
        Returns a current execution file (like jpg, zip and etc.)
        If it is not possible returns current directory path

        The method does not guarantee the correct result.
        It is recommended to call passing in arguments globals()

        The method works based on checking the contents of the global variable __file__

        Good example: Path.currentfile_path(globalvars=globals())
        Bad example (undefined behaviour):  Path.currentfile_path()
        """
        if "__file__" in globalvars:
            return cls(__file__)
        else:
            return cls(os.getcwd())

    def is_link(self):
        """
        Test whether a path is a symbolic link.
        This will always return false for Windows prior to 6.0
        """
        return os.path.islink(self.path)

    def is_mount(self):
        """
        Test whether a path is a mount point
        (a drive root, the root of a share, or a mounted volume)
        """
        return os.path.ismount(self.path)

    def split(self):
        """
        Returns a tuple of hierarchical elements of path
        """
        return self.path.split(os.sep)

    def get_canonical(self):
        """
        Returns string representation of the canonical path of current path object
        """
        return os.path.realpath(self.path)

    def get_canonical_path(self):
        """
        Returns path object representation of the canonical path of current path object
        """
        return Path(self.get_canonical())

    def get_ext(self):
        """
        Returns the extension of current path (str), if not file - returns None
        """
        if (self.is_file()):
            return os.path.splitext(self.path)[1]

    def __str__(self):
        return self.path

    def __repr__(self):
        return "<Path: {}>".format(self.name)

    def is_file(self):
        """
        Tests whether the path is a normal file.
        """
        return os.path.isfile(self.path)

    def is_dir(self):
        """
        Tests whether the path is a directory.
        """
        return os.path.isdir(self.path)

    def open(self, *args, **kwargs):
        """
        Opens a standard Python file wrapper.
        This method unlike 'open' method don't accept file path

        Example: path.open("w", encoding="utf-8")
        """
        return open(self.get_absolute(), *args, **kwargs)

    def can_read(self):
        """
        Tests whether the application can read the file by this abstract pathname
        """
        return os.access(self.get_absolute(), os.R_OK)

    def can_execute(self):
        """
        Tests whether the application can execute the file by this abstract pathname
        """
        return os.access(self.get_absolute(), os.X_OK)

    def can_write(self):
        """
        Tests whether the application can write the file by this abstract pathname
        """
        return os.access(self.get_absolute(), os.W_OK)

    def set_last_modified(self, time=time.time()):
        """
        Sets the last-modified and last-accessed time of the path.

        time - UNIX-time seconds (int or float)
        """
        return os.utime(self, (time, time))

    def set_readable(self, readable, owners_only=True):
        """
        Sets the owner's or everybody's read permission for this abstract pathname.

        If owners_only is true method sets only owner's read permission, else - everybody
        """
        arg = stat.S_IRUSR if owners_only else 0o444
        if readable:
            if self.can_read():
                return
            else:
                self.chmod(self.stat().st_mode ^ arg)
        else:
            if not self.can_read():
                return
            else:
                self.chmod(self.stat().st_mode ^ arg)

    def set_writable(self, writable, owners_only=True):
        """
        Sets the owner's or everybody's write permission for this abstract pathname.

        If owners_only is true method sets only owner's write permission, else - everybody
        """
        arg = stat.S_IWUSR if owners_only else 0o222
        if writable:
            if self.can_write():
                return
            else:
                self.chmod(self.stat().st_mode ^ arg)
        else:
            if not self.can_write():
                return
            else:
                self.chmod(self.stat().st_mode ^ arg)

    def set_executable(self, executable, owners_only=True):
        """
        Sets the owner's or everybody's execute permission for this abstract pathname.

        If owners_only is true method sets only owner's execute permission,
        else - everybody
        """
        arg = stat.S_IXUSR if owners_only else 0o111
        if executable:
            if self.can_execute():
                return
            else:
                self.chmod(self.stat().st_mode ^ arg)
        else:
            if not self.can_execute():
                return
            else:
                self.chmod(self.stat().st_mode ^ arg)

    def set_readonly(self):
        """
        Marks the file or directory named by this abstract pathname
        so that only read operations are allowed for owners, group,
        others.
        """
        if platform.system() == "Windows":
            import win32api
            import win32con
            win32api.SetFileAttributes(self.get_absolute(), win32con.FILE_ATTRIBUTE_READONLY)
        else:
            self.chmod(0o444)

    def chmod(self, *args, **kwargs):
        """
        Change the access permissions of a file. Wrapper for standard-library method
        os.chmod
        """
        os.chmod(self, *args, **kwargs)

    def stat(self):
        """
        Perform a stat system call on the given path.
        Wrapper for standard-library method os.stat
        """
        return os.stat(self)

    def create_new_file(self):
        """
        Creates a new, empty file named by this abstract pathname
        Returns - true if file was successfully created;
        false - if file exists or raised any exception
        """
        try:
            if not self.exists():
                self.open("w").close()
                return True
            else:
                return False
        except Exception:
            return False

    def mkdir(self):
        """
        Creates the directory named by this abstract pathname.
        Returns - true if directory was successfully created;
        false - if directory exists or raised any exception
        """
        try:
            if not self.exists():
                os.mkdir(self.get_absolute())
                return True
            else:
                return False
        except Exception:
            return False

    def delete(self):
        """
        Tries to remove path in filesystem
        """
        try:
            if self.is_dir():
                os.rmdir(self.get_absolute())
            else:
                os.remove(self.get_absolute())
            return True
        except Exception:
            return False

    def rdelete(self):
        """
        Tries to recursively remove path in filesystem. Example: non-empty directory
        """
        try:
            if self.is_dir():
                shutil.rmtree(self.get_absolute())
            else:
                os.remove(self.get_absolute())
            return True
        except Exception:
            return False

    def exists(self):
        """
        Tests whether path exists
        """
        return os.path.exists(self.get_absolute())

    def is_absolute(self):
        """
        Tests whether path is absolute
        """
        return os.path.isabs(self.path)

    @staticmethod
    def copy(path1, path2, symlinks=True):
        """
        Copy file or directory from one path to another using standard-library
        method shutil.copy2
        """
        path1 = path1.get_absolute()
        path2 = path2.get_absolute()
        return Path(shutil.copy2(path1, path2, follow_symlinks=symlinks))

    @staticmethod
    def rcopy(path1, path2, symlinks=False):
        """
        Recursively copy tree of files or directories from one path
        to another using standard-library
        method shutil.copytree
        """
        path1 = path1.get_absolute()
        path2 = path2.get_absolute()
        return Path(shutil.copytree(path1, path2, symlinks=symlinks,
                                    copy_function=shutil.copy2))

    @staticmethod
    def move(path1, path2):
        """
        Recursively move file or directoru or directories from one path
        to another using standard-library
        method shutil.copytree
        """
        path1 = path1.get_absolute()
        path2 = path2.get_absolute()
        shutil.move(path1, path2, copy_function=shutil.copy2)

    def list(self, full_path=False):
        """
        Returns a tuple of strings naming the files and directories
        in the directory denoted by this abstract pathname.

        If full_path returns tuple with absolute-path strings
        """
        directory = os.listdir(self.get_absolute())
        if full_path:
            for i in range(len(directory)):
                directory[i] = os.path.join(self.get_absolute(), directory[i])
        return tuple(directory)

    def list_files(self):
        """
        Returns a tuple of abstract pathnames with files denoted
        by this abstract pathname.
        """
        directory = os.listdir(self.get_absolute())
        files = []
        for i in range(len(directory)):
            directory[i] = Path(self.get_absolute(), directory[i])
            if directory[i].is_file():
                files.append(directory[i])
        return tuple(files)

    def list_dirs(self):
        """
        Returns a tuple of abstract pathnames with directories
        denoted by this abstract pathname.
        """
        directory = os.listdir(self.get_absolute())
        dirs = []
        for i in range(len(directory)):
            directory[i] = Path(self.get_absolute(), directory[i])
            if directory[i].is_dir():
                dirs.append(directory[i])
        return tuple(dirs)

    def list_paths(self):
        """
        Returns a tuple of abstract pathnames with files and dirs
        denoted by this abstract pathname.
        """
        directory = os.listdir(self.get_absolute())
        for i in range(len(directory)):
            directory[i] = Path(self.get_absolute(), directory[i])
        return tuple(directory)

    def get_root(self):
        """
        Returns the filesystem root.
        """
        return Path(Path(self.get_absolute()).split()[0] + self.separator())

    def splitdrive(self):
        """
        Analog to os.path.splitdrive
        """
        return Path(os.path.splitdrive(self.get_absolute())[0])

    def get_relative(self):
        """
        Returns relative path string of current path
        """
        return os.path.relpath(self.get_absolute())

    def get_relative_path(self):
        """
        Returns relative path of current path
        """
        return Path(os.path.relpath(self.get_absolute()))

    def is_hidden(self):
        """
        Tests whether the file named by this abstract pathname is a hidden file.
        In UNIX systems checks if filename starts with "."
        """
        if platform.system() == 'Windows':
            return bool(os.stat(self).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
        else:
            return self.name.startswith(".")

    def set_hidden(self, hidden):
        """
        Sets this path as hidden.
        In UNIX systems adds "." to to the beginning of the filename
        """
        if platform.system() == 'Windows':
            import win32api
            import win32con
            readonly = self.can_read()
            if hidden:
                flag = win32con.FILE_ATTRIBUTE_HIDDEN
            else:
                flag = win32con.FILE_ATTRIBUTE_NORMAL
            win32api.SetFileAttributes(self.get_absolute(), flag)
            if readonly:
                self.set_readonly()
        else:
            if hidden:
                self.rename("." + self.name)
            else:
                if self.name.startswith("."):
                    self.rename(self.name[1:])

    def norm_path(self):
        """
        Normalizes the path using standard-library method os.path.normcase
        and os.path.normpath
        """
        return Path(os.path.normcase(os.path.normpath(self)))

    @staticmethod
    def list_roots():
        """
        List the available filesystem roots.
        """
        if sys.platform == "win32":
            import win32api
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            for i in range(len(drives)):
                drives[i] = Path(drives[i])
        else:
            return [Path("/")]

    def __eq__(self, other):
        return os.path.samefile(self, other)

    @property
    def last_modified(self):
        if self.exists():
            return os.path.getmtime(self.get_absolute())

    @property
    def last_access(self):
        if self.exists():
            return os.path.getatime(self.get_absolute())

    @property
    def ctime(self):
        if self.exists():
            return os.path.getctime(self.get_absolute())

    @property
    def creation_time(self):
        if self.exists():
            if platform.system() == 'Windows':
                return os.path.getctime(self)
            else:
                stat = os.stat(self)
                try:
                    return stat.st_birthtime
                except AttributeError:
                    return stat.st_mtime

    def __len__(self):
        return self.size

    def get_totalspace(self):
        """
        Returns the size of the partition named by this abstract pathname.
        """
        return shutil.disk_usage(self.get_root())[0]

    def get_usedspace(self):
        """
        Returns the number of bytes available on the partition named
        by this abstract pathname
        """
        return shutil.disk_usage(self.get_root())[1]

    def get_freespace(self):
        """
        Returns the number of unallocated bytes in the partition named
        by this abstract pathname.
        """
        return shutil.disk_usage(self.get_root())[2]

    @staticmethod
    def create_temp_file(*args, **kwargs):
        """
        Creates a new empty file in the specified directory,
        using the given prefix and suffix strings to generate its name.

        Some importantly optional arguments:
        suffix
        prefix
        mode (default "w+b")
        encoding

        Wrapper for standard-library class constructor tempfile.TemporaryFile
        """
        t = tempfile.TemporaryFile(*args, **kwargs)
        return _TemporaryPath(t)

    @staticmethod
    def create_temp_dir(*args, **kwargs):
        """
        Creates a directory in the specified directory,
        using the given prefix and suffix strings to generate its name.

        Some importantly optional arguments:
        suffix
        prefix
        mode (default "w+b")
        encoding

        Wrapper for standard-library class constructor tempfile.TemporaryDirectory
        """
        t = tempfile.TemporaryDirectory(*args, **kwargs)
        return TemporaryPath(t)

    @property
    def name(self):
        if self.exists():
            return os.path.split(self.get_absolute())[1]

    @property
    def size(self):
        if self.exists():
            return os.stat(self.get_absolute()).st_size

    def mkdirs(self):
        """
        Creates the directory named by this abstract pathname,
        including any necessary but nonexistent parent directories.
        """
        try:
            if not self.exists():
                os.makedirs(self.get_absolute())
                return True
            else:
                return False
        except Exception:
            return False

    def get_parent_path(self):
        """
        Returns the path of this abstract pathname's parent,
        or current path if this pathname does not name a parent directory.
        """
        return Path(os.path.split(self.get_absolute())[0])

    def get_parent(self):
        """
        Returns the path of this abstract pathname's parent,
        or current path if this pathname does not name a parent directory.
        """
        return os.path.split(self.get_absolute())[0]

    def get_absolute(self):
        """
        Returns the absolute pathname string of this abstract pathname.
        """
        return os.path.abspath(self.path)

    def __iter__(self):
        if self.is_dir():
            return iter(self.list_paths())
        else:
            raise OSError("File is not iterable")

    def rename(self, newname):
        """
        Renames the file denoted by this abstract pathname.
        """
        try:
            pth = self.get_parent()
            new = Path(pth, newname)
            os.rename(self, new)
            return new
        except Exception:
            return None

    def is_temp(self):
        """
        Returns true if abstract pathname object inherited from TemporaryPath file
        """
        return False

    @property
    def path(self):
        return self.__path


class _TemporaryPath(Path):
    """
    Temporary abstract pathnames representation

    It is highly recommended that you do not explicitly call
    the constructor of this class.
    To create class instances, use Path.create_temp_file or Path.create_temp_dir

    When working with an instance, it is highly recommended
    to use the TemporaryPath.open method
    for working with reading / writing a file.

    TemporaryPath attributes (not including attributes from Path): tmp
    """

    def __init__(self, tmp):
        self.__tmp = tmp
        self.__path = tmp.name

    @property
    def path(self):
        return self.__path

    def is_temp(self):
        return True

    def open(self):
        return self.__tmp

    def delete(self):
        super().delete()
        self.free()

    def rdelete(self):
        super().rdelete()
        self.free()

    def free(self):
        if self.is_dir():
            self.__tmp.cleanup()

    @property
    def tmp(self):
        return self.__tmp
