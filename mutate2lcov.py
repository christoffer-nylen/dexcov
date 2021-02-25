#!/usr/bin/env python3

"""
Changes the dextool mutate report to look and feel like lcov.
"""

import optparse
import os
import os.path
import sys
import subprocess

def run_cmd(bashCmd):
    process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if len(output) != 0:
        print(output.rstrip('\n'))

def main(argv):
    parser = optparse.OptionParser('mutate2lcov.py: FILE [.. FILE]')
    parser.set_description(__doc__.strip())
    parser.add_option('-i', '--in-place',
                      action="store_true",
                      dest="editInPlace",
                      help="Edit files in place",
                      default=False)
    parser.add_option('-r', '--restore-javascript',
                      action="store_true",
                      dest="restoreJavascript",
                      help="Restore java script interactions (Default: False)",
                      default=False)
    parser.add_option('-c', '--use-lcov-color',
                      action="store_true",
                      dest="useLcovColor",
                      help="Change the color theme to look like lcov (Default: False)",
                      default=False)
    parser.add_option('-v', '--verbose',
                      action="store_true",
                      dest="useVerbose",
                      help="Print debug information",
                      default=False)
                      
    (opts, args) = parser.parse_args(argv)
    if not args:
        parser.print_help()
        return 1

    for arg in args:
        if not os.path.exists(arg):
            print('Error: path %s does not exist' % arg)
            return 1

    for arg in args:
        content = list()
        didPatch = False
        with open(arg,'r') as fin:
            lines = fin.readlines()
            for line in lines:
                line = line.rstrip()
                if line.startswith('<div id="info_wrapper"'):
                    didPatch = True
                    if opts.restoreJavascript:
                        content.append('<div id="info_wrapper">')
                    else:
                        content.append('<div id="info_wrapper" hidden>')
                elif line.startswith('function ui_set_mut'):
                    didPatch = True
                    if opts.restoreJavascript:
                        content.append('function ui_set_mut(id) {')
                    else:
                        content.append('function ui_set_mut_off(id) {')
                elif opts.useLcovColor and line.startswith(".keyword {color:"):
                    content.append(".keyword {color: black;}")
                elif opts.useLcovColor and line.startswith(".literal {color:"):
                    content.append(".literal {color: black;}")
                elif opts.useLcovColor and line.startswith(".comment {color:"):
                    content.append(".comment {color: black;}")
                elif opts.useLcovColor and line.startswith(".line_nr {color:"):
                    content.append(".line_nr {color: black;}")
                elif opts.useLcovColor and line.startswith(".status_alive {background-color:"):
                    content.append(".status_alive {background-color: #FF6230;}")
                elif opts.useLcovColor and line.startswith(".status_noCoverage {background-color:"):
                    content.append(".status_noCoverage {background-color: #FF6230;}")
                elif opts.useLcovColor and line.startswith(".status_killed {background-color:"):
                    content.append(".status_killed {background-color: #CAD7FE;}")
                elif opts.useLcovColor and line.startswith(".status_killedByCompiler {background-color:"):
                    content.append(".status_killedByCompiler {background-color: white;}")
                elif opts.useLcovColor and line.startswith(".status_timeout {background-color:"):
                    content.append(".status_timeout {background-color: #CAD7FE;}")
                else:
                    content.append(line)
        if not didPatch:
            print("skipping: %s" % arg)
            continue
        if not opts.editInPlace:
            for line in content:
                print(line)
        else:
            print("converting: %s" % arg)
            with open(arg,'w') as fout:
                for line in content:
                    fout.write(line+'\n')
    
if __name__ == '__main__':
    main(sys.argv[1:])
