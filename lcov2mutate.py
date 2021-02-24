#!/usr/bin/env python3

"""
Converts a list of lcov html files to a format that can be compared with
dextool mutate
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

new_header="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<html lang="en">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>LCOV - coverage.info - %s</title>
  <link rel="stylesheet" type="text/css" href="../gcov.css">
</head>

<body>

  <table cellpadding=0 cellspacing=0 border=0>
    <tr>
      <td>
"""

def main(argv):
    parser = optparse.OptionParser('lcov2mutate.py: FILE [.. FILE]')
    parser.set_description(__doc__.strip())
    parser.add_option('-i', '--in-place',
                      action="store_true",
                      dest="editInPlace",
                      help="Edit files in place",
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
        startCopy = False
        with open(arg,'r') as fin:
            lines = fin.readlines()
            for line in lines:
                line = line.rstrip()
                if startCopy:
                    content.append(line)
                if line.startswith("<pre class=\"sourceHeading\">"):
                    startCopy=True
        if not startCopy:
            print("skipping: %s" % arg)
            continue
        if not opts.editInPlace:
            print(new_header)
            for line in content:
                print(line)
        else:
            print("converting: %s" % arg)
            with open(arg,'w') as fout:
                fout.write(new_header % os.path.splitext(os.path.basename(arg))[0])
                for line in content:
                    fout.write(line+'\n')
    
if __name__ == '__main__':
    main(sys.argv[1:])
