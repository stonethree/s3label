# Uploading images for labeling

In order to label new images using S3Label, you will need to first need to place the images on the S3Label server.
You will then need to create a *dataset* to upload images to. 
Once you have a *dataset*, you can upload images to this dataset via the Admin page in S3Label. 
To then make the images available for labeling, you will then need to create a *dataset group*, which will contain the *dataset* that you just created. create a *label task*

1. Copy images to the S3Label server harddrive
    
    **Tip**: Ideally choose a location that is fairly permanent. When you *upload* images you will merely be uploading the absolute paths to these files on disk. S3Label will not create another copy of the image data itself.

    You may choose to use images mounted from a cloud blob store, such as Amazon S3 or Azure Blob store, or maybe using a tool such as [DVC](https://dvc.org/) for storing all your machine learning training data. This is entirely up to you.
    
1. In order to import new images for labeling, you will first need to create a *dataset* to upload images to:

    ~~~ SQL
    INSERT INTO datasets(site, sensor, dataset_description) VALUES ('Cape Town', 'hot air balloon camera', 'This is an dataset of aerial images collected from a hot air balloon');
    ~~~
   
    *Assume for this example that this *dataset* was created with a *dataset_id* 6.*
    
1. You will then upload images to this dataset via the browser interface:
    1. Log into S3Label as an admin user
    1. Go to the *Admin* page
    1. Go to the *Upload Input Data* tab
    1. Select the *dataset* to which you want to upload images.
    1. Enter the path to the directory that contains the images on the S3Label server.
    1. Click either *Find images in folder* or *Find images in folder recursively* to list all the image files in this folder.
        
        If choosing the recursive option, it will look for images in subfolders too.
        
    1. Select/deselect images that you wish to upload. You can view the image by clicking the path.
    1. Click *Upload selected images*
    
        This will generate entries in the *Input Data Items* table in the database. 
        It will store the paths to all the images and create unique IDs and hashes of the images.

1. Create a *dataset group* to contain the *dataset* and assign to a *label task* for labeling:

    We often want to aggregate multiple *datasets* together and create a single *label task* to the whole group of *datasets*.
    
    1. Create a *dataset_group*:
    
        ~~~ SQL
        INSERT INTO dataset_groups(name, description) VALUES ('Hot air balloon datasets', 'All aerial images captured from hot air balloons');
        ~~~ 
       
        *Assume for this example that this *dataset_group* was created with a *dataset_group_id* 3.*
       
    1. Create a *dataset_group_list* entry to link a *dataset* to a *dataset_group*:
    
        ~~~ SQL
        INSERT INTO dataset_group_lists(dataset_group_id, dataset_id) VALUES (3, 6);
        ~~~ 
       
    1. Create a *label_task* entry to link a *dataset* to a *dataset_group*:
    
        ~~~ SQL
        INSERT INTO label_tasks(dataset_group_id, title, description, type) VALUES (3, 'Aerial house labeling', 'Draw bounding boxes around each house in each image', 'instance_segmentation');
        ~~~ 
       
        *Assume for this example that this *label_task* was created with a *label_task_id* 4.*
        
1. Assign user(s) to this label task: 

    Here is an example of assigning user 1 to label task 4:
    ~~~ SQL
    INSERT INTO users_label_tasks (user_id, label_task_id) VALUES (1, 4);
    ~~~
   
The user(s) should now be able to view the label task and label images.
