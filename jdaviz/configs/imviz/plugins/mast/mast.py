import os.path

import astropy.units as u
import solara
from astroquery.mast.missions import MastMissions
from traitlets import Bool, Unicode, observe

from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, TableMixin
from astropy.coordinates import SkyCoord

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

# the `noqa` call is required to suppress warning from this rule:
# https://solara.dev/documentation/advanced/understanding/rules-of-hooks
button = None

icon = solara.reactive('mdi-magnify')


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
    observations.value = MastMissions.get_unique_product_list(
        products
    )
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
    observations.value = MastMissions.query_region(
        coordinates=coord,
        radius=radius.value * u.deg,
        limit=limit.value
    )
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
        solara.Markdown("### Search")
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

    target_name = target_name
    targ_ra = targ_ra
    targ_dec = targ_dec
    radius = radius
    limit = limit
    observations = observations

    _uri = Unicode().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._plugin_description = 'MAST plugin'

        self.widget = Page.widget()
        self.widget_model_id = 'IPY_MODEL_' + self.widget.model_id

        self.table._selected_rows_changed_callback = self._table_selection_changed

    def search_by_name(self):
        _search_by_name()
        self.table._qtable = observations.value

    def cone_search(self):
        _cone_search()
        self.table._qtable = observations.value

    # @property
    # def uri(self):
    #     return self._uri
    #
    # @uri.setter
    # def uri(self, value):
    #     print(f'set uri to {value}')
    #     selected_uri.set(value)
    #     self._uri = value

    @observe('_uri')
    def _load_uri(self):
        print(f'load uri {self._url}')
        local_path = os.path.basename(self._url)
        status, msg, url = MastMissions.download_file(
            uri=self.uri,
            local_path=local_path
        )
        print(f'{status=}')
        print(f'{url=}')
        self.app.load_data(local_path, show_in_viewer='imviz-0')