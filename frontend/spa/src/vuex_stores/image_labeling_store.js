
export const SET_INPUT_DATA_ID = 'set_input_data_id';
export const SET_LABEL_ID = 'set_label_id';
 
export const StoreImageLabeling = {
    namespaced: true,
    state: {
        input_data_id: undefined,
        label_id: undefined,
    },
    mutations: {
        [SET_INPUT_DATA_ID] (state, input_data_id) {
            state.input_data_id = input_data_id;
        },
        [SET_LABEL_ID] (state, label_id) {
            state.label_id = label_id;
        },
    },
    actions: {
        async set_input_data_id_of_existing_image ({ commit }, input_data_id) {
            console.log('set_input_data_id_of_existing_image:::::::::1 ', input_data_id)
            commit(SET_INPUT_DATA_ID, input_data_id)
        },
        async get_input_data_id_of_most_recently_labeled_image ({ commit }, label_task_id) {
            let input_data_id = await getLatestLabeledImage(label_task_id);

            console.log('get_input_data_id_of_most_recently_labeled_image:::::::::2 ', input_data_id)

            commit(SET_INPUT_DATA_ID, input_data_id)
        },
        async get_input_data_id_of_previous_labeled_image ({ commit, getters }, label_task_id) {
            let input_data_id = await getPrecedingLabeledImage(getters.input_data_id, label_task_id)

            console.log('get_input_data_id_of_previous_labeled_image:::::::::3 ', input_data_id)

            if (input_data_id != undefined) {
                commit(SET_INPUT_DATA_ID, input_data_id)
            }
        },
        async get_input_data_id_of_next_image ({ commit, getters }, label_task_id) {
            console.log('get_input_data_id_of_next_image:::::::::4 ')
            var input_data_id = undefined;

            // firstly, check if the user has labeled another image following the current one

            if (getters.input_data_id != undefined) {
                input_data_id = await getFollowingLabeledImage(getters.input_data_id, label_task_id)
                console.log('getFollowingLabeledImage (A) ', input_data_id)
            }

            // if no next image found, request a new unlabeled image for the user to label

            if (input_data_id == undefined) {
                input_data_id = await getUnlabeledImage(label_task_id)
                console.log('getUnlabeledImage (B) ', input_data_id)
            }

            if (input_data_id != undefined) {
                commit(SET_INPUT_DATA_ID, input_data_id)
            }
        },
    },
    getters: {
        input_data_id: state => {
            return state.input_data_id;
        },
        label_id: state => {
            return state.label_id;
        }
    }
}


// static functions for retrieving input_data_ids from backend

import axios from "axios";

var baseUrl = "http://127.0.0.1:5000/image_labeler/api/v1.0";
axios.defaults.baseURL = baseUrl;

async function getLatestLabeledImage(label_task_id) {
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
                let input_data_id_latest = response.data[0].input_data_id;

                return input_data_id_latest;
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

async function getPrecedingLabeledImage(current_input_data_id, label_task_id) {
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

                return preceding_data_item.input_data_id;
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


async function getFollowingLabeledImage(current_input_data_id, label_task_id) {
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

                return following_data_item.input_data_id;
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


async function getUnlabeledImage(label_task_id) {
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
            console.log(response.data, response.data.length)

            var following_data_item = response.data;
            console.log(following_data_item.input_data_id)
            return following_data_item.input_data_id;
        })
        .catch(function(error) {
            console.log(error);
            return undefined;
        });
}
