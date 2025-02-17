<template>
  <j-tray-plugin>
    <j-plugin-section-header>Search</j-plugin-section-header>

    <jupyter-widget :widget="widget_model_id" />

    <j-plugin-section-header>Selected data products</j-plugin-section-header>
    <jupyter-widget :widget="table_selected_widget" />
     <v-btn @click="load_images">
        Download
     </v-btn>

    <j-plugin-section-header>More data products</j-plugin-section-header>
    <jupyter-widget :widget="table_widget" />


</j-tray-plugin>
</template>
<script setup lang="ts">
</script>