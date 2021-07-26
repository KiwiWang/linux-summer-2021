#!/usr/bin/env python3

# tested in python 3.8.10

import subprocess

def print_stderr_if_ret_nonzero(p):
    # but no error handling, hahaha
    if p.returncode:
        cmd = "".join(p.args)
        print(f"{cmd} return {p.returncode}, stderr: {p.stderr}")

complete_proc = subprocess.run(["sudo", "insmod", "hideproc.ko"])
print_stderr_if_ret_nonzero(complete_proc)

# get current sleep
complete_proc = subprocess.run(["pidof", "sleep"], capture_output=True)
print_stderr_if_ret_nonzero(complete_proc)
org_sleep_id = complete_proc.stdout.decode().split()
org_sleep_id.sort()
print(f"Original sleep id: {org_sleep_id}")

# fork some sleep
sleep_proc_list = [subprocess.Popen(["sleep", "600"]) for _ in range(5)]
# get all sleep id
complete_proc = subprocess.run(["pidof", "sleep"], capture_output=True)
print_stderr_if_ret_nonzero(complete_proc)
all_sleep_id = complete_proc.stdout.decode().split()
all_sleep_id.sort()
print(f"all sleep id: {all_sleep_id}")
new_sleep_id = list(set(all_sleep_id) - set(org_sleep_id))
new_sleep_id.sort()
print(f"\nsleep id we fork: {new_sleep_id}")

def hide_unhide(id_list):
    print("- Begin to hide -")
    # hide new_sleep_id
    for sleep_id in id_list:
        complete_proc = subprocess.run(f'echo "add {sleep_id}" | sudo tee /dev/hideproc', shell=True)
        print_stderr_if_ret_nonzero(complete_proc)
        complete_proc = subprocess.run(["pidof", "sleep"], capture_output=True)
        print_stderr_if_ret_nonzero(complete_proc)
        remaining = list((set(complete_proc.stdout.decode().split()) & set(new_sleep_id)) - set(org_sleep_id))
        remaining.sort()
        print(f"Remaining: {remaining}")

    print("\n- Begin to unhide -")
    # unhided new_sleep_id
    for sleep_id in id_list:
        complete_proc = subprocess.run(f'echo "del {sleep_id}" | sudo tee /dev/hideproc', shell=True)
        print_stderr_if_ret_nonzero(complete_proc)
        complete_proc = subprocess.run(["pidof", "sleep"], capture_output=True)
        print_stderr_if_ret_nonzero(complete_proc)
        remaining = list((set(complete_proc.stdout.decode().split()) & set(new_sleep_id)) - set(org_sleep_id))
        remaining.sort()
        print(f"Remaining: {remaining}")


print("********* 1st round ****************")
hide_unhide(new_sleep_id[:3])
print("\n********* 2nd round ****************")
hide_unhide(new_sleep_id[3:])
print("\n********* 3rd round ****************")
hide_unhide(new_sleep_id)

# kill all forked sleep id
for proc in sleep_proc_list:
    proc.kill()

complete_proc = subprocess.run(["sudo", "rmmod", "hideproc.ko"])
print_stderr_if_ret_nonzero(complete_proc)