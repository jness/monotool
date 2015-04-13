#!/bin/env python

from pkg_resources import get_distribution
from glob import glob
from re import search

import pystache
import tempfile
import sys
import os

from utils import run, copy, write, read, delete, mktar, timestamp
from app import app_name
from arguments import get_args
from config import get_config
from logger import get_logger


class MonoTool(object):

    def __init__(self, solution_file):
        """
        repo_dir: Directory of the cloned repo.
        """
        if os.path.exists(solution_file):
            self.solution_file = solution_file.rstrip()
        else:
            raise Exception('Solution file %s not found' % solution_file)

        self.config = get_config()
        self.logger = get_logger(__name__)

        # define a couple of our configs
        self.output_path = self.config['output_path']
        self.xbuild_path = self.config['xbuild_path']
        self.mono_path = self.config['mono_path']
        self.nuget_path = self.config['nuget_path']

    def __get_projects(self):
        """
        Gets the project defined by reading a solution file.
        """
        projects = []
        self.logger.debug('Looking for project definitions in %s' % self.solution_file)
        solution_blob = open(self.solution_file, 'r').read()
        for line in solution_blob.split('\n'):
            if 'Project(' in line and '.csproj' in line:
                _, _, project, csproj, _ = line.split()
                projects.append(project.split('"')[1])  # Ghetto hack to remove string inception.
        return projects

    def __get_artifacts(self, project_name):
        """
        Returns a list of file artifacts
        """
        output_path = '%s/%s' % (project_name, self.output_path)
        self.logger.debug('Looking for artifacts in %s/%s' % 
            (project_name, self.output_path))
        return glob('%s/*' % output_path)

    def __write_templates(self, project_name, dir_name):
        """
        Generate upstart and startup for project
        """
        upstart = self.__generate_project_template(project_name,'upstart_template')
        startup = self.__generate_project_template(project_name, 'startup_template')
        write('%s/upstart.conf' % dir_name, upstart)
        write('%s/startup.sh' % dir_name, startup)

    def __generate_project_template(self, project_name, template):
        """
        Generates template for project.
        """
        pwd = os.path.dirname(__file__)
        filename = '%s/templates/%s.stache' % (pwd, template)

        data = dict(
            project_name=project_name,
            version=get_version(),
            timestamp=timestamp()
        )
        template = read(filename)
        rendered = pystache.render(template, data)
        return rendered

    def _lsp(self, **kwargs):
        """
        Returns a list of all projects
        """
        return '\n'.join([ p for p in self.__get_projects() ])

    def _lsa(self, **kwargs):
        """
        Returns a list of all solutions in project_path
        """
        for project_name in self.__get_projects():
            artifacts = self.__get_artifacts(project_name)
            if artifacts:
                print project_name
                for artifacts in self.__get_artifacts(project_name):
                    print '  %s' % artifacts

    def _copy(self, dest, **kwargs):
        """
        Copies the artifacts from a solutions file to destination directory.

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
                copy(artifact, '%s/%s' % (dir_name, filename))

                copied += 1

            # copy in envrc.sh if found and create upstart
            envrc = '%s/envrc.sh' % project_name
            if os.path.exists(envrc):
                self.logger.debug('Found envrc.sh for project %s' % project_name)
                copy(envrc, '%s/%s' % (dir_name, 'envrc.sh'))
                self.__write_templates(project_name, dir_name)

    def _clean(self, **kwargs):
        """
        Runs xbuild /t:clean to clear all artifacts.
        """
        cmd = '%s %s /t:clean' % (self.xbuild_path, self.solution_file)
        run(cmd)

    def _restore(self, **kwargs):
        """
        Run Nuget.exe if we have a packages.json
        """
        cmd = '%s %s restore %s' % (
                self.mono_path, self.nuget_path, self.solution_file
        )
        self.logger.info('This can take some time...')
        run(cmd)

    def _xbuild(self, **kwargs):
        """
        Run xbuild on the solution
        """
        cmd = '%s %s' % (self.xbuild_path, self.solution_file)
        self.logger.info('This can take some time...')
        run(cmd)

    def _build(self, **kwargs):
        """
        Runs clean, nuget_restore, and xbuild all in one.
        """
        self._clean()
        self._restore()
        self._xbuild()

    def _archive(self, **kwargs):
        """
        Creates a tarball from output_paths by using
        the _copy function.
        """
        now = timestamp(verbose=False)
        app = app_name()
        dirpath = tempfile.mkdtemp()

        # use monotool._copy to get all our artifacts
        # in to the temp directory (dirpath).
        self._copy(dirpath)

        # Make a tarball of temp directory excluding top level
        # temp directory path name.
        self.logger.info('Saving tarball %s.%s.tar.gz' % (app, now))
        mktar(dirpath, '%s.%s.tar.gz' % (app, now))

        # clean up by deleting temp directory.
        delete(dirpath)

def default_solution():
    """
    Try to determine our default solution file
    """
    solutions = glob('*.sln')
    if len(solutions) == 1:
        return solutions[0]
    elif len(solutions) > 1:
        raise Exception('More than one solution file found, please use -s flag.')
    else:
        raise Exception('No solution files found in path.')

def get_version():
    """
    Return application version.
    """
    return get_distribution(app_name()).version

def main():
    """
    Main entry point for the program.
    """
    args = get_args(get_version())

    if not args.solution_file:
        args.solution_file = default_solution()

    # create a new MonoTool object using our project path.
    mt = MonoTool(args.solution_file)

    method = getattr(mt, args.method)
    res = method(**args.__dict__)
    if res:
        print res


if __name__ == '__main__':
    main()
