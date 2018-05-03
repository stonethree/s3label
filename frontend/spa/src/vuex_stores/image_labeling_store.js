import { getLatestLabeledImage, 
         getPrecedingLabeledImage, 
         getFollowingLabeledImage, 
         getUnlabeledImage,
         } from '../../static/label_loading'


// NB: for now we will not include the label ID and polygons in the vuex states, however it would be good to include it later when handling undo/redo etc
// Moreover, there is currently a bug that occurs when the user presses left/right arrow keys too quickly through the images in the image labeler page. In
// this situation, it appears that the multiple asynchronous calls (ie. switching images) are being dispatched too quickly in succession, which causes them
// to result in weird clearing of polygons. To remedy this, either the polygons objects and label IDs etc should be moved to a Vuex store, or have a Vuex flag
// that prevents input_data_id changes until finished handling the request. However, this will add coupling between image labeler and drawing canvas components,
// so maybe best to just use Vuex store for all the variables and then perform atomic mutations.


export const SET_INPUT_DATA_ID = 'set_input_data_id'; 
export const CLEAR_INPUT_DATA_ID = 'clear_input_data_id'; 
 
export const StoreImageLabeling = {
    namespaced: true,
    state: {
        input_data_id: undefined,
    },
    mutations: {
        [SET_INPUT_DATA_ID] (state, input_data_id) {
            state.input_data_id = input_data_id;
        },
        [CLEAR_INPUT_DATA_ID] (state) {
            state.input_data_id = undefined;
        }
    },
    actions: {
        // actions for requesting input_data_ids

        async set_input_data_id_of_existing_image ({ commit }, input_data_id) {
            // console.log('set_input_data_id_of_existing_image:::::::::1 ', input_data_id)
            commit(SET_INPUT_DATA_ID, input_data_id)
        },
        async clear_input_data_id ({ commit }) {
            // console.log('set_input_data_id_of_existing_image:::::::::1 ', input_data_id)
            commit(CLEAR_INPUT_DATA_ID)
        },
        async get_input_data_id_of_most_recently_labeled_image ({ commit }, label_task_id) {
            let input_data_id = await getLatestLabeledImage(label_task_id);

            // console.log('get_input_data_id_of_most_recently_labeled_image:::::::::2 ', input_data_id)

            commit(SET_INPUT_DATA_ID, input_data_id)
        },
        async get_input_data_id_of_previous_labeled_image ({ commit, getters }, label_task_id) {
            let input_data_id = await getPrecedingLabeledImage(getters.input_data_id, label_task_id)

            // console.log('get_input_data_id_of_previous_labeled_image:::::::::3 ', input_data_id)

            if (input_data_id != undefined) {
                commit(SET_INPUT_DATA_ID, input_data_id)
            }
        },
        async get_input_data_id_of_next_image ({ commit, getters }, label_task_id) {
            // console.log('get_input_data_id_of_next_image:::::::::4 ')
            var input_data_id = undefined;

            // firstly, check if the user has labeled another image following the current one

            if (getters.input_data_id != undefined) {
                input_data_id = await getFollowingLabeledImage(getters.input_data_id, label_task_id)
                // console.log('getFollowingLabeledImage (A) ', input_data_id)
            }

            // if no next image found, request a new unlabeled image for the user to label

            if (input_data_id == undefined) {
                input_data_id = await getUnlabeledImage(label_task_id)
                // console.log('getUnlabeledImage (B) ', input_data_id)
            }

            if (input_data_id != undefined) {
                commit(SET_INPUT_DATA_ID, input_data_id)
            }
        },
    },
    getters: {
        input_data_id: state => {
            return state.input_data_id;
        }
    }
}
