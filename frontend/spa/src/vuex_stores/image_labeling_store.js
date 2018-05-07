import { getLatestLabeledImage, 
         getPrecedingLabeledImage, 
         getFollowingLabeledImage, 
         getUnlabeledImage,
         } from '../../static/label_loading'

import { uploadLabels,
         loadLabels,
         getLabelId } from '../../static/label_loading'


const SET_INPUT_DATA_ID = 'set_input_data_id'; 
const CLEAR_INPUT_DATA_ID = 'clear_input_data_id'; 
const SET_LABEL_ID = 'set_label_id'; 
const CLEAR_LABEL_ID = 'clear_label_id'; 
const SET_UNLABELED_IMAGES_AVAILABLE = 'set_unlabeled_images_available'; 
const SET_PREVIOUS_IMAGES_AVAILABLE = 'set_previous_images_available'; 
 
export const StoreImageLabeling = {
    namespaced: true,
    state: {
        input_data_id: undefined,
        label_id: undefined,
        unlabeled_images_available: true,
        previous_images_available: true,
    },
    mutations: {
        [SET_INPUT_DATA_ID] (state, input_data_id) {
            state.input_data_id = input_data_id;
        },
        [CLEAR_INPUT_DATA_ID] (state) {
            state.input_data_id = undefined;
        },
        [SET_LABEL_ID] (state, label_id) {
            state.label_id = label_id;
        },
        [CLEAR_LABEL_ID] (state) {
            state.label_id = undefined;
        },
        [SET_UNLABELED_IMAGES_AVAILABLE] (state, images_are_available) {
            state.unlabeled_images_available = images_are_available;
        },
        [SET_PREVIOUS_IMAGES_AVAILABLE] (state, images_are_available) {
            state.previous_images_available = images_are_available;
        }
    },
    actions: {
        async set_initial_image ({ commit, rootGetters }, input_data_id) {
            var label_task_id = rootGetters['label_task_store/label_task_id'];
            var user_id = rootGetters['user_login/user_id'];

            console.log('setting initial image');

            if (input_data_id != undefined) {
                var label_id = await getLabelId(label_task_id, input_data_id, user_id);

                if (label_id != undefined) {
                    commit(SET_INPUT_DATA_ID, input_data_id);
                    commit(SET_LABEL_ID, label_id);
                    return;
                }
            }

            // clear input_data_id and label_id 

            commit(CLEAR_INPUT_DATA_ID);
            commit(CLEAR_LABEL_ID);
        },

        async leave_page ({ commit }) {
            console.log('leaving page')
            commit(CLEAR_INPUT_DATA_ID);
            commit(CLEAR_LABEL_ID);
        },

        async previous_image ({ commit, getters, dispatch }, label_task_id) {

            console.log('getting previous image')

            var input_data_id = undefined;
            var label_id = undefined;

            if (getters.input_data_id == undefined) {
                let data = await getLatestLabeledImage(label_task_id);

                if (data != undefined) {
                    input_data_id = data.input_data_id;
                    label_id = data.label_id;
                }
            }
            else {
                let data = await getPrecedingLabeledImage(getters.input_data_id, label_task_id);

                if (data != undefined) {
                    input_data_id = data.input_data_id;
                    label_id = data.label_id;
                }
            }

            if (input_data_id != undefined && label_id != undefined) {
                commit(SET_INPUT_DATA_ID, input_data_id);
                commit(SET_LABEL_ID, label_id);
                commit(SET_UNLABELED_IMAGES_AVAILABLE, true);
                commit(SET_PREVIOUS_IMAGES_AVAILABLE, true);
            }
            else {
                commit(SET_PREVIOUS_IMAGES_AVAILABLE, false);
            }
        },

        async next_image ({ commit, getters, dispatch }, label_task_id) {

            console.log('getting next image')

            var input_data_id = undefined;
            var label_id = undefined;

            // firstly, check if the user has labeled another image following the current one

            if (getters.input_data_id != undefined) {
                let next_data = await getFollowingLabeledImage(getters.input_data_id, label_task_id);

                if (next_data != undefined) {
                    input_data_id = next_data.input_data_id;
                    label_id = next_data.label_id;
                }
            }

            console.log('getting next image2:', input_data_id, label_id)

            // if no next image found, request a new unlabeled image for the user to label

            if (input_data_id == undefined) {
                let data = await getUnlabeledImage(label_task_id);

                if (data != undefined) {
                    input_data_id = data.input_data_id;
                    label_id = data.label_id;
                }
            }

            console.log('getting next image3:', input_data_id, label_id)

            if (input_data_id != undefined && label_id != undefined) {
                commit(SET_INPUT_DATA_ID, input_data_id);
                commit(SET_LABEL_ID, label_id);
                commit(SET_UNLABELED_IMAGES_AVAILABLE, true);
                commit(SET_PREVIOUS_IMAGES_AVAILABLE, true);
            }
            else {
                // clear input_data_id and label_id

                commit(CLEAR_INPUT_DATA_ID);
                commit(CLEAR_LABEL_ID);
                commit(SET_UNLABELED_IMAGES_AVAILABLE, false);
            }
            console.log('completed function:', getters.input_data_id, getters.label_id)
        }
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
