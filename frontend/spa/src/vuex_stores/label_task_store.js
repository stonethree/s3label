import { extractColor } from '../../static/color_utilities'

export const StoreLabelTask = {
    namespaced: true,
    state: {
        label_tasks: [],
        label_task_id: -1
    },
    mutations: {
        set_label_tasks(state, label_tasks) {
            state.label_tasks = label_tasks;
        },
        select_label_task(state, idx) {
            state.label_task_id = idx;
        },
    },
    getters: {
        label_tasks: state => {
            return state.label_tasks
        },
        label_task: state => {
            return state.label_tasks.find(label_task => label_task.label_task_id === state.label_task_id)
        },
        labels: (state, getters) => {
            if (getters.label_task != undefined) {
                return JSON.parse(getters.label_task.label_classes);
            }
            else {
                return undefined;
            }
        },
        label_colors: (state, getters) => {
            if (getters.labels != undefined) {
                var d = {};
        
                for (var i = 0; i < getters.labels.length; i++) {
                    d[getters.labels[i].label_class] = extractColor(getters.labels[i].color);
                }
                return d;
            }
            else {
                return undefined
            }
        }
    }
}
