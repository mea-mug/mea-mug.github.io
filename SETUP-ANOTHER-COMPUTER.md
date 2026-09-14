# Setting this up on another computer

This guide is for **moving your own site to a second computer**, or working on it from
two computers. It is not for giving the kit to someone else — that is `MAKE-KIT.bat`,
explained in START-HERE.md.

You already have the GitHub account, the repository and the token, so you do **not**
repeat START-HERE.md. The whole move takes about fifteen minutes.

    Part 1  Install three programs
    Part 2  Download your site
    Part 3  Put your details file back
    Part 4  Check it works

---

## What comes with the download, and what does not

Your site lives on GitHub at `github.com/mea-mug/mea-mug.github.io`. Downloading it
brings back almost everything:

| Comes with the download                                                            | Stays behind on the old computer                                    |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Every page and photo (`html_files`)                                                | `my-github-details.txt` — your token, kept off GitHub on purpose    |
| All the buttons: `ADMIN`, `PUBLISH`, `EXPORT-FOR-AI`, `IMPORT-FROM-AI`, `MAKE-KIT` | `_ai-backups` — your undo history                                   |
| The scripts that run them                                                          | `resources` — the design notes folder                               |
| These guides                                                                       | `AI-PROMPT.md` and `AI-RESPONSE.md` — rebuilt whenever you use them |

Only the first item on the right matters. Part 3 deals with it.

---

## Part 1 - Install three programs

**1. Git for Windows** — downloads your site and publishes it.
Go to https://git-scm.com/download/win , run the file, click **Next** on every screen.

**2. Python 3.14** — runs the admin page and the AI buttons.
Download the 64-bit Windows installer directly:
https://www.python.org/ftp/python/3.14.7/python-3.14.7-amd64.exe

On the **first screen** of the installer, tick **Add python.exe to PATH** before you
click Install. This box is off by default and it is the one people miss. Without it,
`ADMIN.bat` says it cannot find Python.

Why this version and not simply the newest:

- **3.14 gets bug fixes and Windows installers until October 2027**, and security fixes
  until 2030. Older versions no longer get Windows installers for their updates, and
  3.13 stops getting them in October 2026.
- **The photo tool (Pillow, step 3) must support your Python.** Pillow 12.3.0 does support
  3.14. A brand-new Python can come out before Pillow catches up, and then step 3 fails.
- Any **3.14.x** works — if a later 3.14 is out, that is fine too. Do not jump to 3.15 or
  newer without checking that Pillow supports it.

Already have **Python 3.11 or newer** installed? You can keep it and skip this step.

> If typing `python` opens the Microsoft Store instead of doing anything, Python is not
> really installed — that is a shortcut Windows ships with. Install it from the link above.

**3. Pillow 12.3.0** — the photo tool that trims white borders and makes thumbnails.
Open a terminal (search the Start menu for **Terminal**) and paste:

```
python -m pip install pillow==12.3.0
```

This exact version has been tested with the site's photo processing.

Skip this and the site still works, but photos you add from then on arrive untrimmed,
full size, and without a thumbnail.

Restart the computer once.

---

## Part 2 - Download your site

**Choose a short place for it**, such as your Desktop or `C:\Sites`. The longest file name
inside the site is 103 characters and Windows refuses any path over 260, so the folder
you put it in needs a path shorter than about 150 characters. Deep folder trees are the
one thing that makes this step fail.

1. Open that place in File Explorer.
2. Right-click an empty spot and choose **Open Git Bash here**.
   On Windows 11 it is under **Show more options**.
3. Paste this and press Enter:

```
git clone https://github.com/mea-mug/mea-mug.github.io.git
```

You get a folder called `mea-mug.github.io` with your whole site in it. Rename it if you
like — nothing depends on the name.

**Do not use GitHub's "Download ZIP" button instead.** A ZIP leaves out a hidden folder
called `.git` that holds your publishing history. Without it, `PUBLISH.bat` treats the
folder as a brand-new project, and your first publish can clash with the copy already on
GitHub.

---

## Part 3 - Put your details file back

`PUBLISH.bat` and the admin page both need `my-github-details.txt`, and it is not in the
download. Pick one:

**Copy it from the old computer.** Use a USB stick. Not e-mail, not a chat message, not a
shared cloud link — that file holds your token. Put it in the new folder next to
`PUBLISH.bat`.

**Or make a fresh one.** Copy `my-github-details.EXAMPLE.txt`, rename the copy to
`my-github-details.txt`, and fill in the four lines:

    GITHUB_USERNAME=mea-mug
    GITHUB_EMAIL=the e-mail on your GitHub account
    GITHUB_REPO=mea-mug.github.io
    GITHUB_TOKEN=your token

Reuse your existing token if you still have it — the same token works on any number of
computers. If you have lost it, make a new one as in START-HERE.md Part 5, ticking both
`repo` and `workflow`.

Either way it stays private automatically. `.gitignore` keeps it off GitHub on every
computer.

---

## Part 4 - Check it works

Double-click **`ADMIN.bat`**. If the admin page opens and shows `mea-mug.github.io` at the
top, you are done. Press **Open preview** to see the site.

You do not need to publish anything to test the move.

---

## Working on both computers

One rule keeps the two copies from drifting apart:

**Publish before you switch computers.**

- **Finishing** on one computer — publish.
- **Starting** on the other — double-click `PUBLISH.bat` first, even if you have changed
  nothing. When there is nothing new it only fetches the latest version from GitHub and
  changes nothing online. You will see _"Nothing has changed since last time — checking
  GitHub anyway…"_.

If you edit the same page on both computers without publishing in between, the second
publish stops and names the file that clashes. Nothing is lost. START-HERE.md explains
what to do under _"GitHub has a version of a file that clashes with yours"_.

Undo history is per computer: `_ai-backups` on one machine only holds the edits made there.

---

## If something goes wrong

**"Filename too long" while downloading.** The folder is too deep. Delete the half-made
folder and download somewhere shorter, such as `C:\Sites`. Or tell Git to allow long
paths, then download again:

```
git config --global core.longpaths true
```

**"detected dubious ownership" — or `PUBLISH.bat` says it could not read the files.**
This happens when the folder is on a USB stick or external drive. Keep the folder on the
computer's own drive. If it has to stay on the external drive, Git's error message prints
the exact `git config --global --add safe.directory ...` line for your folder — run that
one line.

**`ADMIN.bat` says it cannot find Python.** Python is installed without the PATH box
ticked. Run the Python installer again, choose **Modify**, and tick **Add Python to
environment variables**.

**`ADMIN.bat` says it cannot find your details file.** Do Part 3.

**Photos arrive untrimmed and without a thumbnail.** Pillow is missing — do Part 1, step 3.

**You copied the `resources` folder across.** On the old computer a local rule kept it off
GitHub, and that rule does not travel. To keep it private on the new computer too, add a
line reading `resources/` to the end of `.gitignore`.
