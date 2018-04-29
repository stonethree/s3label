
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
        async set_new_image ({ commit }, input_data_id) {
            commit(SET_INPUT_DATA_ID, input_data_id)
            commit(SET_LABEL_ID, input_data_id*2)

            // attempting to log in. Can display a spinner during this period to notify user to be patient

            // await axios
            // .post("login", {
            //     email: credentials.email,
            //     password: credentials.password
            // })
            // .then(function(response) {
            //     var access_token = response.data.access_token;

            //     // store access token in localStorage
            //     localStorage.setItem("s3_access_token", access_token)

            //     commit(LOGGED_IN)
            // })
            // .catch(function(error) {
            //     console.log("Log in unsuccessful:", error)
            //     commit(SET_AUTHENTICATION_ERROR, true)
            //     commit(LOGGED_OUT)
            // })
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
