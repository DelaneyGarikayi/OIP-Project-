# OIP — Optical Image Processing

This repository contains the student material for the **Optical Image Processing (OIP)** course.

The repository is updated throughout the semester as new course material becomes available.

## Getting the course material

### Option 1: Clone the Git repository

The recommended option is to clone the repository. This makes updating the course material particularly easy:

```bash
git clone <repository-url> oip-shared
cd oip-shared
```

During the semester, update your local copy with:

```bash
git pull
```

### Option 2: Download a release

A ZIP archive is provided for each teaching week through itslearning and the GitLab releases page.

Each release represents the complete state of the student material available at that point in the course.

For example:

- `week-01` contains all material available after Week 1.
- `week-02` contains all material available after Week 2.
- `week-03` contains all material available after Week 3.

The releases are cumulative: a later release contains the material from the earlier weeks together with the newly released material.

## Repository structure

The repository is organized as follows:

```text
oip-shared/
├── notebooks/
│   ├── week-01/
│   ├── week-02/
│   └── ...
│
├── lecture-notes/
│   ├── week-01/
│   ├── week-02/
│   └── ...
│
├── work/
│   ├── week-01/
│   ├── week-02/
│   └── ...
│
├── data-external/
│   └── img/
│
├── src/
│   └── oip/
│
├── pyproject.toml
└── uv.lock
```

The directories have the following purposes:

- `notebooks/` — original exercise notebooks distributed with the course.
- `lecture-notes/` — annotated notebooks and material produced during the lectures.
- `work/` — your personal working directory.
- `data-external/` — images and other data used by the notebooks.
- `src/oip/` — Python functionality shared by the course notebooks.

## Python environment

The course uses [uv](https://docs.astral.sh/uv/) to manage the Python environment.

After cloning or downloading the course material, open a terminal in the root directory of the repository and run:

```bash
uv sync
```

This creates the course environment and installs the required Python packages.

Commands can then be executed inside the course environment using:

```bash
uv run <command>
```

For example, start Jupyter Lab with:

```bash
uv run jupyter lab
```

After an update to the course repository, you can run

```bash
uv sync
```

again if the course dependencies have changed.

## Working on exercises

The `notebooks/` directory contains the original exercise notebooks distributed with the course.

**Do not edit these notebooks directly.**

Instead, copy the notebooks for the current week into the `work/` directory and work on the copies.

For example, for Week 1:

```bash
mkdir -p work/week-01
cp notebooks/week-01/*.ipynb work/week-01/
```

Your directory will then look like:

```text
oip-shared/
├── notebooks/
│   └── week-01/          # original course notebooks
│
├── work/
│   └── week-01/          # your copies — work here
│
├── lecture-notes/
├── data-external/
└── src/
```

Only edit notebooks inside `work/`.

The `work/` directory is ignored by Git. Your solutions and other changes in this directory therefore remain local to your computer and are not affected when the course repository is updated.

### Relative paths

The directory structure of `work/` deliberately mirrors that of `notebooks/`.

For example, a notebook distributed as

```text
notebooks/week-01/exercise.ipynb
```

may access an image using:

```text
../../data-external/img/example.png
```

After copying the notebook to

```text
work/week-01/exercise.ipynb
```

the same relative path still works:

```text
../../data-external/img/example.png
```

There is therefore no need to change paths in the exercise notebooks.

### Back up your work

The `work/` directory contains **your work**. It is intentionally not tracked by the course Git repository.

This also means that the course repository does not provide a backup of your solutions.

You are responsible for backing up the contents of `work/`. Consider keeping a separate backup or putting your personal work under your own version control.

## Updating the course material

New material will be added to the repository throughout the semester.

If you cloned the Git repository, update your local copy before starting a new week's exercises:

```bash
git pull
```

Then copy the new exercise notebooks into your working directory.

For example, for Week 2:

```bash
mkdir -p work/week-02
cp notebooks/week-02/*.ipynb work/week-02/
```

A typical weekly workflow is therefore:

```bash
# Update the course material
git pull

# Update the Python environment if necessary
uv sync

# Copy this week's exercises
mkdir -p work/week-02
cp notebooks/week-02/*.ipynb work/week-02/

# Start Jupyter Lab
uv run jupyter lab
```

Because your own notebooks are stored under `work/`, `git pull` will not overwrite your solutions.

### Corrections to exercises

Occasionally, an already published exercise may need to be corrected.

In that case, `git pull` updates the original notebook under `notebooks/`, but it does **not** modify the copy that you are already working on under `work/`.

For example:

```text
notebooks/week-02/exercise.ipynb   # updated by git pull
work/week-02/exercise.ipynb        # your version remains unchanged
```

Check course announcements if corrections to an existing exercise are published.

## Lecture notes

The `lecture-notes/` directory contains annotated notebooks and other material produced during the lectures.

For example:

```text
lecture-notes/
├── week-01/
├── week-02/
└── ...
```

These files are provided as reference material.

As with the original notebooks, you should normally not modify files under `lecture-notes/`. If you want to experiment with one of these notebooks, copy it to your `work/` directory first.

## Data

Images and other externally supplied course data are stored under:

```text
data-external/
```

Images are normally located under:

```text
data-external/img/
```

The course notebooks use relative paths to access these files. Do not move or rename the `data-external/` directory unless you also adjust the corresponding paths in the notebooks.

## Shared OIP Python library

Python functionality used by several notebooks is provided by the course package under:

```text
src/oip/
```

The package is installed into the course environment by:

```bash
uv sync
```

You should normally not modify the files under `src/oip/`. Updates to the course library are distributed together with the other course material.

## Releases

Each teaching snapshot is identified by a Git tag:

```text
week-01
week-02
week-03
...
```

A corresponding ZIP archive is generated for each release.

The releases are cumulative. For example, `week-05` represents the complete set of student material published up to and including Week 5.

Older releases remain available so that a particular state of the course material can be reproduced.

The same release archives may also be distributed through itslearning.

## Quick reference

### First-time setup

```bash
git clone <repository-url> oip-shared
cd oip-shared

uv sync
uv run jupyter lab
```

### Start working on Week 1

```bash
mkdir -p work/week-01
cp notebooks/week-01/*.ipynb work/week-01/

uv run jupyter lab
```

### Start a new week

For example, Week 2:

```bash
git pull
uv sync

mkdir -p work/week-02
cp notebooks/week-02/*.ipynb work/week-02/

uv run jupyter lab
```

## Rule of thumb

- `notebooks/` — material distributed by the instructor; **do not edit**
- `lecture-notes/` — annotated material from the lectures; **do not edit**
- `data-external/` — shared images and data; **do not edit**
- `src/` — shared course Python code; **do not edit**
- `work/` — **your personal working directory; edit your notebooks here**

When in doubt: **copy the file to `work/` before modifying it.**