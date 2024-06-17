# Build:
# docker build -t mysql-ccdb .
# Run
# docker run -d -p 3306:3306 --name mysql-ccdb-container mysql-ccdb
# The -p option takes two values: the first is the host port you want to bind to,
# and the second is the container port you want to expose.
# Since MySQL typically runs on port 3306, you might want to bind this port to a port on your host machine.
# -d runs the container in detached mode, meaning it runs in the background.
# -p 3306:3306 binds port 3306 on the host to port 3306 on the container

# Use Ubuntu as the base image
FROM ubuntu:latest

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install MySQL Server and other packages
RUN apt-get update && \
    apt-get install -y mysql-server gcc gdb g++ cmake build-essential libsqlite3-dev mysql-client libmysqlclient-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Setup database and user, and import the initial database schema
COPY ccdb.mysql.sql /tmp/ccdb.mysql.sql

RUN service mysql start && \
    mysql -e "CREATE DATABASE test_ccdb;" && \
    mysql -e "CREATE USER 'test_ccdb'@'localhost';" && \
    mysql -e "GRANT ALL PRIVILEGES ON test_ccdb.* TO 'test_ccdb'@'localhost';" && \
    mysql -e "FLUSH PRIVILEGES;" &&\
    mysql -u test_ccdb test_ccdb < /tmp/ccdb.mysql.sql

# CCDB_TEST_MYSQL_CONNECTION
# Copy your SQL file into the container



# Fill the database using the SQL file
#RUN service mysql start && \
#    mysql test_ccdb < /tmp/ccdb.mysql.sql

# Persist MySQL data in a volume
# VOLUME ["/var/lib/mysql"]

# Expose the MySQL port
EXPOSE 3306

# Optimized ENTRYPOINT for initialization and starting mysqld_safe
ENTRYPOINT ["/usr/bin/mysqld_safe"]

# Use CMD instead of ENTRYPOINT to ensure MySQL starts in the foreground
CMD ["mysqld_safe"]
