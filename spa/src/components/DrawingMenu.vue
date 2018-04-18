<template>
    <div id="drawing-menu" class="container row">
        <!-- <div class="row"> -->
            <drawing-modes></drawing-modes>
            <label-classes></label-classes>
            <display-config></display-config>
        <!-- </div> -->
    </div>
</template>

<script>
import DrawingModes from './DrawingModes'
import LabelClasses from './LabelClasses'
import DisplayConfig from './DisplayConfig'

export default {
    name: 'drawing-menu',
    components: {
        DrawingModes,
        LabelClasses,
        DisplayConfig
    },
}
</script>

<style>
/* #drawing-menu {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>