import distutils
from distutils.core import setup
import glob

bin_files = glob.glob("bin/mock_files")
bin_files = bin_files + glob.glob("bin/ap_pipe") 

# The main call
setup(name='mocker',
      version ='0.1',
      license = "GPL",
      description = "A tools to mock files and the AP for LSST",
      author = "Felipe Menanteau",
      author_email = "felipe@illinois.edu",
      packages = ['mocker'],
      package_dir = {'': 'python'},
      scripts = bin_files,
      data_files=[('ups',['ups/mocker.table'])],
      )
