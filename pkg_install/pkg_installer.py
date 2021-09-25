#!/usr/bin/env python3

import sys
import subprocess
import pkg_resources

class PackageInstaller():
    '''
    Checks and Installs any missing required packages.
    '''
    def __init__(self):
        self.required = {'scrapy'}
        self.installed = {pkg.key for pkg in pkg_resources.working_set}

    def run(self):
        missing = self.required - self.installed

        if missing:
            # debug only
            print(missing)
            python = sys.executable
            subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
        else:
            # debug only
            print('Everything installed')
            pass
