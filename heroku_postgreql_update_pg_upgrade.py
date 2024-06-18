import subprocess
import time

#This a postgresql heroku db version update using pg:upgrade method
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        exit(result.returncode)
    return result.stdout.strip()

def provision_follower_db(app_name, old_db_url, version=None):
    command = f"heroku addons:create heroku-postgresql:standard-0 --follow {old_db_url} --app {app_name}"
    if version:
        command += f" --version {version}"
    result = run_command(command)
    # Extract the follower DB URL from the command output
    follower_db_url = [line for line in result.split("\n") if "Attached as" in line][0].split(" ")[-1]
    return follower_db_url

def enter_maintenance_mode(app_name):
    command = f"heroku maintenance:on -a {app_name}"
    run_command(command)

def upgrade_follower_db(follower_db_url, app_name):
    command = f"heroku pg:upgrade {follower_db_url} --app {app_name}"
    run_command(command)
    wait_for_db_upgrade(app_name)

def wait_for_db_upgrade(app_name):
    command = f"heroku pg:wait --app {app_name}"
    print("Waiting for database upgrade to complete...")
    run_command(command)
    print("Database upgrade completed.")

def promote_new_db(follower_db_url, app_name):
    command = f"heroku pg:promote {follower_db_url} --app {app_name}"
    run_command(command)

def exit_maintenance_mode(app_name):
    command = f"heroku maintenance:off -a {app_name}"
    run_command(command)

def deprovision_old_db(old_db_url, app_name):
    command = f"heroku addons:destroy {old_db_url} --app {app_name} --confirm {app_name}"
    run_command(command)

def main():
    app_name = "example-app"
    old_db_url = "HEROKU_POSTGRESQL_OLD_URL"
    new_db_version = "13"  # Specify the desired version

    print("Provisioning a follower database...")
    follower_db_url = provision_follower_db(app_name, old_db_url, version=new_db_version)

    print("Entering maintenance mode...")
    enter_maintenance_mode(app_name)

    print("Upgrading the follower database...")
    upgrade_follower_db(follower_db_url, app_name)

    print("Promoting the new database...")
    promote_new_db(follower_db_url, app_name)

    print("Deprovisioning the old primary database...")
    deprovision_old_db(old_db_url, app_name)

    print("Exiting maintenance mode...")
    exit_maintenance_mode(app_name)

    print("Database upgrade completed successfully.")

if __name__ == "__main__":
    main()
