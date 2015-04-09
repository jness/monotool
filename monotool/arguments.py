import argparse

def get_args(version):
    """
    Parse our input args and return the argparse object
    """
    
    # Setup a basic parser for our input arguments.
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", metavar="")
    
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('--debug', action='store_true', dest='debug', default=False)
    parser.add_argument('-s', dest='solution_file', metavar='solution_file', required=False,
            help='A solution file to work with.')

    # Our subparser commands
    list_projects = subparsers.add_parser('lsp',
            help='Lists all project files found in the solution.')
    list_projects.set_defaults(method='list_projects')


    list_artifacts = subparsers.add_parser('lsa',
            help='Lists all artifacts files found in the project.')
    list_artifacts.set_defaults(method='list_artifacts')

    copy_artifacts = subparsers.add_parser('copy',
            help='Copies all artifacts files found in the project to directory.')
    copy_artifacts.add_argument('dest', help='The destination directory.')
    copy_artifacts.set_defaults(method='copy')

    clean = subparsers.add_parser('clean',
            help='Runs xbuild clean, this will delete all artifacts.')
    clean.set_defaults(method='clean')

    nuget_restore = subparsers.add_parser('restore',
            help='Run nuget restore on a solution file.')
    nuget_restore.set_defaults(method='restore')

    xbuild = subparsers.add_parser('xbuild',
            help='xbuild on a solution file.')
    xbuild.set_defaults(method='xbuild')

    build = subparsers.add_parser('build',
            help='runs clean, nuget_restore, and xbuild.')
    build.set_defaults(method='build')

    # parse our parsers and get the args.
    args = parser.parse_args()
    return args
