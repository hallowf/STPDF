import sys
import os
import pickle

__version__ = None
__version2__ = None
__releaseDate__ = None
__releaseDate2__ = None

if getattr(sys, "frozen", False):
    # pyInstaller
    data = None
    if os.path.isfile("version.pckl"):
        data = pickle.load(open("version.pckl", "rb"))
    if data is None:
        sys.stdout.write("\n\nError loading version file\n\n")
    else:
        __version__ = data["version"]
        __version2__ = data["version2"]
        __releaseDate__ = data["r_date"]
        __releaseDate2__ = data["r_date2"]
else:
    import subprocess
    args = sys.argv
    tag = True if "--tag" in sys.argv else False
    c_path = os.getcwd()
    p_source = "version.pckl" if c_path.endswith("src") \
        else "src/version.pckl"

    def set_version_tag(version):
        c_os = sys.platform
        c_os = "Windows" if c_os.startswith("win") else \
            ("Linux" if c_os.startswith("lin") else "Mac")
        tag = "%s-%s" % (c_os, version)
        print("Setting tag:", tag)
        os.environ["TRAVIS_TAG"] = tag

    def get_git_revision_short_hash():
        try:
            # ghash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])

            # independent of location as long as there is a git folder
            #   what about if you use setup_user.py install?
            #   what about if you don't have git?
            # can raise a subprocess.CalledProcessError, which means the return code != 0
            ghash = subprocess.check_output(['git', 'describe', '--always'], cwd=os.path.dirname(__file__))

            ghash = ghash.decode('utf-8').rstrip()
        except:
            # git isn't installed
            ghash = 'no.checksum.error'
        return 'dev.%s' % ghash

    revision = get_git_revision_short_hash()
    __version__ = "V0.1"
    __version2__ = 'V0.1+%s' % revision
    __releaseDate__ = '16/06/2019'
    __releaseDate2__ = '16 June, 2017'
    data = {
        "version": __version__,
        "version2": __version2__,
        "r_date": __releaseDate__,
        "r_date2": __releaseDate2__
    }
    # print(data)
    pickle.dump(data, open(p_source, "wb"))
    if tag:
        set_version_tag(__version__)
