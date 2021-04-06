import os
import sys
from os.path import dirname, abspath

path = dirname(dirname(abspath(__file__)))
sys.path.append(path)
os.chdir(path)
