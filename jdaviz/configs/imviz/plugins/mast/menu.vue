<template>
  <j-tray-plugin>
        <jupyter-widget :widget="widget_model_id" />
    <div v-if="table_widget.length > 0">
        <jupyter-widget :widget="table_widget"></jupyter-widget>
    </div>
  </j-tray-plugin>
</template>
<script setup lang="ts">
</script>