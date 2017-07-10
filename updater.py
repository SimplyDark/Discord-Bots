import os
import subprocess
import shutil
import stat


def update():
    # Get path to directory the program is running in
    path = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory to the cwd
    prev_dir = path.split("/")
    clone_dir_name = str(prev_dir.pop(-1))
    parent_dir = '/'.join(prev_dir)
    # Make temp folders
    try:
        os.makedirs(parent_dir + "/tmp/")
    except FileExistsError:
        pass
    tmp = parent_dir + "/tmp/"
    # Clone git repo to temp folders
    repo = "https://github.com/SimplyDark/Discord-Bots"
    clone_args = ["git", "--git-dir=" + tmp, "clone", repo]
    clone = subprocess.Popen(clone_args, cwd=r"{}".format(tmp))
    clone.communicate()
    # Copy contents of temp folders to cwd
    copy_args = ["rsync", "-av", "{}{}".format(tmp, clone_dir_name), path, "--exclude", tmp + clone_dir_name + "/.git"]
    copy = subprocess.Popen(copy_args)
    print("Copying update...")
    copy.communicate()
    # Clean up
    del_files(tmp)
    del_files(path + "/Discord-Bots")


def del_files(name):
    for root, dirs, files in os.walk(name):
        for file in dirs:
            os.chmod(os.path.join(root, file), stat.S_IWRITE | stat.S_IRUSR)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IWRITE | stat.S_IRUSR)
    shutil.rmtree(name)

