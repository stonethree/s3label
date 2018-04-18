<template>
    <div class="container">
        <div id="graphics_settings" class="col">
            <div id="stroke_slider_container">
                <span>Stroke thickness</span>
                <input id="stroke_thickness_slider" type="range" min="0" max="10" value="2" class="slider" @change="strokeThicknessChange">
            </div>
            <div id="opacity_slider_container">
                <span>Opacity</span>
                <input id="opacity_slider" type="range" min="0" max="100" value="50" class="slider">
            </div>
        </div>
        <div id="clear_canvas_container" class="col">
            <button type="submit" onclick="clearCanvas();">Clear canvas</button>
        </div>
    </div>
</template>

<script>
// detect stroke thickness and opacity slider changes

// stroke_thickness_slider.oninput = function () {

//     if (this.value > 0) {
//         ctx.lineWidth = this.value;
//         use_stroke = true;
//     }
//     else {
//         ctx.lineWidth = 1;
//         use_stroke = false;
//     }

//     drawAllPolygons(ctx, polygons);
// }

// opacity_slider.oninput = function () {
//     opacity = this.value / 100.;

//     drawAllPolygons(ctx, polygons);
// }

export default {
    name: 'display-config',
    data: function() {
        return {
            stroke_slider_value: null,
            opacity_slider_value: null,
        };
    },
    computed: {
        stroke_thickness: function() {
            return Math.max(1, stroke_slider_value);
        },
        use_stroke: function() {
            return stroke_slider_value > 0 ? true : false; 
        },
        opacity: function() {
            return this.value / 100.;
        }
    },
    methods: {
        strokeThicknessChange: function(event) {
            console.log(event);
        },
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