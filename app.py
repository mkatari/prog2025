from pathlib import Path

import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

sns.set_theme()

# Load your GTEx-based demo data
df = pd.read_csv(Path(__file__).parent / "gtex_shiny_demo.csv")

# Automatically detect numeric columns (for X/Y axes)
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# Categorical grouping: broad tissue
tissue_col = "Broad Tissue"
tissues = df[tissue_col].unique().tolist()
tissues.sort()

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_selectize(
            "xvar",
            "X variable (QC metric)",
            numeric_cols,
            selected=numeric_cols[0] if numeric_cols else None,
        ),
        ui.input_selectize(
            "yvar",
            "Y variable (QC metric)",
            numeric_cols,
            selected=numeric_cols[1] if len(numeric_cols) > 1 else None,
        ),
        ui.input_checkbox_group(
            "tissue",
            "Filter by tissue",
            tissues,
            selected=tissues,
        ),
        ui.hr(),
        ui.input_switch("by_tissue", "Color by tissue", value=True),
        ui.input_switch("show_margins", "Show marginal plots", value=True),
    ),
    ui.card(
        ui.h4("GTEx sample QC scatterplot"),
        ui.output_plot("scatter"),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        """Return a data frame that includes only the selected tissues."""
        req(len(input.tissue()) > 0)
        return df[df[tissue_col].isin(input.tissue())]

    @output
    @render.plot
    def scatter():
        """Generate the QC scatterplot (with or without marginal plots)."""

        plotfunc = sns.jointplot if input.show_margins() else sns.scatterplot

        plotfunc(
            data=filtered_df(),
            x=input.xvar(),
            y=input.yvar(),
            hue=tissue_col if input.by_tissue() else None,
            hue_order=tissues,
            legend=False,
        )


app = App(app_ui, server)