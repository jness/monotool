# Monotool

A tool for assisting with the Mono build process.

## Installation

```
# If your are on OSX you can install mono and 
# xbuild from brew:
brew install mono

# Install nuget the package manager for the
# Microsoft development platform
sudo wget http://nuget.org/nuget.exe -O /opt/local/bin/nuget.exe

# Install Python virtualenv and pip 
# http://docs.python-guide.org/en/latest/dev/virtualenvs/
sudo easy_install pip
sudo pip install virtualenv

# Get the latest monotool source from Github:
git clone git@github.com:bigrentz/monotool.git
cd monotool/

# Copy the example config to your user profile:
cp monotool.conf.example ~/.monotool.conf

# Create a activate Python virtualenv for site-packages:
virtualenv ~/virtualenv/monotool
source ~/virtualenv/monotool/bin/activate

# Install monotool!
python setup.py install
```

## Quick Install (system wide)

```
# Install from Git
sudo pip install git+https://github.com/bigrentz/monotool.git

# Add Configuration to /etc/monotool.conf
# Example configuration can be found below:
#  * https://github.com/bigrentz/monotool/blob/master/monotool.conf.example
```

## Directory Structure

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
$ monotool -s BigRentz.Project.sln listProjects
BigRentz.Project.PorjectService
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

## Usage

### Activating the monotool virtualenv

If you have not already activated your virtualenv do it now

```
$ source ~/virtualenv/monotool/bin/activate
```

You can deactivate by either exiting the command session, 
or running the following:

```
$ deactivate
```

### Getting help

```
$ monotool --help
usage: monotool [-h] [--version] [--debug] -s solution_file  ...

optional arguments:
  -h, --help          show this help message and exit
  --version           show program's version number and exit
  --debug
  -s solution_file    A solution file to work with.

Commands:

    listProjects      Lists all project files found in the solution.
    listProjectVersion
                      Lists the projects Assembly Version.
    listArtifacts     Lists all artifacts files found in the project.
    listSpecs         Lists all nuget spec files found in the project.
    copyArtifacts     Copies all artifacts files found in the project to
                      directory.
    clean             Runs xbuild clean, this will delete all artifacts.
    nugetRestore      Run nuget restore on a solution file.
    xbuild            xbuild on a solution file
```

### Getting version

```
$ monotool --version
0.0.5
```

### List all project definded in the Solution file

```
$ monotool -s BigRentz.Project.sln listProjects
BigRentz.Project
```

### Get a project Assembly Version

```
$ monotool -s BigRentz.Project.sln listProjectVersion BigRentz.Project
1.0.0.0
```

### Debug or verbose logging with the --debug flag

```
$ monotool --debug -s BigRentz.Project.sln listProjects
2015-03-19 07:46:51,770 - DEBUG - Looking for project definitions in BigRentz.Project.sln
BigRentz.Project
```

### Run Nuget Restore on a solution file.

```
$ monotool -s BigRentz.Project.sln nugetRestore
2015-03-19 07:48:18,610 - INFO - Running: /usr/bin/mono /Users/jeffreyness/Downloads/NuGet.exe restore BigRentz.Project.sln
2015-03-19 07:48:18,610 - INFO - This can take some time...
2015-03-19 07:48:26,621 - INFO - Command Successful
```

### Running xbuild on a solution file.

```
$ monotool -s BigRentz.Project.sln xbuild
2015-03-19 07:48:44,936 - INFO - Running: /usr/bin/xbuild BigRentz.Project.sln
2015-03-19 07:48:44,937 - INFO - This can take some time...
2015-03-19 07:48:46,625 - INFO - Command Successful
```

### Listing build artifacts.

```
$ monotool -s BigRentz.Project.sln listArtifacts
BigRentz.Project
  BigRentz.Project/bin/Debug/BigRentz.Project.dll
```

### Copy artifacts to a versioned directory

```
$ monotool -s BigRentz.Project.sln copyArtifacts tmp/
2015-03-19 07:49:40,095 - INFO - Copying BigRentz.Project.dll to tmp/BigRentz.Project.0.0.0.1/
```

### Cleaning up

```
$ monotool -s BigRentz.Project.sln clean
2015-03-20 10:53:02,272 - INFO - Running: /usr/local/bin/xbuild BigRentz.Project.sln /t:clean
2015-03-20 10:53:02,571 - INFO - Command Successful

