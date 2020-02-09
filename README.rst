=================
iofile
=================

iofile is a module for convenient work with paths as objects. iofile contains class Path - abstract representation of file and directory pathnames.
Path uses standard-library modules like os, os.path, shutil, tempfile and combines their features in one class

Features:
• System-independent
• Path information: size, modification time, access time, creation time, name, parent
• Copying directories
• Moving trees
• Getting absolute, canonical path
• Creating and deleting (e.g. recursively) files or directories
• Getting disk usage
• Creating temp files and directories

Python 3.6+ recommended. 