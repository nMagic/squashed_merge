#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import subprocess
import os
import sys
from datetime import datetime

class GitException(Exception):
    pass

def proc(*args):
    '''
    Execute process with args.
    '''
    cmd = ''.join([str(item) + ' ' for item in args])
    return subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def merge(a, b):
    '''
    Merge branch a into branch b.
    Step-by-step:
        Move to destination branch with git checkout command.
        Merge branches with git merge --squash command.
        Check status list for determinate conflicts with git status --short command.
        Call each conflict file for manual resolving with nano file command.
        Commit merge with git commit -a -m 'Squashed merge from a into b'
    '''
    checkout = proc("git", "checkout", b).stderr.read().decode("utf-8")
    if len(checkout) and checkout.startswith("error:"):
        raise GitException(checkout)
    merge = proc("git", "merge", "--squash", a).stderr.read().decode("utf-8")
    if len(merge) and merge.startswith("merge:"):
        raise GitException(merge)
    status = proc("git", "status", "--short").stdout.read().decode("utf-8")
    status_list = {item.split(' ')[1]: item.split(' ')[0] for item in status.split('\n')[:-1]}
    for key in status_list:
        if status_list[key] == "UD":
            proc("git", "rm", key)
        elif status_list[key] == "AA" or status_list[key] == "UU":
            os.system("nano " + key)
    commit = proc("git", "commit", "-a", "-m 'Squashed merge from "+a+" into "+b+"'").stderr.read().decode("utf-8")
    if len(commit):
        raise GitException(commit)

def search_merge(a, b):
    '''
    Search and return last merge commit between branch a and branch b.
    '''
    a_to_b = proc("git", "log", "--pretty=format:'%ci%n%h'", "--max-count=1",
                  "--grep='Squashed merge from "+a+" into "+b+"'", "--all").stdout.read().decode("utf-8")
    b_to_a = proc("git", "log", "--pretty=format:'%ci%n%h'", "--max-count=1",
                  "--grep='Squashed merge from " + b + " into " + a + "'", "--all").stdout.read().decode("utf-8")
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
    return a_to_b[1] if a_to_b[0] > b_to_a[0] else b_to_a[1]

def revert(node):
    '''
    Revert merge commit with sha1-hash "node".
    '''
    proc("git", "revert", node)
    status = proc("git", "status", "--short").stdout.read().decode("utf-8")
    status_list = {item.split(' ')[1]: item.split(' ')[0] for item in status.split('\n')[:-1]}
    for key in status_list:
        if status_list[key] == "UD":
            proc("git", "rm", key)
        elif status_list[key] == "AA" or status_list[key] == "UU":
            os.system("nano " + key)
    commit = proc("git", "commit", "-a", "-m 'Delete squashed merge "+node+"'").stderr.read().decode("utf-8")
    if len(commit):
        raise GitException(commit)

def start(a, b):
    merge_commit = search_merge(a, b)
    if merge_commit:
        try:
            revert(merge_commit)
        except GitException:
            raise
    try:
        merge(a, b)
    except GitException:
        raise


if __name__ == "__main__":
    try:
       start(sys.argv[1], sys.argv[2])
    except GitException as ex:
        print(ex)
    except IndexError as ex:
        print("Arguments must be passed")
