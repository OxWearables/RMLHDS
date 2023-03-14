---
layout: post
---

* This will become a table of contents (this text will be scrapped).
{:toc}

# Version control with Git

Git is a distributed version control system that allows developers to keep track of changes made to code over time. It was created by Linus Torvalds in 2005 to manage the development of the Linux kernel.

With Git, developers can create a repository to store their code and all of its versions. They can make changes to the code and commit those changes to the repository, creating a new version. Git keeps track of all of these versions, so developers can easily go back in time to see what changes were made and when.

Git uses a system of branches to allow developers to work on different versions of the code at the same time. Developers can create a new branch to work on a specific feature or bug fix, and then merge that branch back into the main code when they are finished.

## Getting Started

### Step 1: Install Git
First, you need to install Git on your computer. Go to the Git website and download the version that is appropriate for your operating system. Alternatively, if you use Anaconda, you can install Git by simply running `conda install git`.

### Step 2: Set up Git
Once you have installed Git, you need to set up your user name and email address. Open the command line interface or terminal and enter the following commands:

```console
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```
These commands will set your user name and email address, which will be associated with all of your Git commits.

### Step 3: Create a Git repository
A Git repository is a folder that contains all of your project files and their version history. 
Create a new directory called *myproject* and initialize a new Git repository:

```console
mkdir myproject
cd myproject
git init
```

*Question*: Where is the "repository" located? What's changed?

### Step 4: Add files to the repository
Create a plain text file *hello.txt* containing the following:

> Hello Wolrd!

The file contains a typo that we will fix later. 

Create a second file *hola.txt* containing the following:

> hola mundo

Now that we have some files to work with, pick the files for which you want to track changes. 
Start by adding *hello.txt*:

```console
git add hello.txt
```

Now type `git status`. *Question*: What do you see?

Next, add *hola.txt*:
```console
git add hola.txt
```

You can also add both files in one command:
```console
git add hello.txt hola.txt
```

...or add all the files in the current directory:
```console
git add .
```

### Step 5: Commit changes
You can now *commit* the changes for the files you selected. 
A *commit* is a core concept in git. It acts like a snapshot of the changes that you have made to the repository. 
To commit your changes, enter the following command:

```console
git commit -m "My first commit"
```

Type `git log`. *Question*: What do you see?

*Question*: What happens if you don't provide a message with `-m`?

### Step 6: Make some changes

Open *hello.txt* and fix the typo:

> Hello World!

Exit to the command line and type `git status`. *Question*: What do you see?

To commit the new changes you just made, repeat Step 4 & 5:

```console
git add hello.txt
git commit -m "Fix typo"
```

Verify with `git status` and `git log`.

### Step 7: Create a branch
You can think of a *branch* as a separate copy of your directory that you can work on without affecting the *main* branch. 

We will create a new branch in which we will do work to make *hola.txt* a bit more fancy.
To create a new branch, enter the following command:

```console
git branch fancy-hola
```

### Step 8: Switch to a branch
To switch to the new branch:

```console
git checkout fancy-hola
```

*Note*: You can't switch branches if your repository has "unsaved" changes. Either *commit*, *stash*, or undo your changes.

### Step 9: Do some work in new branch

Edit *hola.txt* to be:
> Hola Mundo

Save and commit:

```console
git add hola.txt
git ci -m "Capitalize words"
```

Edit *hola.txt* again:
> Hola Mundo!

Again, save and commit:
```console
git add hola.txt
git ci -m "Add exclamation mark!"
```

Now check `git log`

### Step 8: Merge branches
To merge changes from one branch into another, first switch to the branch you want to merge changes *into*.

Switch to the original branch (`master`/`main`):

```console
git checkout master
git log
```
You can check with `git log` that your last two commits are not here!

*Question*: Open *hola.txt*. Are the changes there?

Now, to merge the changes from the other branch `fancy-hola`:

```console
git merge fancy-hola
```

Check `git log` and *hola.txt* again to verify that the changes were applied.

## Git tools

If the command line interface is inconvenient, there exist tools that make the experience much more graphic such as [gitk](https://www.atlassian.com/git/tutorials/gitk) and [Git Kraken](https://www.gitkraken.com/).
