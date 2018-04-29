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

// loadNextImage: async function () {
//     // first try get next image that the user has already viewed/labeled, if one exists

//     let access_token = localStorage.getItem("s3_access_token");

//     let config = {
//         headers: {
//         Authorization: "Bearer " + access_token
//         }
//     };

//     var vm = this;
//     var got_an_image = false;


//     // check if we have an input data ID first

//     if (this.input_data_id != undefined) {
//         got_an_image = await axios
//             .get("labeled_data/label_tasks/" + this.label_task.label_task_id + "?action=next&current_input_data_id=" + this.input_data_id, config)
//             .then(function(response) {
//                 if (response.data.length == 1) {
//                     var next_data_item = response.data[0];
//                     // vm.fetchAndDisplayImage(baseUrl + '/input_images/' + next_data_item.input_data_id);
//                     vm.input_data_id = next_data_item.input_data_id;
//                     return true;
//                 }
//                 else {
//                     return false;
//                 }
//             })
//             .catch(function(error) {
//                 console.log('error getting next image:', error);
//                 return false;
//             });
//     }

//     // request a fresh unlabeled image if we have already scrolled to the most recent image

//     if (!got_an_image) {
//         console.log('get new unlabeled image')

//         got_an_image = await axios
//             .get("unlabeled_images/label_tasks/" + this.label_task.label_task_id + "?shuffle=true", config)
//             .then(function(response) {
//                 return response.data.input_data_id;
//             })
//             .then(function(input_data_id) {
//                 vm.fetchAndDisplayImage(baseUrl + '/input_images/' + input_data_id);
//                 vm.input_data_id = input_data_id;
//                 return true;
//             })
//             .catch(function(error) {
//                 console.log(error);
//                 return false;
//             });
//     }

//     // if we have scrolled to the most recent image and no unlabeled images are available, display a message to the user

//     if (!got_an_image) {
//         console.log("No more unlabeled images available!")
//         vm.input_data_id = undefined;
//         // this.draw_image_unavailable_placeholder();
//     }
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