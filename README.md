# Unit testing in python

## Goal

Learn how to structure and write unit tests for `python`.

## Prerequisites

A Linux or MacOS machine for local development. If you are running Windows, you first need to set up the *Windows Subsystem for Linux (WSL)* environment.

You need `docker cli` on your machine for testing purposes, and/or on the machines that run your pipeline.
You can check this by running the following command:
```sh
docker --version
```

## What we have

Let's start with a `python` file that has a function:
```sh
def formatLinks(links: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for link in links:
        if not isinstance(link, dict):
            continue
        label = str(link.get("label", "")).strip()
        url = str(link.get("url", "")).strip()
        if label and url:parts.append(f"[{label}]({url})")
    return " ".join(parts)
```
, and is located in an *app* directory.

## What we want

The goal is to build unit tests in such a way, that we can call all of them with a single command that must not change when we add more unit tests or unit testing files.

## Implementation

Let's create a unit testing file:
```sh
import unittest

import sys
sys.path.append('app')

class TestGenerate(unittest.TestCase):

if __name__ == '__main__':
    unittest.main()
```
in another directory named *unit-tests*, for example.
Here we have a class named *TestGenerate*, which currently does not contain any unit tests. Let's also note that we add the directory where our code lies(*app*) to the paths that can be used to import functions.

Let's add 2 unit tests to *TestGenerate*:
```sh
    def test_formatLinks_emptyList(self):
        """Should return empty string when links list is empty"""
        result = formatLinks([])
        self.assertEqual(result, "")

    def test_formatLinks_singleLink(self):
        """Should format a single link correctly"""
        links = [{"label": "GitLab", "url": "https://gitlab.com"}]
        result = formatLinks(links)
        self.assertEqual(result, "[GitLab](https://gitlab.com)")
```
The unit tests themselves are not relevant, but they should pass.

With this setup we can now call:
```sh
python3 -m unittest discover -s ./unit-tests -p 'test_*.py'
```
, which will return:
```sh
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```
So the tests passed, and everything looks good. The command we used discovers unit testing files starting with *test_* in the *unit-tests* directory. This looks pretty dynamic, since we did not had to hardcode the name of the testing file(*test_generate.py*), or the name of the testing class(*TestGenerate*). Let's actually try this out by moving one of the unit tests to another file:
```sh
import unittest

import sys
sys.path.append('app')
from app.generate import formatLinks

class TestGenerate2(unittest.TestCase):

    def test_formatLinks_singleLink(self):
        """Should format a single link correctly"""
        links = [{"label": "GitLab", "url": "https://gitlab.com"}]
        result = formatLinks(links)
        self.assertEqual(result, "[GitLab](https://gitlab.com)")

if __name__ == '__main__':
    unittest.main()
```

If we now run:
```sh
python3 -m unittest discover -s ./unit-tests -p 'test_*.py'
```
again, we get exactly the same result, so the second unit testing class with the moved unit test was discovered, and its unit tests ran successfully.

This looks good, and achieves what we wanted, but let's go a little further. Since we are building unit tests and infrastructure to run them, we want to build them with the purpose of running in a CI/CD pipeline. In this case, I suggest to have all the command run via `Docker` so that we do not need to leave the configuration of machines where the pipeline runs to others that do not have the experience to set it up. Our only requirement is `docker cli`.

## Adding docker

Let's start with a dockerfile that can run python:
```sh
FROM python:3.13-alpine

COPY ./ /app
WORKDIR /app
```
We also added everything from our repository in an *app* directory and configured it to be the working directory. Note that the versions are pinned.

Now we can crate a docker-compose file to add extra logic, although not much will be needed for our scenario:
```sh
services:
  main:
    image: pythonunittests
    network_mode: host
    working_dir: /app
    entrypoint: ["sh", "-c"]
    command: ["python3 -m unittest discover -s ./unit-tests -p 'test_*.py'"]
```
Note that we moved our command to call the unit tests in here. Here you can add environment variables for more complex use cases, or add more commands if you need to.

The only thing that is missing is a simple shell script that triggers all of this:
```sh
#!/bin/sh
set -e

docker build -t pythonunittests .
docker compose run --rm main
```
In here we just build the dockerfile and run the only defined service. Note that the container will be deleted after it runs, so you do not have to worry about any kind of leftovers.

Now we can just run:
```sh
sh test.sh
```
to trigger the unit tests. The advantage of this is that we can add this very easily in any CI/CD pipeline.
