<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Remove all default margins, padding, and backgrounds */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  background: transparent;
}

#app {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: transparent;
}

/* Ensure router-view also has no margins */
.router-view {
  margin: 0;
  padding: 0;
  width: 100%;
}
</style>
