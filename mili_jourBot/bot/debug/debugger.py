
import pydevd

# Set up the debug session with PyCharm
debugger = pydevd.settrace('localhost', port=7131, stdoutToServer=True, stderrToServer=True, suspend=False, patch_multiprocessing=True)
