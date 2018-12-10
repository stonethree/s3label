## Useful SQL queries

Delete duplicate input_data items from a particular dataset that has just been uploaded:

~~~ SQL
BEGIN;

delete from input_data i using duplicate_input_data d where i.input_data_id = d.input_data_id and i.dataset_id = 17 and i.timestamp_upload is not null;

select * from input_data where dataset_id = 17;

--rollback, so that we can test the query before executing (i.e. perform a dry run)
ROLLBACK;
~~~
