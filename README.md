# Monotool

Tool to help BigRentz with Mono building and distributing.

## Installation

If your are on OSX you can install mono and 
xbuild from brew:

```
$ brew install mono
```

Install nuget the package manager for the
Microsoft development platform

```
$ sudo wget http://nuget.org/nuget.exe -O /opt/local/bin/nuget.exe
```

Install Python virtualenv and pip 
http://docs.python-guide.org/en/latest/dev/virtualenvs/

```
$ sudo easy_install pip
$ sudo pip install virtualenv
```

Get the latest monotool source from Github:

```
$ git clone git@github.com:bigrentz/monotool.git
$ cd monotool/
```

Copy the example config to your user profile and edit:

```
$ cp monotool.conf.example ~/.monotool.conf
$ vim ~/.monotool.conf
```

Create a activate Python virtualenv for site-packages:

```
$ virtualenv ~/virtualenv/monotool
$ source ~/virtualenv/monotool/bin/activate
```

Install monotool!

```
$ python setup.py install
```

You hould now haev monotool installed in your virtualenv:

```
$ which monotool
/Users/jness/virtualenv/monotool/bin/monotool
```

You can deactivate the virtualenv by either exiting the console
session, or running the following:

```
$ deactivate
```

To re-enable the virtualenv run:

```
$ source ~/virtualenv/monotool/bin/activate
```

## Quick Install (system wide)

Install from Git

```
$ sudo pip install git+https://github.com/bigrentz/monotool.git
```

Add Configuration to /etc/monotool.conf

Example configuration can be found below:
  
  https://github.com/bigrentz/monotool/blob/master/monotool.conf.example

## Project Directory Structure

monotool expects the following directory structure per projects:

```
.
├── README.md
└── src
    ├── BigRentz.Project.ProjectService
    │   ├── BigRentz.Project.ProjectService.csproj
    │   ├── bin
    │   │   └── Debug
    │   ├── envrc.sh
    │   └── packages.config
    └── BigRentz.Project.sln
```

The repos root solution file should build the needed projects:

```
$ monotool -s BigRentz.Project.sln lsp
BigRentz.Project.ProjectService
```

If the project is a service and requires a upstart and startup file,
the project directory (directory containing the .csproj) should
include a **envrc.sh** with runtime environment. If found we will
use the mustache templates to generate start.sh and upstart.conf
in the csproj directory:

   https://github.com/bigrentz/monotool/tree/master/monotool/templates

## envrc.sh

The envrc.sh file is merely a *nix source-able text file:

```
export BR_PR_DB_USER_ID=project
export BR_PR_DB_USER_PW=password
export BR_PR_DB_HOST=localhost
export BR_PR_DB_NAME=project
export BR_PR_LISTEN_PORT=1337
```

If present we will create a few scripts based of our templates:

   https://github.com/bigrentz/monotool/tree/master/monotool/templates

## Usage

### Getting help

```
$ monotool --help
usage: monotool [-h] [--version] [-s solution_file]  ...

optional arguments:
  -h, --help        show this help message and exit
  --version         show program's version number and exit
  -s solution_file  A solution file to work with.

Commands:

    lsp             Lists all project files found in the solution.
    lsa             Lists all artifacts files found in the project.
    copy            Copies all artifacts files found in the project to
                    directory.
    clean           Runs xbuild clean, this will delete all artifacts.
    restore         Run nuget restore on a solution file.
    xbuild          xbuild on a solution file.
    build           runs clean, nuget_restore, and xbuild.
    archive         Archives all the artifacts file found in the project to
                    directory.
```

### Getting version

```
$ monotool --version
0.0.30
```

### List all project definded in the Solution file

```
$ monotool lsp
BigRentz.Project
```

### Specify a solution file

```
$ monotool -s BigRentz.Project.sln lsp
BigRentz.Project
```

### Cleaning

```
$ monotool clean
2015-04-13 08:54:29,743 - monotool.utils - INFO - Running command /usr/local/bin/xbuild BigRentz.Project.sln /t:clean
2015-04-13 08:54:30,216 - monotool.utils - INFO - Command successful
```

### Run Nuget Restore

```
$ monotool restore
2015-04-13 08:54:50,332 - monotool.monotool - INFO - This can take some time...
2015-04-13 08:54:50,332 - monotool.utils - INFO - Running command /usr/local/bin/mono /usr/local/bin/nuget.exe restore BigRentz.Project.sln
2015-04-13 08:54:50,678 - monotool.utils - INFO - Command successful
```

### Running xbuild

```
$ monotool xbuild
2015-04-13 08:55:07,862 - monotool.monotool - INFO - This can take some time...
2015-04-13 08:55:07,862 - monotool.utils - INFO - Running command /usr/local/bin/xbuild BigRentz.Project.sln
2015-04-13 08:55:09,791 - monotool.utils - INFO - Command successful
```

### Running the complete build process and output a tarball.

```
$ monotool build
2015-04-13 08:55:30,268 - monotool.utils - INFO - Running command /usr/local/bin/xbuild BigRentz.Project.sln /t:clean
2015-04-13 08:55:30,591 - monotool.utils - INFO - Command successful
2015-04-13 08:55:30,592 - monotool.monotool - INFO - This can take some time...
2015-04-13 08:55:30,592 - monotool.utils - INFO - Running command /usr/local/bin/mono /usr/local/bin/nuget.exe restore BigRentz.Project.sln
2015-04-13 08:55:30,857 - monotool.utils - INFO - Command successful
2015-04-13 08:55:30,858 - monotool.monotool - INFO - This can take some time...
2015-04-13 08:55:30,858 - monotool.utils - INFO - Running command /usr/local/bin/xbuild BigRentz.Project.sln
2015-04-13 08:55:32,435 - monotool.utils - INFO - Command successful
```

### Listing build artifacts.

```
$ monotool lsa
BigRentz.Project
  BigRentz.Project/bin/Debug/BigRentz.Project.dll
```

### Copy all artifacts to destination directory

```
$ monotool copy bins/

$ ls -l bins/
total 0
drwxr-xr-x  21 jness  staff   714 Apr 13 08:56 BigRentz.Project
```

### Create tarball of all artifacts 

The output tarball will be named using the following structure:

  {{ monotool.__get_app_name }}.{{ git_commit_hash }}.tar.gz

```
$ monotool archive .
2015-04-13 08:57:33,195 - monotool.utils - INFO - Running command git rev-parse HEAD
2015-04-13 08:57:33,201 - monotool.utils - INFO - Command successful
2015-04-13 08:57:33,201 - monotool.monotool - INFO - Saving tarball ./Project.be96ee3fa91084360ae637226e3cc954e388b0f4.tar.gz
```

### Debugging

monotool will log INFO level to standard out and DEBUG level to /tmp/monotool.log:

```
$ tail -n 1 /tmp/monotool.log
2015-04-13 08:57:33,201 - monotool.monotool - INFO - Saving tarball ./Project.be96ee3fa91084360ae637226e3cc954e388b0f4.tar.gz
```
