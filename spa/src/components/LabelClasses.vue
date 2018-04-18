<template>
    <div class="container row">
        <div id="semantic_labels" class="col border-right">
            <span>Semantic Labels</span>
            <form>
                <div v-for="label in labels" :key="label.label_class">
                    <input type="radio" class="radio-button" name="semantic_label" :value="label.label_class" v-model="active_label"> {{ label.label_class }} <br>
                </div>
            </form>
        </div>
    </div>
</template>

<script>

export default {
    name: 'label-classes',
    data: function() {
        return {
            labels: [{"label_class": "Individual rock", "color": [255, 0, 0]}, 
                     {"label_class": "Belt", "color": [0, 255, 0]}, 
                     {"label_class": "Other", "color": [0, 0, 255]}],
            active_label: null,
        };
    },
    created() {
       this.active_label = this.labels[0].label_class;
       console.log(this.labels[0].label_class)
    }
}
</script>

<style>
/* #about {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>