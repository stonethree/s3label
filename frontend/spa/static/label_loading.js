// uploadLabeledImage: function (input_data_id) {      // TODO: this should be made a "static" function and moved into a separate javascript file

//     console.log('uploading label with label task ID', this.label_task.label_task_id, 'and input data ID', input_data_id)

//     var data = {label_serialised: this.polygons}

//     let access_token = localStorage.getItem("s3_access_token");

//     let config = {
//         headers: {
//         Authorization: "Bearer " + access_token
//         }
//     };

//     var vm = this;

//     axios
//         .post("label_history/label_tasks/" + vm.label_task.label_task_id + "/input_data/" + input_data_id, data, config)
//         .then(function(response) {
//             console.log('saving:', vm.label_task.label_task_id, input_data_id, response)
//         })
//         .catch(function(error) {
//             console.log('error saving label:', error);
//         });
// },

// loadImageLabels: function (input_data_id) {     // TODO: this should be made a "static" function and moved into a separate javascript file (i.e. maybe return a promise with the polygons array)

//     console.log('getting image labels with label task ID', this.label_task.label_task_id, 'and input data ID', input_data_id)

//     let access_token = localStorage.getItem("s3_access_token");

//     let config = {
//         headers: {
//         Authorization: "Bearer " + access_token
//         }
//     };

//     var vm = this;

//     axios
//         .get("labels/input_data/" + input_data_id + "/label_tasks/" + this.label_task.label_task_id, config)
//         .then(function(response) {
//             if (response.data.length == 1) {
//                 console.log("Label found for this image: attempting to apply it in the view")
//                 var label = response.data[0];

//                 // check label format is correct

//                 var polygons = JSON.parse(label.label_serialised);

//                 if (polygons.length > 0 && polygons[0].polygon != undefined) {
//                     console.log('Applied serialised label to image')
//                     vm.polygons = polygons;
//                     // vm.drawAllPolygons(vm.ctx, vm.polygons);
//                 }
//                 else {
//                     console.log('Serialised label has wrong format:', polygons)
//                 }
//             }
//             else if (response.data.length == 0) {
//                 console.log("No label found for this image")
//             }
//             else {
//                 console.log("Error: expected at most one label for this image!")
//             }
//         })
//         .catch(function(error) {
//             console.log(error);
//         });
// },

// get_label_id: function (label_task_id, input_data_id, user_id) {
//     // get the label ID, given user ID, label task ID and input data ID

//     if (label_task_id == undefined || input_data_id == undefined || user_id == undefined) {
//         console.log("Input fields must all be defined in order to get the label ID")
//         this.label_id = undefined;
//     }
//     else {
//         let access_token = localStorage.getItem("s3_access_token");

//         let config = {
//             headers: {
//             Authorization: "Bearer " + access_token
//             }
//         };

//         var vm = this;

//         axios
//             .get("label_ids/label_tasks/" + label_task_id + "/input_data/" + input_data_id + "/user/" + user_id, config)
//             .then(function(response) {
//                 console.log('dfdgff', response.data, 'user_id:', user_id, 'input_data_id:', input_data_id, 'label_task_id:', label_task_id, 'label_id:', response.data.label_id)
//                 vm.label_id = response.data.label_id;
//             })
//             .catch(function(error) {
//                 console.log('error getting label id:', error);
//                 vm.label_id = undefined;
//             });
//     }
// }