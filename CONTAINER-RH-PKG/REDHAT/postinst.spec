%post
#!/bin/bash

printf "\n* Container postinst...\n" | tee -a /dev/tty

printf "\n* Building podman image...\n" | tee -a /dev/tty
cd /usr/lib/api-vmware

# Build container image.
buildah bud -t api-vmware . | tee -a /dev/tty

printf "\n* The container will start in few seconds.\n\n"

function containerSetup()
{
    wallBanner="RPM automation-interface-api-vmware-container post-install configuration message:\n"
    cd /usr/lib/api-vmware

    # First container run: associate name, bind ports, bind fs volume, define init process, ...
    # api-vmware folder will be bound to /var/lib/containers/storage/volumes/.
    podman run --name api-vmware -v api-vmware:/var/www/api/api -v api-vmware-db:/var/lib/mysql -v api-vmware-cacerts:/usr/local/share/ca-certificates -dt localhost/api-vmware /sbin/init
    podman exec api-vmware chown www-data:www-data /var/www/api/api # within container.

    podman exec api-vmware chown mysql:mysql /var/lib/mysql # within container.
    podman exec api-vmware systemctl restart mysql

    printf "$wallBanner Starting Container Service on HOST..." | wall -n
    systemctl daemon-reload

    systemctl start automation-interface-api-vmware-container # (upon installation, container is already run).
    systemctl enable automation-interface-api-vmware-container

    printf "$wallBanner Configuring container..." | wall -n
    # Setup a Django secret key: using host-bound folders.
    djangoSecretKey=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)
    sed -i "s|^SECRET_KEY =.*|SECRET_KEY = \"$djangoSecretKey\"|g" /var/lib/containers/storage/volumes/api-vmware/_data/settings.py

    # Setup the JWT token public key (taken from SSO): using host-bound folders.
    cp -f /var/lib/containers/storage/volumes/sso/_data/settings_jwt.py /var/lib/containers/storage/volumes/api-vmware/_data/settings_jwt.py
    sed -i -e ':a;N;$!ba;s|\s*"privateKey.*}|\n}|g' /var/lib/containers/storage/volumes/api-vmware/_data/settings_jwt.py

    printf "$wallBanner Internal database configuration..." | wall -n
    if podman exec api-vmware mysql -e "exit"; then
        # User api.
        # Upon podman image creation, a password is generated for the user api.
        databaseUserPassword=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

        if [ "$(podman exec api-vmware mysql --vertical -e "SELECT User FROM mysql.user WHERE User = 'api';" | tail -1 | awk '{print $2}')" == "" ]; then
            # User api not present: create.
            echo "Creating api user..."
            podman exec api-vmware mysql -e "CREATE USER 'api'@'localhost' IDENTIFIED BY '$databaseUserPassword';"
            podman exec api-vmware mysql -e "GRANT USAGE ON *.* TO 'api'@'localhost' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
            podman exec api-vmware mysql -e 'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER, CREATE TEMPORARY TABLES, CREATE VIEW, SHOW VIEW, EXECUTE ON `api`.* TO `api`@`localhost`;'
            podman exec api-vmware mysql -e 'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER, CREATE TEMPORARY TABLES, CREATE VIEW, SHOW VIEW, EXECUTE ON `api`.* TO `stage2`@`localhost`;'
        else
            # Update user's password.
            echo "Updating api user's password..."
            podman exec api-vmware mysql -e "SET PASSWORD FOR 'api'@'localhost' = PASSWORD('$databaseUserPassword');"
        fi

        # Change database password into Django config file, too.
        echo "Configuring Django..."
        sed -i "s/^.*DATABASE_USER$/        'USER': 'api', #DATABASE_USER/g" /var/lib/containers/storage/volumes/api-vmware/_data/settings.py
        sed -i "s/^.*DATABASE_PASSWORD$/        'PASSWORD': '$databaseUserPassword', #DATABASE_PASSWORD/g" /var/lib/containers/storage/volumes/api-vmware/_data/settings.py

        # Database api.
        echo "Creating database api and restoring SQL dump..."
        if [ "$(podman exec api-vmware mysql --vertical -e "SHOW DATABASES LIKE 'api';" | tail -1 | awk -F': ' '{print $2}')" == "" ]; then
            podman exec api-vmware mysql -e 'CREATE DATABASE api DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;' # create database.
            podman exec api-vmware mysql api -e "source /var/www/api/vmware/sql/vmware.schema.sql" # restore database schema.
            podman exec api-vmware mysql api -e "source /var/www/api/vmware/sql/vmware.data.sql" # restore database data.
            podman exec api-vmware mysql -e 'CREATE DATABASE stage2 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;' # create database.
            podman exec api-vmware mysql stage2 -e "source /var/www/api/vmware/sql/stage2.schema.sql" # restore database schema.
        fi

        # Database update via diff.sql (migrations).
        echo "Applying migrations..."
        podman exec api-vmware bash /var/www/api/vmware/sql/migrate.sh

        # Activate mysql audit plugin.
        podman exec api-vmware bash -c "cp -p /usr/share/automation-interface-api/51-mariadb.cnf /etc/mysql/mariadb.conf.d"
    else
        echo "Failed to access MariaDB RDBMS, auth_socket plugin must be enabled for the database root user. Quitting."
        exit 1
    fi

    printf "$wallBanner Restarting container's services..." | wall -n
    podman exec api-vmware systemctl restart apache2
    podman exec api-vmware systemctl restart mariadb

    diffOutput=$(podman exec api-vmware diff /var/www/api_default_settings.py /var/www/api/api/settings.py | grep '^[<>].*' | grep -v SECRET | grep -v PASSWORD | grep -v VENV || true)
    if [ -n "$diffOutput" ]; then
        printf "$wallBanner Differences from package's stock config file and the installed one (please import NEW directives in your installed config file, if any):\n* $diffOutput" | wall -n
    fi

    # syslog-ng seems going into a catatonic state while updating a package: restarting the whole thing.
    if rpm -qa | grep -q automation-interface-log; then
        if systemctl list-unit-files | grep -q syslog-ng.service; then
            systemctl restart syslog-ng || true # on host.
            podman exec api-vmware systemctl restart syslog-ng # on this container.
        fi
    fi

    printf "$wallBanner Installation completed." | wall -n
}

systemctl start atd

{ declare -f; cat << EOM; } | at now
containerSetup
EOM

exit 0

