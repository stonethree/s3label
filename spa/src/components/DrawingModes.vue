<template>
    <div class="container row">
        <div id="tools" class="col border-right">
            <span>Tools</span>
            <form id="tools_form">
                <input type="radio" class="radio-button" name="tool" value="freehand" v-model="active_tool"> Freehand
                <br>
                <input type="radio" class="radio-button" name="tool" value="polygon" v-model="active_tool"> Polygon
                <br>
                <input type="radio" class="radio-button" name="tool" value="select" v-model="active_tool"> Select
            </form>
        </div>
        <div id="tool_modes" class="col border-right">
            <span>Modes</span>
            <form id="mode_form">
                <input type="radio" class="radio-button" name="mode" value="new" v-model="active_mode"> New
                <br>
                <input type="radio" class="radio-button" name="mode" value="append" v-model="active_mode"> Append
                <br>
                <input type="radio" class="radio-button" name="mode" value="erase" v-model="active_mode"> Erase
            </form>
        </div>
        <div id="choose_overlap" class="col border-right">
            <span>Overlap Mode</span>
            <form>
                <input type="radio" class="radio-button" name="overlap_mode" value="overlap" v-model="active_overlap_mode"> Overlapping
                <br>
                <input type="radio" class="radio-button" name="overlap_mode" value="no-overlap" v-model="active_overlap_mode"> Non-overlapping
            </form>
        </div>
    </div>
</template>

<script>
export default {
    name: 'drawing-modes',
    data: function() {
        return {
            active_tool: "freehand",
            active_mode: "new",
            active_overlap_mode: "no-overlap",
            previous_tool: null,
            previous_mode: null,
        };
    },
    watch: {
        active_tool: function (newActiveTool, oldActiveTool) {
            this.previous_tool = oldActiveTool;
        },
        active_mode: function (newActiveMode, oldActiveMode) {
            this.previous_mode = oldActiveMode;
        }
    },
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