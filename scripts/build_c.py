import os
from shutil import rmtree

PATH_TO_PROJECT = "/home/serj/work/mirror0/mirror0"
BUILD_DIR = "../mirror0_c"
EXCLUDE_DIRS = ["tests", "git_ignore", "virtual_env", "notes", "scripts", "build"]

biicode_pkg_path = PATH_TO_PROJECT 
biicode_python_path = os.path.dirname(biicode_pkg_path)
build_dir = BUILD_DIR 
src_dir = os.path.abspath(os.path.join(build_dir, 'src'))
rmtree(build_dir)
if os.path.exists(src_dir):
    rmtree(src_dir)
os.makedirs(src_dir)
ignored_files = ['__init__.py']
included_dirs = [os.path.join(biicode_pkg_path, dir_) for dir_ in ['..']]

from Cython.Build import cythonize
def do_cythonize(force_compile):
   '''
   Creates c files from your source python
   Params:
       force_compile: boolean, if true compiles regardeless 
                      of whether the file has changed or not
   Returns:
       list of c files relative to biicode_pkg_path
   '''
 
   c_files = []
   for dir_ in included_dirs:
       for dirname, dirnames, filenames in os.walk(dir_):
           for edir in EXCLUDE_DIRS:
               if edir in dirnames:
                   dirnames.remove(edir)
 
           for filename in filenames:
               file_ = os.path.join(dirname, filename)
               stripped_name = os.path.relpath(file_, biicode_python_path)
               file_name, extension = os.path.splitext(stripped_name)
 
               if extension == '.py':
                   target_file = os.path.join(src_dir, file_name + '.c')
                   if filename not in ignored_files:
                       c_files.append(stripped_name.replace('.py', '.c'))
                       file_dir = os.path.dirname(target_file)
                       if not os.path.exists(file_dir):
                           os.makedirs(file_dir)
 
                       extension = cythonize(stripped_name,
                                             force=force_compile, 
                                             build_dir=src_dir)
   return c_files

from distutils import sysconfig
from distutils.extension import Extension
import platform

def prepare(abs_path_c_files):
   modules = []
   for c_file in abs_path_c_files:
       relfile = os.path.relpath(c_file, src_dir)
       filename = os.path.splitext(relfile)[0]
       extName = filename.replace(os.path.sep, ".")
       extension = Extension(extName,
                             sources=[c_file],
                             define_macros=[('PYREX_WITHOUT_ASSERTIONS',
                                             None)]  # ignore asserts in code
                             )
       modules.append(extension)
   if platform.system() != 'Windows':
       cflags = sysconfig.get_config_var('CFLAGS')
       opt = sysconfig.get_config_var('OPT')
       sysconfig._config_vars['CFLAGS'] = cflags.replace(' -g ', ' ')
       sysconfig._config_vars['OPT'] = opt.replace(' -g ', ' ')
   if platform.system() == 'Linux':
       ldshared = sysconfig.get_config_var('LDSHARED')
       sysconfig._config_vars['LDSHARED'] = ldshared.replace(' -g ', ' ')
   elif platform.system() == 'Darwin':
       #-mno-fused-madd is a deprecated flag that now causes a hard error
       # but distuitls still keeps it
       # it was used to disable the generation of the fused multiply/add instruction
       for flag, flags_line in sysconfig._config_vars.iteritems():
           if ' -g' in str(flags_line):
               sysconfig._config_vars[flag] = flags_line.replace(' -g', '')
       for key in ['CONFIG_ARGS', 'LIBTOOL', 'PY_CFLAGS', 'CFLAGS']:
           value = sysconfig.get_config_var(key)
           if value:
               sysconfig._config_vars[key] = value.replace('-mno-fused-madd', '')
               sysconfig._config_vars[key] = value.replace('-DENABLE_DTRACE',  '')
   return modules

c_files = do_cythonize(True)
print str(c_files)

from distutils.core import setup
 
abs_path_c_files = [os.path.join(src_dir, c) for c in c_files]
modules = prepare(abs_path_c_files)
 
setup(
       name="bii",
       version="1.4-b1",
       script_name='setup.py',
       script_args=['build_ext'],
       packages=['mirror0'],
       ext_modules=modules,
       )


