import subprocess
import os
from datetime import datetime

class GitException(Exception):
    pass

def proc(*args):
    cmd = ''.join([str(item) + ' ' for item in args])
    print(cmd)
    return subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def merge(a, b):
    checkout = proc("git", "checkout", b).stderr.read().decode("utf-8")
    if len(checkout) and checkout.startswith("error:"):
        raise GitException(checkout)
    '''merge = proc("git", "merge", "--squash", a).stderr.read().decode("utf-8")
    if len(merge) and merge.startswith("merge:"):
        raise GitException(merge)
    status = proc("git", "status", "--short").stdout.read().decode("utf-8")
    status_list = {item.split(' ')[1] : item.split(' ')[0] for item in status.split('\n')[:-1]}
    for key in status_list:
        if status_list[key] == "UD" : proc("git", "rm", key)
        elif status_list[key] == "AA" or status_list[key] == "UU" : os.system("nano " + key)'''
    merge = proc("git", "merge", "--squash", "-s recursive", "-Xtheirs", a).stderr.read().decode("utf-8")
    if len(merge) and merge.startswith("error:"):
        raise GitException(merge)
    commit = proc("git", "commit", "-a", "-m 'Squashed merge from "+a+" into "+b+"'").stderr.read().decode("utf-8")
    if len(commit):
        raise GitException(commit)

def search_merge(a, b):
    a_to_b = proc("git", "log", "--pretty=format:'%ci%n%h'", "--max-count=1",
                  "--grep='Squashed merge from "+a+" into "+b+"'").stdout.read().decode("utf-8")
    b_to_a = proc("git", "log", "--pretty=format:'%ci%n%h'", "--max-count=1",
                  "--grep='Squashed merge from " + b + " into " + a + "'").stdout.read().decode("utf-8")
    if len(b_to_a) == 0 and len(a_to_b) == 0:
        return False
    elif len(b_to_a) == 0:
        return a_to_b.split('\n')[1]
    elif len(a_to_b) == 0:
        return b_to_a.split('\n')[1]
    a_to_b = a_to_b.split('\n')
    a_to_b[0] = datetime.strptime(a_to_b[0][:-6], "%Y-%m-%d %H:%M:%S")
    b_to_a = b_to_a.split('\n')
    b_to_a[0] = datetime.strptime(b_to_a[0][:-6], "%Y-%m-%d %H:%M:%S")
    return a_to_b[0] if a_to_b[0] > b_to_a[0] else b_to_a[0]

if __name__ == "__main__":
    os.chdir("../git-test/")
    try:
       print(search_merge('KLM', 'XYZ'))
    except GitException as ex:
        print(ex)
    #print(proc("git reset 14d600a --hard").stdout.read().decode("utf-8"))