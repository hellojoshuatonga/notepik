REFERENCE:
    - http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-posgresql-for-django


COMMANDS USED:
    - sudo su - postgres -- Login as postgres user
    - psql - Database prompt
    - createdb databasename -- Create database
    - CREATE ROLE myusername WITH LOGIN PASSWORD 'mypassword'; -- psql command to create user for database
    - GRANT ALL PRIVILEGES ON DATABASE databasename TO myusername; -- psql command to grant privileges for user to dataabase
    - ALTER USER myusername CREATEDB; -- another psql command
    - ALTER DATABASE databasename OWNER TO myusername -- Change owner of the database to make ./manage reset_db work 
