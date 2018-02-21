import os
import subprocess


_CYGWIN_HOME = os.getenv('CYGWIN_HOME', 'C:\\cygwin')
_EXEC_PATH = os.path.join(_CYGWIN_HOME, 'usr',  'local', 'bin')
_SYS_EXEC_PATH = os.path.join(_CYGWIN_HOME, 'bin')

TEMP = os.getenv('TEMP', 'C:\\TEMP')


def run_wfdb_app(app_name,app_args,working_dir, shell=True, check=True, stdout=subprocess.PIPE):
    process_args = [os.path.join(_EXEC_PATH, app_name)].extend(app_args)
    subprocess.run(process_args, shell=shell, check=check, cwd=working_dir, stdout=stdout)
