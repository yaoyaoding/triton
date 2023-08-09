import atexit

# clean the cache dir in envorioment variable TRITON_CACHE_DIR
import os
import shutil

cache_dir = os.environ['TRITON_CACHE_DIR']
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)

# dump ir
os.environ['MLIR_ENABLE_DUMP'] = '1'

# redict stderr to a file
import sys
fname = 'triton_stderr.log'
new_stderr = open(fname, 'w')
os.dup2(new_stderr.fileno(), sys.stderr.fileno())


def run_at_exit():
    import re
    new_stderr.close()

    lines = []
    with open(fname) as f:
        lines = list(f.readlines())
    current_lines = []
    # the pattern that starts with "//" and ends with "//"
    pattern = re.compile(r'//.*//')
    idx = 0
    shutil.rmtree('./ir', ignore_errors=True)
    os.makedirs('./ir', exist_ok=True)
    previous_content = ''
    for i, line in enumerate(lines):
        if not pattern.match(line):
            current_lines.append(line)
        else:
            if len(current_lines) > 0:
                current_content = '\n'.join(current_lines[1:])
                with open(f'ir/{idx}{"*" if previous_content != current_content else ""}.mlir', 'w') as f:
                    f.writelines(current_lines)
                previous_content = current_content
                idx += 1
            current_lines = [line]
    with open(f'ir/{idx}.txt', 'w') as f:
        f.writelines(current_lines)


atexit.register(run_at_exit)
