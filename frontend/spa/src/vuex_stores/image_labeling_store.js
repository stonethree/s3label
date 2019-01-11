import { getLatestLabeledImage, 
         getPrecedingLabeledImage, 
         getFollowingLabeledImage, 
         getUnlabeledImage,
         getPrecedingLabeledImageFiltered, 
         getFirstLabeledImageFiltered,
         getFollowingLabeledImageFiltered,
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
            commit(SET_UNLABELED_IMAGES_AVAILABLE, true);
            commit(SET_PREVIOUS_IMAGES_AVAILABLE, true);
        },
        
        async change_filter({ commit }) {
            console.log('Cleared ids after filter changed')
            commit(CLEAR_INPUT_DATA_ID);
            commit(CLEAR_LABEL_ID);
            commit(SET_UNLABELED_IMAGES_AVAILABLE, true);
            commit(SET_PREVIOUS_IMAGES_AVAILABLE, true);
        }, 

        async previous_image ({ commit, getters, dispatch }, payload) {
            
            var label_task_id = payload.task_id;
            var label_filter = payload.label_filter;

            console.log('getting previous image')

            var input_data_id = undefined;
            var label_id = undefined;

            switch(label_filter){
                case "filter_all":
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
                    break;
                    
                case "filter_complete":
                case "filter_incomplete":
                    if (getters.input_data_id == undefined) {
                        console.log(label_filter + ' - getting image:', input_data_id, label_id)
                        let data = await getFirstLabeledImageFiltered(label_task_id, label_filter);
                        if (data != undefined) {
                            input_data_id = data.input_data_id;
                            label_id = data.label_id;
                        }
                    }
                    else {
                        console.log(label_filter + ' - getting image:', input_data_id, label_id)
                        let next_data = await getPrecedingLabeledImageFiltered(getters.label_id, label_task_id, label_filter);
                        if (next_data != undefined) {
                            input_data_id = next_data.input_data_id;
                            label_id = next_data.label_id;
                        }
                    }
                    break;
                    
                default:
                    console.log(label_filter + ' not implemented yet.')
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

        //async next_image ({ commit, getters, dispatch }, label_task_id) {
        async next_image ({ commit, getters, dispatch }, payload) {

            var label_task_id = payload.task_id;
            var label_filter = payload.label_filter;

            var input_data_id = undefined;
            var label_id = undefined;

            switch(label_filter){
                case "filter_all":
                    console.log('ALL: getting next image')
                    // First look for all the labeled images
                    console.log('input_data_id '+getters.input_data_id)
                    if (getters.input_data_id != undefined) {
                        let next_data = await getFollowingLabeledImage(getters.input_data_id, label_task_id);

                        if (next_data != undefined) {
                            input_data_id = next_data.input_data_id;
                            label_id = next_data.label_id;
                        }
                    }
                    // if no next image found, request a new unlabeled image for the user to label
                    if (input_data_id == undefined) {
                        console.log('All: getting next image2:', input_data_id, label_id)
                        let data = await getUnlabeledImage(label_task_id);
                        if (data != undefined) {
                            input_data_id = data.input_data_id;
                            label_id = data.label_id;
                        }
                    }
                    break;
                    
                case "filter_complete":
                case "filter_incomplete":
                    if (getters.input_data_id == undefined) {
                        console.log(label_filter + ' - getting image: ', input_data_id, label_id)
                        let data = await getFirstLabeledImageFiltered(label_task_id, label_filter);
                        if (data != undefined) {
                            input_data_id = data.input_data_id;
                            label_id = data.label_id;
                        }
                    }
                    else {
                        console.log(label_filter + ' - getting image: ', input_data_id, label_id)
                        let next_data = await getFollowingLabeledImageFiltered(getters.label_id, label_task_id, label_filter);
                        if (next_data != undefined) {
                            input_data_id = next_data.input_data_id;
                            label_id = next_data.label_id;
                        }
                    }
                    break;
                    
                default:
                    console.log(label_filter + ' not implemented yet.')
            }

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
