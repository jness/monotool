#!/bin/env python

from glob import glob
from ConfigParser import ConfigParser
from subprocess import Popen, PIPE

import pkg_resources
import argparse
import logging
import sys
import os

class MonoTool(object):

    def __init__(self, repo_dir, debug=False):
        """
        repo_dir: Directory of the cloned repo.
        """
        if debug:
            self.log_level = 'DEBUG'
        else:
            self.log_level = 'INFO'
        self.logger = self.__logger()
        self.config = self.__config()
        self.repo_dir = repo_dir.rstrip('/')
        self.source_dir = os.path.abspath('%s/%s' % (self.repo_dir, self.config.get('sln_path', 'src')))

    def __logger(self):
        _format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=_format)
        logger = logging.getLogger('monotool')  # shouldn't be hard coded.
        logger.setLevel(getattr(logging, self.log_level))
        return logger


    def __config(self, cfg='~/.monotool.conf'):
        path = os.path.expanduser(cfg)
        if os.path.exists(path):
            config = ConfigParser()
            config.readfp(open(path))
            return dict(config.items('default'))  # shouldn't be hard coded.
        else:
            raise Exception('Unable to open %s' % cfg)

    def run(self, command, cwd='.'):
        "Runs a command and returns a tuple of stdout and stderr"
        process = Popen(command, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
        process.wait()
        stdout, stderr = process.communicate()
        if process.returncode:
            self.logger.error(stderr)
            raise Exception('Process returned with a non 0 return code.')
        return stdout, stderr

    def __get_project_path(self, solution_file):
        """
        Get the solution path for a given sln file.

        A fancy extension remover =)
        """
        return '.'.join(solution_file.split('.')[0:-1])

    def get_solutions(self):
        """
        Returns a list of solutions files in your
        slnPath path.
        """
        self.logger.debug('Looking for sln files in %s' % (
            self.source_dir)
        )
        solutions = glob('%s/*.sln' % (self.source_dir))
        return [ (s, self.__get_project_path(s)) for s in solutions ]

    def run_nuget(self, solution):
        """
        Run Nuget.exe if we have a packages.json
        """
        solution_file, project_path = solution
        if os.path.exists('%s/packages.config' % project_path):
            cmd = '%s %s restore %s' % (
                    self.config['mono_path'], self.config['nuget_path'], solution_file
            )
            self.logger.debug('Running: %s' % cmd)
            return self.run(cmd, cwd=self.source_dir)
        else:
            self.logger.debug('Project does not have a %s/packages.json, skipping..' % project_path)

    def run_xbuild(self, solution):
        """
        Run xbuild on the solution
        """
        solution_file, project_path = solution
        cmd = '%s %s' % (self.config['xbuild_path'], solution_file)
        self.logger.debug('Running: %s' % cmd)
        return self.run(cmd, cwd=self.source_dir)

    def get_artifacts(self, solution):
        """
        Returns a list of file artifacts
        """
        solution_file, project_path = solution
        artifact_path = self.config['artifact_path']
        artifacts = glob('%s/%s/*' % (project_path , artifact_path))
        return artifacts

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
    subparsers = parser.add_subparsers(title="Commands", metavar="--")
    
    parser.add_argument('--version', action='version', version=get_version())
    parser.add_argument('--debug', action='store_true', dest='debug', default=False) 
    parser.add_argument('-p', dest='project_path', required=True, metavar='project_path', 
            help='The relative path to your mono project.') 

    # Our subparser commands
    list_solutions = subparsers.add_parser('listSolutions', 
            help='Lists all solution files found in the project.')
    list_solutions.set_defaults(method='get_solutions')

    # parse our parsers and get the args.
    args = parser.parse_args()
    return args

def main():
    """
    Main entry point for the program.
    """
    args = get_args()

    # We should be sure the project path exists.
    if os.path.exists(args.project_path):
        project_path = os.path.expanduser(args.project_path)
    else:
        raise Exception('%s does not exists' % args.project_path)

    # create a new MonoTool object using our project path.
    project = MonoTool(project_path, debug=args.debug)

    method = getattr(project, args.method)
    print method()

      

if __name__ == '__main__':
    main()
