import argparse


def get_args(version):
    """
    Parse our input args and return the argparse object
    """
    
    # Setup a basic parser for our input arguments.
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", metavar="")
    
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('-s', dest='solution_file', metavar='solution_file', required=False,
            help='A solution file to work with.')

    # Our subparser commands
    lsp = subparsers.add_parser('lsp',
            help='Lists all project files found in the solution.')
    lsp.set_defaults(method='_lsp')


    lsa = subparsers.add_parser('lsa',
            help='Lists all artifacts files found in the project.')
    lsa.set_defaults(method='_lsa')

    copy = subparsers.add_parser('copy',
            help='Copies all artifacts files found in the project to directory.')
    copy.add_argument('dest', help='The destination directory.')
    copy.set_defaults(method='_copy')

    clean = subparsers.add_parser('clean',
            help='Runs xbuild clean, this will delete all artifacts.')
    clean.set_defaults(method='_clean')

    nuget_restore = subparsers.add_parser('restore',
            help='Run nuget restore on a solution file.')
    nuget_restore.set_defaults(method='_restore')

    xbuild = subparsers.add_parser('xbuild',
            help='xbuild on a solution file.')
    xbuild.set_defaults(method='_xbuild')

    build = subparsers.add_parser('build',
            help='runs clean, nuget_restore, and xbuild.')
    build.set_defaults(method='_build')

    archive = subparsers.add_parser('archive',
            help='Archives all the artifacts file found in the project to directory.')
    archive.set_defaults(method='_archive')

    # parse our parsers and get the args.
    args = parser.parse_args()
    return args
