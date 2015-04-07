#!/bin/env python

from pkg_resources import get_distribution
from glob import glob
from subprocess import Popen, PIPE
from re import search
from datetime import datetime

import pystache
import shutil
import sys
import os

from arguments import get_args
from config import get_config
from logger import get_logger

APP_NAME = 'monotool'

class MonoTool(object):

    def __init__(self, solution_file, debug=False):
        """
        repo_dir: Directory of the cloned repo.
        """

        if debug:
            self.log_level = 'DEBUG'
        else:
            self.log_level = 'INFO'

        self.logger = get_logger(self.log_level)
        self.config = get_config(APP_NAME)

        if os.path.exists(solution_file):
            self.solution_file = solution_file.rstrip()
        else:
            raise Exception('Solution file %s not found' % solution_file)

        # define a couple of our configs
        self.output_path = self.config['output_path']
        self.xbuild_path = self.config['xbuild_path']
        self.mono_path = self.config['mono_path']
        self.nuget_path = self.config['nuget_path']

    def __run(self, command, cwd='.'):
        """
        Runs a command and returns a tuple of stdout and stderr
        """
        self.logger.info('Running command %s' % command)
        process = Popen(command, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        self.logger.debug(stdout)

        if process.returncode:
            if stderr:
                self.logger.error(stderr)
            raise Exception('Command returned with non zero return')
        self.logger.info('Command successful')

    def __timestamp(self):
        """
        Returns a human readable timestamp.
        """
        return datetime.now().strftime("%A, %d. %B %Y %I:%M%p")

    def __write(self, filename, data):
        """
        Write to a file.
        """
        self.logger.debug('Writing data to file %s' % filename)
        f = open(filename, 'w')
        f.write(data)
        f.close()

    def __read(self, filename):
        """
        Read from a file.
        """
        self.logger.debug('Reading from file %s' % filename)
        f = open(filename, 'r')
        data = f.read()
        f.close()
        return data

    def __copy(self, path, dest):
        """
        Copy a file or directory to destination.
        """
        try:
            shutil.copyfile(path, dest)
        except IOError:
            shutil.copytree(path, dest)

    def __get_projects(self):
        """
        Returns all directories containing a csproj file.
        """
        projects = []
        csprojs = glob('*/*.csproj')
        for csproj in csprojs:
            projects.append(csproj.split('/')[0])
        return projects

    def __get_artifacts(self, project_name):
        """
        Returns a list of file artifacts
        """
        output_path = '%s/%s' % (project_name, self.output_path)
        self.logger.debug('Looking for artifacts in %s/%s' % 
            (project_name, self.output_path))
        return glob('%s/*' % output_path)

    def __generate_templates(self, project_name, dir_name):
        """
        Generate upstart and startup for project
        """
        upstart = self.__generate_project_template(project_name,'upstart_template')
        startup = self.__generate_project_template(project_name, 'startup_template')
        self.__write('%s/upstart.conf' % dir_name, upstart)
        self.__write('%s/startup.sh' % dir_name, startup)

    def list_projects(self, **kwargs):
        """
        Returns a list of all projects
        """
        return '\n'.join([ p for p in self.__get_projects() ])

    def list_project_version(self, project_name, **kwargs):
        """
        Get the project's AssemblyVersion.
        """
        filename = '%s/Properties/AssemblyInfo.cs' % project_name
        if not os.path.exists(filename):
            raise Exception('Unable to find %s' % filename)

        data = self.__read(filename)
        for line in data.split('\n'):
            s = search('^\[assembly\: AssemblyVersion\("(.*)"\)\]', line)
            if s:
                return s.group(1)

    def __generate_project_template(self, project_name, template):
        """
        Generates template for project.
        """
        pwd = os.path.dirname(__file__)
        filename = '%s/templates/%s.stache' % (pwd, template)

        data = dict(
            project_name=project_name,
            version=get_version(),
            timestamp=self.__timestamp()
        )
        template = self.__read(filename)
        rendered = pystache.render(template, data)
        return rendered

    def list_artifacts(self, **kwargs):
        """
        Returns a list of all solutions in project_path
        """
        for project_name in self.__get_projects():
            print project_name
            for artifacts in self.__get_artifacts(project_name):
                print '  %s' % artifacts

    def list_specs(self, **kwargs):
        """
        List all NuGet spec files found in projects.
        """
        _specs = self.__get_specs()
        for project, specs in _specs:
            print project
            for spec in specs:
                print '  %s' % spec.split('/')[-1]

    def copy(self, dest, **kwargs):
        """
        Copies the artifacts from a solutions file to destination directory.

        If version=True we will concatenate version to project
        directory name.
        """
        copied = 0
        dest = dest.rstrip('/')

        # create directory if not present
        if not os.path.exists(dest):
            os.makedirs(dest)

        for project_name in self.__get_projects():

            # Create the project directory if not present
            dir_name = '%s/%s' % (dest, project_name)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            artifacts = self.__get_artifacts(project_name)
            for artifact in artifacts:
                filename = artifact.split('/')[-1]
                self.logger.debug('Copying %s to %s/' % (filename, dir_name))

                # copyfile or copytree depending on if file or directory.
                self.__copy(artifact, '%s/%s' % (dir_name, filename))

                copied += 1

            # copy in envrc.sh if found and create upstart
            envrc = '%s/envrc.sh' % project_name
            if os.path.exists(envrc):
                self.logger.debug('Found envrc.sh for project %s' % project_name)
                shutil.copyfile(envrc, '%s/%s' % (dir_name, 'envrc.sh'))
                self.__generate_templates(project_name, dir_name)

        print 'Copied %d files to %s' % (copied, dest)

    def clean(self, **kwargs):
        """
        Runs xbuild /t:clean to clear all artifacts.
        """
        cmd = '%s %s /t:clean' % (self.xbuild_path, self.solution_file)
        self.__run(cmd)

    def nuget_restore(self, **kwargs):
        """
        Run Nuget.exe if we have a packages.json
        """
        cmd = '%s %s restore %s' % (
                self.mono_path, self.nuget_path, self.solution_file
        )
        self.logger.info('This can take some time...')
        self.__run(cmd)

    def xbuild(self, **kwargs):
        """
        Run xbuild on the solution
        """
        cmd = '%s %s' % (self.xbuild_path, self.solution_file)
        self.logger.info('This can take some time...')
        self.__run(cmd)

    def build(self, **kwargs):
        """
        Runs clean, nuget_restore, and xbuild all in one.
        """
        self.clean()
        self.nuget_restore()
        self.xbuild()

def default_solution():
    """
    Try to determine our default solution file
    """
    solutions = glob('*.sln')
    if len(solutions) == 1:
        return solutions[0]
    elif len(solutions) < 1:
        raise Exception('More than one solution file found, please use -s flag.')
    else:
        raise Exception('No solution files found in path.')

def get_version():
    """
    Return application version.
    """
    return get_distribution(APP_NAME).version

def main():
    """
    Main entry point for the program.
    """
    args = get_args(get_version())

    if not args.solution_file:
        args.solution_file = default_solution()

    # create a new MonoTool object using our project path.
    mt = MonoTool(args.solution_file, debug=args.debug)

    method = getattr(mt, args.method)
    res = method(**args.__dict__)
    if res:
        print res


if __name__ == '__main__':
    main()
