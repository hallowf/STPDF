# <STPDF convert scans to pdf>
# Copyright (C) <2019>  <Alexandre Cortegaça>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import pickle

__version__ = None
__version2__ = None
__releaseDate__ = None
__releaseDate2__ = None
__developer__ = None
__developer2__ = None
__devhome__ = None

if getattr(sys, "frozen", False):
    # REQ: Travis windows build fails otherwise
    # https://stackoverflow.com/questions/47468705/pyinstaller-could-not-find-or-load-the-qt-platform-plugin-windows
    # https://stackoverflow.com/questions/54132763/how-to-fix-could-not-find-the-qt-platform-plugin-windows-in-when-implemen
    # https://stackoverflow.com/questions/20495620/qt-5-1-1-application-failed-to-start-because-platform-plugin-windows-is-missi
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(os.getcwd(), "PyQt5", "Qt", "plugins", "platforms", "")
    os.environ["QT_PLUGIN_PATH"] = os.path.join(os.getcwd(), "PyQt5", "Qt", "plugins", "")
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
        __developer__ = data["developer"]
        __developer2__ = data["developer2"]
        __devhome__ = data["devhome"]
else:
    import subprocess
    from subprocess import CalledProcessError
    from datetime import date
    from lxml import html
    import requests
    args = sys.argv
    tag = True if "--tag" in sys.argv else False
    c_path = os.getcwd()
    p_source = "version.pckl" if c_path.endswith("src") \
        else "src/version.pckl"

    def set_version_tag(version):
        c_os = sys.platform
        c_os = "Windows" if c_os.startswith("win") else \
            ("Linux" if c_os.startswith("lin") else \
                ("FreeBSD" if c_os.startswith("freebsd") else "Mac"))
        tag = "%s-%s" % (c_os, version)
        print("Setting tag:", tag)
        with open("version.txt", "w") as fh:
            fh.write(tag)

    def get_git_latest_version():
        try:
            ghash = subprocess.check_output(['git', 'describe', '--always'],
                                            cwd=os.getcwd())

            ghash = ghash.decode("utf-8").rstrip()
        except CalledProcessError:
            # git isn't installed
            ghash = "no.checksum.error"
        return ghash

    def get_git_revision_short_hash():
        try:
            # ghash = subprocess.check_output(['git',
            #               'rev-parse', '--short', 'HEAD'])

            # independent of location as long as there is a git folder
            #   what about if you use setup_user.py install?
            #   what about if you don't have git?
            # can raise a subprocess.CalledProcessError,
            # which means the return code != 0
            c_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                             cwd=os.getcwd())
            c_hash = c_hash.decode("utf-8").rstrip()
        except CalledProcessError:
            c_hash = "no.checksum.error"
        return c_hash

    def get_git_user():
        try:
            c_hash = subprocess.check_output(["git", "config", "user.name"],
                                             cwd=os.getcwd())
            c_hash = c_hash.decode("utf-8").rstrip()
        except CalledProcessError:
            c_hash = "no.checksum.error"
        return c_hash

    def get_git_user2(user):
        try:
            if user == "no.checksum.error":
                raise ValueError
            r = requests.get("https://github.com/%s" % user)
            h_tree = html.fromstring(r.content)
            name = h_tree.xpath("//span[@class='p-name vcard-fullname d-block overflow-hidden']/text()")[0]
            if name == "" or name is None:
                raise ValueError
        except CalledProcessError:
            name = "unknown"
        return name

    version = get_git_latest_version()
    l_commit = get_git_revision_short_hash()
    stage = "-Alpha" if version.endswith("a") else ("-Beta" if version.endswith("b") else "")
    today = date.today()
    t_short = today.strftime("%d/%m/%Y")
    t_long = today.strftime("%B %d, %Y")
    has_plus = "+" if version != "no.checksum.error" else ""
    __version__ = version if version != "no.checksum.error" else ""
    __version2__ = '%s%s%s%s' % (version, stage, has_plus, l_commit)
    __releaseDate__ = t_short
    __releaseDate2__ = t_long
    __developer__ = get_git_user()
    __developer2__ = get_git_user2(__developer__)
    __devhome__ = "https://github.com/%s" % __developer__
    data = {
        "version": __version__,
        "version2": __version2__,
        "r_date": __releaseDate__,
        "r_date2": __releaseDate2__,
        "developer": __developer__,
        "developer2": __developer2__,
        "devhome": __devhome__
    }
    pickle.dump(data, open(p_source, "wb"))
    if tag:
        set_version_tag(__version__)
