# ssci
### Shit&amp;Sticks CI

Little CLI tool to poll for changes in remote git repo, pull and run any commad after update.

Also it can run as a daemon docker container that continuosly does exactly the same.

## Usage

To configure new project, run `ssci new`. It will interactively ask you for repo url, branch to use and so on.

This config will be saved into `ssci.yaml` file, that you can change later via cli or manually
Project parameters are:
- `repo_url`: url to git repository
- `build_cmd`: command to run after each pull. It should stop previous instances if needed, for example "docker-compose up -d --build --remove-orphans" if you use compose
- `branch`: git branch to track
- `project_name`: uummm you can guess this one
- `add_dir`: directory with additional files, that should be copied after clone (for example, .env file with secrets)
- `dind`: enable dind for build (needed if you use docker/compose for build)
- `checks`: list of checks needed to start build after each pull (for example, wait for gitlab pipelene to succeed)
- `key_file`: deploy secret key file for github
- `build_detached`: set to true if your build command blocks
- `build_detched_timeout`: time to wait on detached build to confirm successfull startup

Then, run `ssci dc start` to run ssci docker daemon

### Other features

#### Notifiacations
You can add target for notifications with interactive `ssci notification`

As of 0.2.0, only telegram implemented

#### Github authorization
Easy configure github token with `ssci github` commands
- `gen`    Generate new pair of keys for project
- `patch`  Add github key to SSH config
- `pub`    Print projets public key

#### Checks
Add new check with `ssci addcheck`
As of 0.2.0, only github pipeline check implemented

#### Manual rebuild
Run `ssci rebuild <project>` to trigger manual rebuild
