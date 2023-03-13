---
layout: post
---

* This will become a table of contents (this text will be scrapped).
{:toc}

# Python Virtual Environments Tutorial

Virtual environments are a way to isolate Python packages and dependencies for different projects, preventing conflicts between them. In this tutorial, we'll learn how to create and activate a virtual environment. We will show two common approaches: using the `venv` module in Python 3, and using Anaconda environments.

The examples below assume Linux command line, but the steps are similar in Windows.

## Step 1: Install Python
There are a few ways we can install Python. If you are using Ubuntu, you already have some version of Python preinstalled. However, we don't recommend that you use your system's own Python as you may risk corrupting your system. Instead, we recommend that you use Anaconda for further isolation.

Anaconda/Conda is a popular distribution of Python and other tools for data science.
If you haven't already, you'll need to install Conda on your machine. You can download the latest version of Conda from the official website: https://docs.conda.io/en/latest/miniconda.html

**Windows**: Once you installed Anaconda, go to the Start Menu and look for "Anaconda Prompt". This will open a terminal and you'll be ready to go.

**Linux**: Once you installed Anaconda, re-open your terminal. If you see `(base)` printed in front of your prompt, you're ready to go.

## Step 2: Create a new project directory
Create a new directory for your project. In this tutorial, we'll call it *myproject*. You can create this directory using the command line:

```console
mkdir myproject
cd myproject
```

## Step 3 (`venv`): Create a virtual environment
Now that we have a project directory, let's create a virtual environment for it. To create a virtual environment using `venv`, run the following command:

```console
python3 -m venv venv
```

This command creates a new directory called *venv* inside your *myproject* directory. The name is arbitrary and is a simple folder which will contain all of your project's dependencies.
Another convention is to name it *.venv* (leading dot), making it a hidden folder.

## Step 3 (`conda`): Create a virtual environment
To create a virtual environment using Conda, run the following command:

```
conda create --name myenv
```

This command creates a new virtual environment called *myenv*. 

*Question*: Where is the folder for this environment located?

## Step 4 (`venv`): Activate the virtual environment
To activate the virtual environment, run the following command:

```console
source venv/bin/activate
```

You should now see `(venv)` at the beginning of your command prompt, indicating that you're in the virtual environment.

## Step 4 (`conda`): Activate the virtual environment
To activate the virtual environment, run the following command:

```console
conda activate myenv
```

You should now see `(myenv)` at the beginning of your command prompt, indicating that you're in the virtual environment.

## Step 5 (`venv`/`pip`): Install packages
Now that we're inside the virtual environment, we can install packages without affecting any other projects on our system. For example, let's install the requests package:

```
pip install requests
```

This command installs the requests package and any dependencies it requires inside our virtual environment.

Pip ("Pip Installs Packages") is Python's standard package management system.

*Question*: Where was the package installed?

## Step 5 (`conda`): Install packages
Now that we're inside the virtual environment *myenv*, let's install the numpy package:

```console
conda install numpy
```

This command installs the numpy package and any dependencies it requires inside our virtual environment.

*Question*: Where was the package installed?

*Question*: Can we use `pip` here?

## Step 6 (`venv`): Use the virtual environment
Now that we've installed a package, let's use it in our Python code. Create a new file called *main.py* inside your *myproject* directory with the following code:

```python
import requests

response = requests.get('https://www.google.com')
print(response.status_code)
```

This code uses the requests package to make a GET request to Google's homepage and prints the response status code.

Run your script with `python3 main.py`.

## Step 6 (`conda`): Use the virtual environment
Now that we've installed a package, let's use it in our Python code. Create a new file called *main.py* inside your *myproject* directory with the following code:

```python
import numpy as np

a = np.array([1, 2, 3])
print(a)
```

This code uses the numpy package to create an array and prints it to the console.

Run your script with `python3 main.py`.

## Step 7 (`venv`): List your dependencies

```console
pip freeze > requirements.txt
pip install –r requirements.txt
```

This will list all the packages that are currently installed in your environment.

## Step 7 (`conda`): List your dependencies
 
```console
conda env export > environment.yaml
conda install –f environment.yaml
```

Note: In contrast to the `venv` approach, this will recreate a whole new virtual environment.

## Step 8 (`venv`): Deactivate the virtual environment
Once you're done working with your virtual environment, you can deactivate it using the following command:

```console
deactivate
```

This command returns you to your regular shell prompt, outside of the virtual environment.

*Question*: Test your *main.py* script again. Does it work? Why?

## Step 8 (`conda`): Deactivate the virtual environment
Once you're done working with your virtual environment, you can deactivate it using the following command:

```console
conda deactivate
```

This command returns you to your regular shell prompt, outside of the virtual environment.

*Question*: Test your *main.py* script again. Does it work? Why?

## Conclusion
In this tutorial, we learned how to create and activate a virtual environment using `venv` and `conda`, how to install packages inside the virtual environment, and how to use those packages in our code. Virtual environments are a powerful tool for managing dependencies and preventing conflicts between projects, and we encourage you to use them in your own Python projects.

## Listing existing environments

To list all environments that were created in Conda:

```console
conda env list
```

This will print a list of all Conda environments.

Similar options are not available with `venv`. You will need to remember the location of the *venv* folders if you want to return to them in the future.

## Deleting environments

In Conda:
```console
conda env remove -n myenv
```

In `venv`, simply delete the folder that you created with `venv`.

## Environment managers and Package managers
`venv` is an environment manager

`pip` is a package manager

`conda` is both a package & environment manager, plus other data sciency tools

You _could_ use both `pip` and `conda` for package management, but we recommend that you don't mix them and stick to one.

*Best practice*: Using `conda` to manage the *environment*, and `pip` to manage the *packages*.

## Use `venv` or `conda`?
The most obvious difference is the place where environments are stored. `venv` keeps it near your project files whereas `conda` stores it somewhere in its folder. On the other hand, this means that Conda environments are more easily accesible globally: If we want to activate some environment, we don't need to remember where it was installed (see Step 4). 

`venv` is part of the standard library, meaning that there is no need for additional downloads. But if you are doing data science, it is likely that you will download Anaconda anyway.
