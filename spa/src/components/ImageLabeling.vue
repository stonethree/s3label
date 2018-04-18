<template>
    <div id="image_labeling" class="container">
        <div class="row">
            <drawing-menu></drawing-menu>
        </div>
        <div class="row">
            <drawing-canvas></drawing-canvas>
        </div>
    </div>
</template>

<script>
import DrawingMenu from './DrawingMenu'
import DrawingCanvas from './DrawingCanvas'

export default {
    name: 'image_labeling',
    components: {
        DrawingMenu,
        DrawingCanvas
    },
}
</script>

<style>
/* #image_labeling {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>