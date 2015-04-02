#!/bin/env python

from glob import glob
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE
from re import search

import pkg_resources
import argparse
import logging
import shutil
import sys
import os

class MonoTool(object):

    def __init__(self, solution_file, debug=False):
        """
        repo_dir: Directory of the cloned repo.
        """
        if debug:
            self.log_level = 'DEBUG'
        else:
            self.log_level = 'INFO'
        self.logger = self.__logger()
        self.config = self.__config()

        if os.path.exists(solution_file):
            self.solution_file = solution_file.rstrip()
        else:
            raise Exception('Solution file %s not found' % solution_file)
        self.solution_path = '/'.join(os.path.abspath(solution_file).split('/')[:-1])

        # define a couple of our configs
        self.output_path = self.config['output_path']
        self.xbuild_path = self.config['xbuild_path']
        self.mono_path = self.config['mono_path']
        self.nuget_path = self.config['nuget_path']

    def __logger(self):
        _format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=_format)
        logger = logging.getLogger('monotool')  # shouldn't be hard coded.
        logger.setLevel(getattr(logging, self.log_level))
        return logger


    def __config(self):
        """
        Uses configuration from /etc/monotool.conf or
        ~/.monotool.conf, the latter trumps the former.
        """
        system_path = os.path.expanduser('/etc/monotool.conf')
        home_path = os.path.expanduser('~/.monotool.conf')
        if os.path.exists(home_path):
            config_file = home_path
        elif os.path.exists(system_path):
            config_file = system_path
        else:
            raise Exception('Unable to find monotool config in %s or %s' %
                    (system_path, home_path))

        config = ConfigParser()
        config.readfp(open(config_file))
        return dict(config.items('default'))  # shouldn't be hard coded.

    def __run(self, command, cwd='.'):
        """
        Runs a command and returns a tuple of stdout and stderr
        """
        process = Popen(command, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stdout, stderr, process.returncode

    def __log_run(self, results):
        """
        Logs the results of our __run using a universal method
        """
        print 'I made it'
        stdout, stderr, returncode = results

        if returncode:
            if stdout:
                self.logger.error(stdout)
            if stderr:
                self.logger.error(stderr)
            raise Exception('Command returned with %s return code' % returncode)
        else:
            if stdout:
                self.logger.debug(stdout)
            if stderr:
                self.logger.warn(stderr)
            self.logger.info('Command Successful')

    def __get_projects(self):
        """
        Gets the project defined by reading a solution file.
        """
        projects = []
        self.logger.debug('Looking for project definitions in %s' % self.solution_file)
        solution_blob = open(self.solution_file, 'r').read()
        for line in solution_blob.split('\n'):
            if 'Project(' in line:
                _, _, project, csproj, _ = line.split()

                project = project.split('"')[1]  # Ghetto hack to remove string inception.
                csproj = csproj.split('"')[1]  # Ghetto hack to remove string inception.
                csproj = csproj.replace('\\', '/')  # Windows path to Linux..

                # Need to get path from csproj
                project_path = csproj.split('/')[:-1][0]
                output_path = '%s/%s' % (project_path, self.output_path)
                projects.append(dict(project=project, csproj=csproj, output_path=output_path,
                    project_path=project_path))
        return projects

    def __get_project(self, project_name):
        """
        Get a project from project_name
        """
        for project in self.__get_projects():
            if project.get('project') == project_name:
                return project

    def __get_artifacts(self):
        """
        Returns a list of file artifacts
        """
        artifacts = []
        projects = self.__get_projects()
        for project in projects:
            output_path = '%s/%s' % (project['project_path'], self.output_path)
            self.logger.debug('Looking for artifacts in %s' % output_path)
            data = glob('%s/*' % output_path)
            if data:
                artifacts.append([ project['project'], data ])
        return artifacts

    def __get_specs(self):
        """
        Returns a list of nuget spec files
        """
        specs = []
        for _project in self.__get_projects():
            project = _project['project']
            project_path = _project['project_path']
            self.logger.debug('Looking for nuspec in %s' % project_path)
            data = glob('%s/*.nuspec' % project_path)
            if data:
                specs.append([project, data])
        return specs

    def list_projects(self, **kwargs):
        """
        Returns a list of all projects
        """
        return '\n'.join([ p['project'] for p in self.__get_projects() ])

    def list_project_version(self, project_name, **kwargs):
        """
        Get the project's AssemblyVersion.
        """
        project = self.__get_project(project_name)
        if not project:
            raise Exception('Project not found in Solution file.')
        filename = '%s/Properties/AssemblyInfo.cs'
        f = open(filename % project['project_path'], 'r').read()
        for line in f.split('\n'):
            s = search('^\[assembly\: AssemblyVersion\("(.*)"\)\]', line)
            if s:
                return s.group(1)

    def list_artifacts(self, **kwargs):
        """
        Returns a list of all solutions in project_path
        """
        _artifacts = self.__get_artifacts()
        for project, artifacts in _artifacts:
            print project
            for artifact in artifacts:
                print '  %s' % artifact.split('/')[-1]

    def list_specs(self, **kwargs):
        """
        List all NuGet spec files found in projects.
        """
        _specs = self.__get_specs()
        for project, specs in _specs:
            print project
            for spec in specs:
                print '  %s' % spec.split('/')[-1]

    def copy_artifacts(self, dest, **kwargs):
        """
        Copies the artifacts from a solutions file to destination directory.
        """
        dest = dest.rstrip('/')
        if not os.path.exists(dest):
            raise Exception('Does not appear %s exists' % dest)
        if not os.path.isdir(dest):
            raise Exception('It does not appear %s is a directory' % dest)

        _artifacts = self.__get_artifacts()
        for project_name, artifacts in _artifacts:
            project_version = self.list_project_version(project_name)
            dir_name = '%s/%s.%s' % (dest, project_name, project_version)

            # Create the project directory if it does not exist.
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            for artifact in artifacts:
                filename = artifact.split('/')[-1]
                self.logger.info('Copying %s to %s/' % (filename, dir_name))
                shutil.copyfile(artifact, '%s/%s' % (dir_name, filename))

    def clean(self, **kwargs):
        """
        Runs xbuild /t:clean to clear all artifacts.
        """
        cmd = '%s %s /t:clean' % (self.xbuild_path, self.solution_file)
        self.logger.info('Running: %s' % cmd)
        self.__log_run(self.__run(cmd, cwd=self.solution_path))

    def nuget_restore(self, **kwargs):
        """
        Run Nuget.exe if we have a packages.json
        """
        cmd = '%s %s restore %s' % (
                self.mono_path, self.nuget_path, self.solution_file
        )
        self.logger.info('Running: %s' % cmd)
        self.logger.info('This can take some time...')
        self.__log_run(self.__run(cmd, cwd=self.solution_path))

    def xbuild(self, **kwargs):
        """
        Run xbuild on the solution
        """
        cmd = '%s %s' % (self.xbuild_path, self.solution_file)
        self.logger.info('Running: %s' % cmd)
        self.logger.info('This can take some time...')
        self.__log_run(self.__run(cmd, cwd=self.solution_path))

def get_version():
    """
    Return application version.
    """
    return pkg_resources.require("monotool")[0].version

def get_args():
    """
    Parse our input args and return the argparse object
    """
    
    # Setup a basic parser for our input arguments.
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", metavar="")
    
    parser.add_argument('--version', action='version', version=get_version())
    parser.add_argument('--debug', action='store_true', dest='debug', default=False)
    parser.add_argument('-s', dest='solution_file', metavar='solution_file', required=True,
            help='A solution file to work with.')

    # Our subparser commands
    list_projects = subparsers.add_parser('listProjects',
            help='Lists all project files found in the solution.')
    list_projects.set_defaults(method='list_projects')

    list_project_version = subparsers.add_parser('listProjectVersion',
            help='Lists the projects Assembly Version.')
    list_project_version.add_argument('project_name', help='A project in the solution file.')
    list_project_version.set_defaults(method='list_project_version')

    list_artifacts = subparsers.add_parser('listArtifacts',
            help='Lists all artifacts files found in the project.')
    list_artifacts.set_defaults(method='list_artifacts')

    list_specs = subparsers.add_parser('listSpecs',
            help='Lists all nuget spec files found in the project.')
    list_specs.set_defaults(method='list_specs')

    copy_artifacts = subparsers.add_parser('copyArtifacts',
            help='Copies all artifacts files found in the project to directory.')
    copy_artifacts.add_argument('dest', help='The destination directory.')
    copy_artifacts.set_defaults(method='copy_artifacts')

    clean = subparsers.add_parser('clean',
            help='Runs xbuild clean, this will delete all artifacts.')
    clean.set_defaults(method='clean')

    nuget_restore = subparsers.add_parser('nugetRestore',
            help='Run nuget restore on a solution file.')
    nuget_restore.set_defaults(method='nuget_restore')

    xbuild = subparsers.add_parser('xbuild',
            help='xbuild on a solution file.')
    xbuild.set_defaults(method='xbuild')

    # parse our parsers and get the args.
    args = parser.parse_args()
    return args

def main():
    """
    Main entry point for the program.
    """
    args = get_args()

    # create a new MonoTool object using our project path.
    mt = MonoTool(args.solution_file, debug=args.debug)

    method = getattr(mt, args.method)
    res = method(**args.__dict__)
    if res:
        print res


if __name__ == '__main__':
    main()

