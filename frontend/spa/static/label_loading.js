import axios from "axios";

var baseUrl = process.env.API_ADDR;
axios.defaults.baseURL = baseUrl;


// static functions for retrieving input_data_ids from backend


export async function getLatestLabeledImage(label_task_id) {
    // get the input_data_id of the latest image that the user has labeled

    let access_token = localStorage.getItem("s3_access_token");

    let config = {
        headers: {
        Authorization: "Bearer " + access_token
        }
    };

    return await axios
        .get("all_data/label_tasks/" + label_task_id + "/users/own?num_labeled_images=1", config)
        .then(function(response) {
            if (response.data.length == 1) {
                let data = {
                    input_data_id: response.data[0].input_data_id,
                    label_id: response.data[0].label_id
                };

                console.log(data)

                return data;
            }
            else {
                return undefined;
            }
        })
        .catch(function(error) {
            console.log(error);
            return undefined;
        });
}

export async function getPrecedingLabeledImage(current_input_data_id, label_task_id) {
    // get preceding labeled image

    let access_token = localStorage.getItem("s3_access_token");

    let config = {
        headers: {
        Authorization: "Bearer " + access_token
        }
    };

    return await axios
        .get("labeled_data/label_tasks/" + label_task_id + "?action=previous&current_input_data_id=" + current_input_data_id, config)
        .then(function(response) {
            if (response.data.length == 1) {
                var preceding_data_item = response.data[0];

                return preceding_data_item;
            }
            else {
                return undefined;
            }
        })
        .catch(function(error) {
            console.log(error);
            return undefined;
        });
}


export async function getFollowingLabeledImage(current_input_data_id, label_task_id) {
    // get following labeled image that has already been

    let access_token = localStorage.getItem("s3_access_token");

    let config = {
        headers: {
        Authorization: "Bearer " + access_token
        }
    };

    return await axios
        .get("labeled_data/label_tasks/" + label_task_id + "?action=next&current_input_data_id=" + current_input_data_id, config)
        .then(function(response) {
            if (response.data.length == 1) {
                var following_data_item = response.data[0];

                return following_data_item;
            }
            else {
                return undefined;
            }
        })
        .catch(function(error) {
            console.log(error);
            return undefined;
        });
}


export async function getUnlabeledImage(label_task_id) {
    // get a new image that the user has not already labeled

    let access_token = localStorage.getItem("s3_access_token");

    let config = {
        headers: {
        Authorization: "Bearer " + access_token
        }
    };

    return await axios
        .get("unlabeled_images/label_tasks/" + label_task_id + "?shuffle=true", config)
        .then(function(response) {
            var following_data_item = response.data;
            console.log('unlabeled data:', following_data_item)
            return following_data_item;
        })
        .catch(function(error) {
            console.log(error);
            return undefined;
        });
}


// static functions for retrieving labels from backend


function checkLabelFormatValid(polygons) {
    // check that the labels are of the correct format to load

    if (polygons != undefined) {
        if (polygons.length > 0 && polygons[0].polygon != undefined) {
            return true;
        }
        else if (polygons.length == 0) {
            return true;
        }
    }
    
    return false;
}


export async function uploadLabels(input_data_id, label_task_id, polygons) {

    console.log('uploading label with label task ID', label_task_id, 'and input data ID', input_data_id)

    if (label_task_id == undefined || input_data_id == undefined) {
        console.log("Error: Input fields must all be defined in order to upload label:" + label_task_id + input_data_id)
    }
    else if (polygons.length == 0) {
        console.error('Polygons object should (probably) not be empty when uploading! Not uploading item.');
    }
    else {
        var data = {label_serialised: polygons}

        let access_token = localStorage.getItem("s3_access_token");

        let config = {
            headers: {
            Authorization: "Bearer " + access_token
            }
        };

        await axios
            .post("label_history/label_tasks/" + label_task_id + "/input_data/" + input_data_id, data, config)
            .then(function(response) {
                console.log('saved label:', label_task_id, input_data_id, response)
            })
            .catch(function(error) {
                console.error('error saving label:' + error + ', input_data_id:' + input_data_id + ', label_task_id:' + label_task_id + ', polygons:' + polygons);
            });
    }
}

export async function loadLabels(input_data_id, label_task_id) {

    console.log('getting image labels with label task ID', label_task_id, 'and input data ID', input_data_id)

    if (label_task_id == undefined || input_data_id == undefined) {
        console.error("Input fields must all be defined in order to load label")
    }
    else {

        let access_token = localStorage.getItem("s3_access_token");

        let config = {
            headers: {
            Authorization: "Bearer " + access_token
            }
        };

        return await axios
            .get("labels/input_data/" + input_data_id + "/label_tasks/" + label_task_id, config)
            .then(function(response) {
                if (response.data.length == 1) {
                    console.log("Label found for this image. Attempting to apply it in the view", response.data)
                    var label = response.data[0];

                    // check label format is correct

                    var polygons = JSON.parse(label.label_serialised);

                    if (polygons == null) {
                        polygons = [];
                    }

                    if (checkLabelFormatValid(polygons)) {
                        console.log('Applied serialised label to image')
                        return polygons;
                    }
                    else {
                        console.error('Serialised label has wrong format:' + polygons)
                    }
                }
                else if (response.data.length == 0) {
                    console.error("No label found for this image")
                }
                else {
                    console.error("Error: expected at most one label for this image!")
                }
            })
            .catch(function(error) {
                console.error(error);
                return undefined;
            });
    }
}

export async function getLabelId(label_task_id, input_data_id, user_id) {
    // get the label ID, given user ID, label task ID and input data ID

    if (label_task_id == undefined || input_data_id == undefined || user_id == undefined) {
        console.error("Input fields must all be defined in order to get the label ID")
    }
    else {
        let access_token = localStorage.getItem("s3_access_token");

        let config = {
            headers: {
            Authorization: "Bearer " + access_token
            }
        };

        return await axios
            .get("label_ids/label_tasks/" + label_task_id + "/input_data/" + input_data_id + "/user/" + user_id, config)
            .then(function(response) {
                console.log('dfdgff', response.data, 'user_id:', user_id, 'input_data_id:', input_data_id, 'label_task_id:', label_task_id, 'label_id:', response.data.label_id)
                return response.data.label_id;
            })
            .catch(function(error) {
                console.log('error getting label id:', error);
                return undefined;
            });
    }
}
