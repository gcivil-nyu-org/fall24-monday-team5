# fall24-monday-team5

# Calm Seek

Welcome to the project repository! Please follow the guidelines below to maintain consistency and ensure a smooth development process.

## Branches Importance

### Master Branch
- The `master` branch contains the code that is deployed to **production**.
- **No one** can push to this branch directly from their local environment.
- All production-ready code must pass through a pull request and be reviewed before being merged into `master`.

### Develop Branch
- The `develop` branch contains code that will be deployed to the **staging** environment.
- This branch will be used primarily for **demo purposes**.
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