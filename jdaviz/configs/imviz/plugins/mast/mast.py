import os.path

import astropy.units as u
import solara
from astroquery.mast.missions import MastMissions
from traitlets import Bool, Unicode, observe, Integer, Instance

from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, Table, TableMixin, with_spinner
from astropy.coordinates import SkyCoord
from astropy.table import QTable

MastMissions.mission = 'jwst'
mission_columns = MastMissions.get_column_list()
mission_columns.add_index('name')

__all__ = ['Mast']

target_name = solara.reactive(None)
targ_ra = solara.reactive(None)
targ_dec = solara.reactive(None)
radius = solara.reactive(0.2)
limit = solara.reactive(10)
selected_uri = solara.reactive('')
observations = solara.reactive(None)
progress = solara.reactive(False)
cell = solara.reactive({})
button = None
icon = solara.reactive('mdi-magnify')


from traitlets import HasTraits


class Counter(HasTraits):
    """
    This class has a `value` attr that increments
    whenever the observation table gets updated,
    and the value gets observed by the plugin. This allows
    both the solara widget's buttons and the jdaviz vue buttons
    to have the same effects.
    """
    value = Integer()

    def __init__(self, val=0):
        self.value = val


counter = Counter()


def default_table_cuts(table):
    """
    For now, return only calibrated science images.
    """
    cuts = (
            (table['type'] == 'science') &
            (table['file_suffix'] == '_cal') &
            (table['access'] == 'PUBLIC')
    )

    return table[cuts]


def _search_by_name():
    progress.set(True)
    icon.set('mdi-progress-clock')

    # identify data products that meet criteria:
    products = MastMissions.query_object(
        objectname=target_name.value,
        radius=radius.value * u.deg,
        limit=limit.value,
    )
    # get table of unique data products from above:
    observations.value = default_table_cuts(
            MastMissions.get_unique_product_list(
            products,
        )
    )
    counter.value += 1
    icon.set('mdi-magnify')
    progress.set(False)


@solara.component
def search_by_name():  # noqa: SH103
    solara.InputText("Search target name", value=target_name, continuous_update=False)
    solara.InputFloat("Radius (deg)", radius)
    solara.InputInt("Limit results", limit)
    solara.ProgressLinear(value=progress.value)
    solara.Button(
        "Search", on_click=_search_by_name, text=True,
        icon_name=icon.value,
    )


def _cone_search():
    progress.set(True)
    icon.set('mdi-progress-clock')
    coord = SkyCoord(ra=targ_ra.value * u.deg, dec=targ_dec.value * u.deg)
    observations.value = default_table_cuts(
            MastMissions.query_region(
            coordinates=coord,
            radius=radius.value * u.deg,
            limit=limit.value,
        )
    )
    counter.value += 1
    icon.set('mdi-magnify')
    progress.set(False)


@solara.component
def cone_search():  # noqa: SH103
    progress = solara.use_reactive(False)

    solara.InputFloat("RA", targ_ra, optional=True)
    solara.Text(mission_columns.loc['targ_ra']['description'])
    solara.InputFloat("Dec", targ_dec, optional=True)
    solara.Text(mission_columns.loc['targ_dec']['description'])
    solara.InputFloat("Radius (deg)", radius)
    solara.InputInt("Limit results", limit)
    solara.ProgressLinear(value=progress.value)
    solara.Button(
        "Search", on_click=_cone_search, text=True,
        icon_name=icon.value,
    )


@solara.component
def FilterTable(df):
    def on_action_cell(column, row_index):
        cell.set(dict(column=column, row_index=row_index))
        select_uri = df.iloc[int(row_index)]['uri']
        print(f'select URI: {select_uri}')
        selected_uri.set(select_uri)

    cell_actions = [solara.CellAction(icon="mdi-file-download-outline", name="Load file", on_click=on_action_cell)]

    solara.provide_cross_filter()
    solara.CrossFilterReport(df, classes=["py-2"])
    solara.CrossFilterSelect(df, "instrument_name", multiple=True)
    solara.CrossFilterSelect(df, "filters", multiple=True)
    solara.CrossFilterSelect(df, "type", multiple=True)
    solara.CrossFilterSelect(df, "file_suffix", multiple=True)
    solara.CrossFilterSelect(df, "category", multiple=True)
    solara.CrossFilterDataFrame(
        df, items_per_page=5, scrollable=True,
        cell_actions=cell_actions
    )


@solara.component
def Page():
    with solara.Column():
        # solara.Markdown("### Search")
        solara.Details("Search by name", [search_by_name()])
        solara.Details("Search by coord", [cone_search()])
        # if observations.value is not None:
        #     solara.Markdown("### Results")
        #     FilterTable(observations.value.to_pandas())


name = 'mast'
label = "MAST"


@tray_registry(name, label=label, overwrite=True)
class Mast(PluginTemplateMixin, TableMixin):
    """
    """
    template_file = __file__, "menu.vue"
    show_menu = Bool(True).tag(sync=True)
    context = Bool(False).tag(sync=True)
    file_set_name = Unicode().tag(sync=True)
    widget_model_id = Unicode().tag(sync=True)
    table_selected_widget = Unicode().tag(sync=True)

    target_name = target_name
    targ_ra = targ_ra
    targ_dec = targ_dec
    radius = radius
    limit = limit
    observations = observations
    n_obs = 0 if observations.value is None else len(observations.value)

    # counter = Instance(klass=Counter, args=(2,))

    _uri = Unicode().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_notifiers()

        self._plugin_description = 'MAST plugin'

        self.widget = Page.widget()
        self.widget_model_id = 'IPY_MODEL_' + self.widget.model_id
        self.table.item_key = 'uri'

        # initializing the headers in the table that is displayed in the UI
        # self.table.headers_avail = self.headers
        # self.table.headers_visible = self.headers
        # self.table._default_values_by_colname = self._default_table_values
        self.table._selected_rows_changed_callback = self._table_selection_changed
        self.table.show_rowselect = True

        def clear_table_callback():
            # gets the current viewer
            viewer = self.viewer.selected_obj

            # resetting values
            self.results_available = False
            self.number_of_results = 0

            if self._marker_name in self.app.data_collection.labels:
                # all markers are removed from the viewer
                viewer.remove_markers(marker_name=self._marker_name)

        self.table._clear_callback = clear_table_callback

        self.table_selected = Table(self, name='table_selected')
        self.table_selected.clear_btn_lbl = 'Clear Selection'
        self.table_selected.show_if_empty = False

        def clear_selected_table_callback():
            self.table.select_none()

        self.table_selected._clear_callback = clear_selected_table_callback
        self.table_selected_widget = 'IPY_MODEL_'+self.table_selected.model_id

    def _table_selection_changed(self, msg={}):
        selected_rows = self.table.selected_rows

        self.table_selected._clear_table()
        for selected_row in selected_rows:
            self.table_selected.add_item(selected_row)

    def search_by_name(self):
        _search_by_name()
        self._update_table()

    def cone_search(self):
        _cone_search()
        self._update_table()

    @with_spinner()
    def vue_load_images(self, event):
        uris_to_load = list(self.table_selected._qtable['uri'])

        for uri in uris_to_load:
            local_path = os.path.basename(uri)
            status, msg, url = MastMissions.download_file(
                uri=uri,
                local_path=local_path
            )
            print(f"{local_path=}")
            self.app._jdaviz_helper.load_data(local_path)

        self.table_selected.clear_table()

    def set_notifiers(self):
        HasTraits.observe(counter, self._update_table, 'value')

    def _update_table(self, value=None):
        print(f"change {value=}")
        self.table.add_item(QTable(observations.value))
