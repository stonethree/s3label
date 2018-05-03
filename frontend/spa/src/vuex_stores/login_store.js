import axios from 'axios';

axios.defaults.baseURL = "http://127.0.0.1:5000/image_labeler/api/v1.0/";

const ATTEMPT_LOGIN = 'attempt_login';
const LOGGED_IN = 'logged_in';
const LOGGED_OUT = 'logged_out';
const SET_USER_ID = 'set_user_id';
const SET_AUTHENTICATION_ERROR = 'set_authentication_error';
const SET_USER_TYPE = 'set_user_type';

export const NORMAL_USER = 'normal_user';
export const ADMIN_USER = 'admin_user';

export const StoreLogin = {
    namespaced: true,
    state: {
        is_logged_in: false, //!!localStorage.getItem("s3_access_token"),
        pending: false,
        user_id: undefined,
        authentication_error: false,
        user_type: NORMAL_USER
    },
    mutations: {
        [ATTEMPT_LOGIN] (state) {
            state.is_logged_in = false;
            state.pending = true;
        },
        [LOGGED_IN] (state) {
            state.is_logged_in = true;
            state.pending = false;
            state.authentication_error = false;
        },
        [LOGGED_OUT] (state) {
            state.is_logged_in = false;
            state.pending = false;
        },
        [SET_USER_ID] (state, user_id) {
            state.user_id = user_id;
        },
        [SET_AUTHENTICATION_ERROR] (state, error_occured) {
            state.authentication_error = error_occured;
        },
        [SET_USER_TYPE] (state, user_type) {
            if (user_type == NORMAL_USER || user_type == ADMIN_USER) {
                state.user_type = user_type;
            }
        },
    },
    actions: {
        async login({ commit }, credentials) {
            commit(ATTEMPT_LOGIN)

            // attempting to log in. Can display a spinner during this period to notify user to be patient

            await axios
            .post("login", {
                email: credentials.email,
                password: credentials.password
            })
            .then(function(response) {
                var access_token = response.data.access_token;

                // store access token in localStorage
                localStorage.setItem("s3_access_token", access_token)

                commit(LOGGED_IN)
            })
            .catch(function(error) {
                console.log("Log in unsuccessful:", error)
                commit(SET_AUTHENTICATION_ERROR, true)
                commit(LOGGED_OUT)
            })
        },
        async get_user_id({ commit }) {
            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            await axios
            .get("user_id", config)
            .then(function(response) {
                commit(SET_USER_ID, response.data.user_id)
            })
            .catch(function(error) {
                commit(SET_USER_ID, undefined)
                console.log("Could not get user ID:", error)
            })
        },
        async get_user_type({ commit }) {
            let access_token = localStorage.getItem("s3_access_token");

            let config = {
                headers: {
                Authorization: "Bearer " + access_token
                }
            };

            await axios
            .get("users", config)
            .then(function(response) {
                commit(SET_USER_TYPE, ADMIN_USER);
            })
            .catch(function(error) {
                commit(SET_USER_TYPE, NORMAL_USER);
            })
        },
        logout({ commit }) {
            // remove access token from server to prevent user to making further requests to the backend
            localStorage.removeItem("s3_access_token")
            commit(LOGGED_OUT);
            commit(SET_USER_TYPE, NORMAL_USER);
        }
    },
    getters: {
        is_logged_in: state => {
            return state.is_logged_in;
        },
        user_id: state => {
            return state.user_id;
        },
        authentication_error: state => {
            return state.authentication_error;
        },
        is_admin_user: state => {
            return state.user_type == ADMIN_USER;
        },
    }
}