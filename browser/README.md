## Setting up the CoreLex browser site

To create a CoreLex browser you need to do the following:

1. Create the database tables
2. Create a database
3. Upload the browser to a server
4. Configure access to the database

These notes concentrate on steps 2 through 4, for creating the database tables refer to the [legacy](../legacy/README.md) pages in this repository.


#### Create a database

How to do this depends on your host set up. For the browser at http://www.timeml.org/corelex/browser/ we have used MySQL and the instructions here assume MySQL and phpMyAdmin, but the essentials are the same for other relational databases and tools.

Create a database named `corelex-browser` or any other name you desire. Use the `utf8mb4` character set and the `utf8mb4_bin` collation, although with WordNet you may probably get a way with the `latin1` defaults.

Import the file `schema.sql` or cut and paste the contents into the phpMyAdmin SQL tab. Do the same with the three SQL files that contain the data (`corelex_nouns.basictypes.sql`, `corelex_nouns.classes.sql` and `corelex_nouns.sql`, as created by the code in the `legacy` directory). The last file may be too large for an import, if so, first try to gzip the file and if that still results in too large a file you need to ftp the file to the server and do a local import.

```
 mysql -u <USER_NAME> -p -D <DATABASE_NAME> < corelex_nouns.sql
 ```

#### Upload the browser to a server

Put the `browser` directory with all its contents on the server either by uploading and unpacking an archive or by using git:

```
$ git clone https://github.com/marcverhagen/corelex
```


#### Configure access to the database

Copy the file `connection-sample.php` to `connection.php` and edit the contents as required by the host.
