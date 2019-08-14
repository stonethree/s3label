# Upgrading S3Label version

If you have installed an older version of S3Label and would like to upgrade to a newer version without losing previously labeled data, perform the following steps.

## Migrate database

1. Ensure Postgres database is backed up.

    Test the backup is working correctly before risking proceeding (I would advise actually restoring the latest backup to a new database on your local machine and confirming that all the data is there).

1. Apply migrations to database to create and remove columns that differ between old version and new version.

    * Use [migra](https://djrobstep.com/docs/migra) to generate a file of SQL commands required to change the original database schema into the new schema.
    * Run the generated SQL file to apply migrations
    
        Ideally do this with a copy of the original database to prevent accidents.

1. Check data consistency

    Run SQL queries or view data in some of the Postgres views (e.g. label_task_counts or payments_owed, which depend on many different tables and so will show a change if any of the underlying tables have altered).
    
## Update front-end and back-end

1. Replace S3Label code wherever it has been installed to on the server
1. Restart front-end and back-end servers

    See [this page](installation.md) for more info.
