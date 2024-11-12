# fall24-monday-team5

## Main Branch
Build status: [![Build Status](https://app.travis-ci.com/gcivil-nyu-org/fall24-monday-team5.svg?token=gZFLquVHo7ZPGVRcsxqJ&branch=main)](https://app.travis-ci.com/gcivil-nyu-org/fall24-monday-team5)

Coverage Report: [![Coverage Status](https://coveralls.io/repos/github/gcivil-nyu-org/fall24-monday-team5/badge.svg?branch=main)](https://coveralls.io/github/gcivil-nyu-org/fall24-monday-team5?branch=main)

Website Link: [Prod Deployment](http://django-env3.eba-vbtmdwcq.us-east-1.elasticbeanstalk.com/)

## Develop Branch
Build status: [![Build Status](https://app.travis-ci.com/gcivil-nyu-org/fall24-monday-team5.svg?token=gZFLquVHo7ZPGVRcsxqJ&branch=develop)](https://app.travis-ci.com/gcivil-nyu-org/fall24-monday-team5)

Coverage Report: [![Coverage Status](https://coveralls.io/repos/github/gcivil-nyu-org/fall24-monday-team5/badge.svg?branch=develop)](https://coveralls.io/github/gcivil-nyu-org/fall24-monday-team5?branch=develop)

Website Link: [Develop deployment](http://django-env2.eba-hv2zpdfp.us-east-1.elasticbeanstalk.com/)
# Calm Seek

Welcome to the project repository! Please follow the guidelines below to maintain consistency and ensure a smooth development process.

## Branches Importance

### Master Branch
- The `master` branch contains the code that is deployed to **production**.
- **No one** can push to this branch directly from their local environment.
- All production-ready code must pass through a pull request and be reviewed before being merged into `master`.
- This branch will be used primarily for **demo purposes**.

### Develop Branch
- The `develop` branch contains code that will be deployed to the **staging** environment.
- All feature branches should be merged into `develop` through a pull request after testing and approval.

## Branch Naming Convention on Local

When creating a new branch on your local machine, please use the following naming convention:

```<issue_no>-<yourname>```

- `<issue_no>`: The issue number corresponding to the task you are working on. This can be obtained from the Zenhub list of issues.
- `<yourname>`: The name of the person primarily working on this branch.

Example: `1-xyz`
1 - the issue number
xyz - Name of person working on the branch

### Notes:
- All local branches must be branched from the `develop` branch.
- Create pull requests to merge your feature branches into `develop` after completing your work and ensuring it passes all necessary tests.


## How to setup a pre-commit hook

**NOTE:** All of the steps down below are assuming that you're in the root directory of the repository.

- create a file called `pre-commit`

```sh

$ touch ./.git/hooks/pre-commit

```

- add the following code to it:

you can use `vim` or `nano` (preferred) to add the code
replace the `myvenv` with the environment name you have created

```sh

#!/bin/sh

ROOT_DIR=$(git rev-parse --show-toplevel)
source $ROOT_DIR/myvenv/bin/activate

black . # this is the code formatter (very opinionated)

pylint $ROOT_DIR/calmseek/calmseek/
# we'll need to keep adding all of the modules that we
# want linted to the command above

deactivate

```

- make the `pre-commit` file executable

```sh

$ chmod +x ./.git/hooks/pre-commit

```

- start making your commits!


## Working with dummy data on local

Django provides something known as fixtures, which we can use to insert dummy data into our database for the models we have prepared.

The dummy data for appointments app is in the: `BASE_DIR/appointments/fixtures/`, in the `dummy_data.json` file.

To load this dummy data into your database, use:
```sh
$ python manage.py loaddata appointments/fixtures/dummy_data.json
```

## Django Superuser Info

- username: `calmseek-admin`
- password: ask me (@aryanprasad7)