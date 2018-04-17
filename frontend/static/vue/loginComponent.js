axios.defaults.baseURL = 'http://127.0.0.1:5000/image_labeler/api/v1.0/';

Vue.component('s3label-login', {
  data: function () {
    return {
      count: 0
    }
  },
  template: '<button v-on:click="count++">Login {{ count }} times.</button>'
})

Vue.component('label-task-chooser', {
  data: function () {
    return {
      picked: -1,
      label_tasks: []
    }
  },
  methods: {
    get_label_options: function (event) {
      // get list of label tasks from the backend

      const vm = this;

      axios.get('label_tasks')
        .then(function (response) {
          vm.label_tasks = response.data;
        })
        .catch(function (error) {
          console.log(error);
        });
    },
    select_label_task: function (label_task_id) {
      // go to other window to allow user to label images from this label task
      console.log('select label task:', label_task_id);
    },
    view_labeled_data: function (label_task_id) {
      // go to other window to allow user to view his/her images from this label task
      console.log('view_labeled_data:', label_task_id);
    }
  },
  template: `
    <div>
      <button v-on:click="get_label_options">Get label tasks</button>
      <div  v-for="lt in label_tasks">

        <div class="card" style="background-color:hsla(20, 100%, 64%, 0.7);">
          <div class="card-body">
            <h4 class="card-title"> {{ lt.label_task_id }} - {{ lt.title }} </h4>
            <h6 class="card-subtitle mb-2 font-italic"> {{ lt.type }} </h6>
            <p> {{ lt.description }} </p>
            <button v-on:click="select_label_task(lt.label_task_id)"> Label data </button>
            <button v-on:click="view_labeled_data(lt.label_task_id)"> View labeled data </button>
          </div>
        </div>

      </div>

      <br>
      <span>Picked: {{ picked }}</span>
      <button v-on:click="select_label_task">Choose this label task</button>

    </div>`
})

Vue.component('label-classes', {
  data: function () {
    return {
      picked: -1,
      label_tasks: [],
      label_task: -1
    }
  },
  computed: {
    label_class_options: function () {
      if (this.label_task != -1) {
        return JSON.parse(this.label_task.label_classes);
      }
      else {
        return [{ label_class: 'c1', colour: 'red' }, { label_class: 'c2', colour: 'blue' }, { label_class: 'c3', colour: 'green' }];
      }
    }
  },
  methods: {
    get_label_options: function (event) {
      // get list of label tasks from the backend

      const vm = this;

      axios.get('label_tasks')
        .then(function (response) {
          vm.label_tasks = response.data;

          // choose one of the label tasks
          vm.label_task = vm.label_tasks[0];
        })
        .catch(function (error) {
          console.log(error);
        });
    }
  },
  template: `<div>
      <button v-on:click="get_label_options">Get label tasks</button>
      <div  v-for="item in label_class_options">
        <input type="radio" :value="item.label_class" v-model="picked"> {{ item.label_class }} </input>
      </div>
      <br>
      <span>Picked: {{ picked }}</span>
    </div>`
})





new Vue({
  el: '#components-demo'
})