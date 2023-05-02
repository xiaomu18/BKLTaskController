import os, shutil
from distutils.core import setup
from Cython.Build import cythonize

files = ['BKLTC.py', 'BKLUtils.py']

setup(name='BKLTaskController Modules', ext_modules=cythonize(files))

print("remove building cache")

shutil.rmtree(".\\Build")

lst = os.listdir('.')
for filename in lst:
     stem, suffix = os.path.splitext(filename)
     if suffix == ".c":
          os.remove(filename)

print("remove original file")
for file in files:
     os.remove(file)

os.remove(__file__)

print("build done.")


