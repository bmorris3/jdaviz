<template>
  <j-tray-plugin
    :config="config"
    plugin_key="Footprints"
    :api_hints_enabled.sync="api_hints_enabled"
    :description="docs_description"
    :link="docs_link || 'https://jdaviz.readthedocs.io/en/'+vdocs+'/'+config+'/plugins.html#footprints'"
    :uses_active_status="uses_active_status"
    @plugin-ping="plugin_ping($event)"
    :keep_active.sync="keep_active"
    :disabled_msg="disabled_msg"
    :popout_button="popout_button"
    :scroll_to.sync="scroll_to">

    <jupyter-widget :widget="table_widget"></jupyter-widget> 

  </j-tray-plugin>
</template>

<script>
  module.exports = {
    created() {
      this.throttledSetColor = _.throttle(
        (v) => { this.color = v },
        100);
    },
    methods: {
      boolToString(b) {
        if (b) {
          return 'True'
        } else {
          return 'False'
        }
      },
    } 
  }
</script>

<style>
  .v-slider {
    margin: 0px !important;
  }

  .color-menu {
      font-size: 16px;
      padding-left: 16px;
      border: 2px solid rgba(0,0,0,0.54);
  }
</style>
