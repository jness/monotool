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

    clean = subparsers.add_parser('clean',
            help='Runs xbuild clean, this will delete all artifacts.')
    clean.set_defaults(method='_clean')

    restore = subparsers.add_parser('restore',
            help='Run nuget restore on a solution file.')
    restore.set_defaults(method='_restore')

    xbuild = subparsers.add_parser('xbuild',
            help='Xbuilds on a solution file.')
    xbuild.set_defaults(method='_xbuild')

    build = subparsers.add_parser('build',
            help='Runs end to end build process.')
    build.set_defaults(method='_build')

    archive = subparsers.add_parser('archive',
            help='Archives artifact files found in all projects to tarball.')
    archive.add_argument('dest', help='The destination directory of the tarball.')
    archive.set_defaults(method='_archive')

    copy = subparsers.add_parser('copy',
            help='Copies artifact files found in all projects to directory.')
    copy.add_argument('dest', help='The destination directory.')
    copy.set_defaults(method='_copy')

    # parse our parsers and get the args.
    args = parser.parse_args()
    return args
