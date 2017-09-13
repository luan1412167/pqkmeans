import os
import re
import sys
import platform
import subprocess

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion


def requirements():
    list_requirements = []
    with open('requirements.txt') as f:
        for line in f:
            if line.find("git") == -1:
                list_requirements.append(line.rstrip())
    return list_requirements


def dependencies():
    list_requirements = []
    with open('requirements.txt') as f:
        for line in f:
            if line.find("git") >= 0:
                list_requirements.append(line.rstrip())
    print(list_requirements)
    return list_requirements


class CMakeExtension(Extension):
    """
    @see https://github.com/pybind/cmake_example/blob/master/setup.py
    """

    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """
    @see https://github.com/pybind/cmake_example/blob/master/setup.py
    """

    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2 ** 32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)


setup(
    name='pqkmeans',
    version='0.0.1',
    author='',
    author_email='',
    description='',
    long_description='',
    install_requires=requirements(),
    dependency_links=dependencies(),
    # dependency_links=[
    #     "git+https://github.com/Hi-king/read_texmex_dataset_python.git#egg=read_texmex_dataset_python-1.0"
    # ],
    packages=find_packages(),
    ext_modules=[CMakeExtension('_pqkmeans')],
    cmdclass=dict(build_ext=CMakeBuild),
    test_suite='test',
    zip_safe=False,
)
