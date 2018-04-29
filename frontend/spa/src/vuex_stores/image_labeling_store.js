
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
            commit(SET_INPUT_DATA_ID, input_data_id)
        },
        async get_input_data_id_of_unlabeled_image ({ commit }, label_task_id) {
            let input_data_id = await getLatestLabeledImage(label_task_id);

            commit(SET_INPUT_DATA_ID, input_data_id)
        },
        async get_input_data_id_of_most_recently_labeled_image ({ commit }) {

        },
        async get_input_data_id_of_previous_labeled_image ({ commit, getters }, label_task_id) {
            let input_data_id = await getPrecedingLabeledImage(getters.input_data_id, label_task_id)

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


// utility functions

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

                console.log(preceding_data_item)

                return preceding_data_item.input_data_id;
            }
            else {
                console.log('errrrror!')
                return undefined;
            }
        })
        .catch(function(error) {
            console.log(error);
            return undefined;
        });
}