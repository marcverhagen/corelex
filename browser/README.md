### Setting up the CoreLex browser site

To create the browser you need to do the following:

1. Create the database tables. There is code to do this which will be added to this repository, but part of it requires local access to the old static CoreLex Browser site on the Brandeis Computer Science server. Since CoreLex is built mostly automatically from WordNet these static files could be created directly from WordNet, but this has not been done yet.

2. Create a database, upload the schema and populate the tables. How to do this depends on your host set up. We have used MySQL.

3. Put the `browser` directory with all its contents on a server.

4. Copy the file `config-default.txt` to `config.txt` and edit the contents as required by the host.
