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
import xml.etree.ElementTree as ET

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def remove_suffix(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

def find_up(path, file):
    def find_up_abs(path, file):
        """
        searches the directory tree upwards for FILE beginning at a given PATH start
        """
        if os.path.exists(os.path.join(path, file)):
            return path
        if path=="/":
            return None
        return find_up_abs(os.path.dirname(path), file)
    return find_up_abs(os.path.abspath(path), file)

def run_cmd_iter(cmd):
    print(cmd)
    proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        yield line.rstrip()

def run_cmd(cmd):
    print(cmd)
    proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    proc.wait()

def get_mutate_files(mutate_index):
    with open(mutate_index, 'r') as fin:
        for line in fin.readlines():
            if '<td><a href=\"files/' in line:
                html_file = line.split('"')[-2]
                source_file = remove_suffix(line.rstrip(),'</a></td>').split(">")[-1]
                yield source_file, html_file
    
compare_file_template="""
<!DOCTYPE html PUBLIC"-//W3C//DTD XHTML 1.0 Strict//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html lang="en-US">

  <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
  <meta content="utf-8" http-equiv="encoding">
  
  <head>
    <link rel="stylesheet" href="mystyle.css">
    
    <script src="jquery-3.5.1.js"></script> 
    <script> 
      $(function(){
          $("#left").load("%s");
          $("#right").load("%s");
      });
    </script> 
  </head>

  <body>

    <div id="left" class="container leftContainer"></div>
    <div id="right" class="container rightContainer"></div>
    
    <script type="text/javascript">
      var isSyncingLeftScroll = false;
      var isSyncingRightScroll = false;
      var leftDiv = document.getElementById('left');
      var rightDiv = document.getElementById('right');
      
      leftDiv.onscroll = function() {
	  if (!isSyncingLeftScroll) {
	      isSyncingRightScroll = true;
	      rightDiv.scrollTop = this.scrollTop;
	  }
	  isSyncingLeftScroll = false;
      }

      rightDiv.onscroll = function() {
	  if (!isSyncingRightScroll) {
	      isSyncingLeftScroll = true;
	      leftDiv.scrollTop = this.scrollTop;
	  }
	  isSyncingRightScroll = false;
      }
    </script>

  </body>

</html>
"""

def main(argv):
    parser = optparse.OptionParser('mutcov.py: PATH PATH')
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
    parser.add_option('-o', '--output-dir',
                      action="store",
                      type='string',
                      dest='outDir',
                      default="mutcov",
                      help="Directory to store the result (default: mutcov)")
    
    (opts, args) = parser.parse_args(argv)
    if not len(args) == 2:
        parser.print_help()
        return 1

    gcov_project = None
    mutate_project = None
    
    for arg in args:
        tmp = find_up(arg, 'gcov.css')
        if tmp:
            gcov_project = tmp
            print("found: lcov '%s'" % gcov_project)
        tmp = find_up(arg, 'long_term_view.html')
        if tmp:
            mutate_project = tmp
            print("found: mutate '%s'" % mutate_project)

    if not gcov_project:
        print("lcov html tree not found!")
        return 1

    if not mutate_project:
        print("dextool mutate html tree not found!")
        return 1

    gcov_files=dict()
    for html_file in run_cmd_iter('find %s -name *.gcov.html' % gcov_project):
        source_file = remove_prefix(html_file, gcov_project+'/')
        source_file = remove_suffix(source_file, '.gcov.html')
        html_file = remove_prefix(html_file, os.path.dirname(gcov_project)+'/')
        print("found: '%s' for '%s'" % (html_file, source_file))
        gcov_files[source_file]=html_file

    mutate_index=os.path.join(mutate_project,'index.html')
        
    if not os.path.exists(mutate_index):
        print("file: '%s' not found!" % mutate_index)
        return 1
        
    mutate_files=dict()
    for source_file, html_file in get_mutate_files(mutate_index):
        html_file = os.path.join(os.path.basename(mutate_project), html_file)
        print("found: '%s' for '%s'" % (html_file, source_file))
        mutate_files[source_file]=html_file

    run_cmd('mkdir -p %s'%opts.outDir)
    run_cmd('cp -a %s %s/' % (gcov_project, opts.outDir))
    run_cmd('cp -a %s %s/' % (mutate_project, opts.outDir))

    tool_dir = os.path.dirname(os.path.abspath(__file__))
    run_cmd('cp %s/data/* %s' % (tool_dir, opts.outDir))

    for src_file in gcov_files:
        run_cmd('lcov2mutate.py -i %s' % os.path.join(opts.outDir, gcov_files[src_file]))

    for src in mutate_files:
        if src in gcov_files:
            with open(os.path.join(opts.outDir, os.path.basename(src)+'.html'), 'w') as fout:
                fout.write(compare_file_template % (mutate_files[src],gcov_files[src]))
    
if __name__ == '__main__':
    main(sys.argv[1:])

    
def foo():
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
