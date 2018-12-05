# Keeping track of payments

Once users have labeled data and marked their labeling as *complete*, and an admin user has approved the labeling, we can record in the database that payments have been made for this batch of labeled data.

This is currently done using SQL commands, since we have not yet created a UI to do this via the front-end.

We begin by marking the *paid* field true for the labels that have been approved:

~~~ SQL
update labels set paid=true where admin_complete=true and paid=FALSE and payment_date is not null
~~~

Then, to display a summary of the payment numbers that we will query the *payments_owed* view to see a payment summary:

~~~ SQL
select * from payments_owed where payment_date is null
~~~

Export this table to a Google Sheet, Excel, etc as needed.

Then set the *payment_date* field of these labels:

~~~ SQL
update labels set payment_date=now() where paid=true and payment_date is null
~~~

We can then make the payments to the users in any way we see fit.
