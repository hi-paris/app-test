import streamlit as st
import json
import glob
import plotly.graph_objects as go
from collections import defaultdict

from htbuilder import HtmlElement, div, hr, a, p, img, styles
from htbuilder.units import percent, px

def main():
    def _max_width_():
        max_width_str = f"max-width: 1000px;"
        st.markdown(
            f"""
        <style>
        .reportview-container .main .block-container{{
            {max_width_str}
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )


    # Hide the Streamlit header and footer
    def hide_header_footer():
        hide_streamlit_style = """
                    <style>
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # increases the width of the text and tables/figures
    _max_width_()

    # hide the footer
    hide_header_footer()

# Use glob to collect all the JSON files in the directory
json_files = glob.glob('./results/*.json')  # Change this to the path where your JSON files are stored

# Function to group and average dataset results based on prefix
def summarize_dataset_scores(data, prefixes):
    summary = defaultdict(lambda: defaultdict(list))
    
    # Loop through each model and its scores
    for model_name, scores in data.items():
        for dataset, score in scores.items():
            # Check for each prefix
            for prefix in prefixes:
                if dataset.startswith(prefix):
                    summary[model_name][prefix].append(score)
    
    # Calculate the average score for each dataset prefix
    for model_name, prefix_scores in summary.items():
        for prefix in prefix_scores:
            if len(summary[model_name][prefix]) > 0:
                summary[model_name][prefix] = sum(summary[model_name][prefix]) / len(summary[model_name][prefix])
    
    return summary

# List of dataset prefixes to summarize
dataset_prefixes = ['fiqasa', 'agnews', 'dbpedia', 'headlines', 'arc', 'mmlu', 'yelp', 'sst2', 'financialphrasebank']  # Add more prefixes as needed

# Initialize an empty dictionary to store all summarized model data
models = {}

# Loop through each JSON file and read its content
for json_file in json_files:
    with open(json_file, 'r') as f:
        data = json.load(f)
        # Summarize scores for each dataset prefix
        summarized_scores = summarize_dataset_scores(data, dataset_prefixes)
        for model_name, scores in summarized_scores.items():
            models[model_name] = list(scores.values())

# Streamlit app starts here
st.subheader("Models Performance Comparison Across Datasets")

# Extract model names and dataset prefixes for multiselect options
model_names = list(models.keys())
available_datasets = dataset_prefixes

# Streamlit multiselect widgets for model and dataset selection
selected_models = st.sidebar.multiselect("Select Models", model_names, default=model_names)
selected_datasets = st.sidebar.multiselect("Select Datasets", available_datasets, default=available_datasets)

# Initialize a radar chart with Plotly
fig = go.Figure()

# Add traces for each selected model
for model_name in selected_models:
    scores = models[model_name]
    selected_scores = [score for dataset, score in zip(available_datasets, scores) if dataset in selected_datasets]
    filtered_datasets = [dataset for dataset in available_datasets if dataset in selected_datasets]

    fig.add_trace(go.Scatterpolar(
        r=selected_scores,
        theta=filtered_datasets,
        fill='toself',
        name=model_name,
        customdata=list(zip(selected_scores, filtered_datasets)),  # Custom data for hover info
        hovertemplate="<b>Dataset: %{customdata[1]}</b><br>" +
                      "Accuracy: %{customdata[0]:.2f}<extra></extra>"  # Custom hover text
    ))

# Customize the layout with increased size
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]  # Adjust range based on your data if necessary
        )
    ),
    showlegend=True,
    width=1000,  # Increased width
    height=700   # Increased height
)

# Display the radar chart
st.plotly_chart(fig)







if __name__=='__main__':
    main()
def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;background - color: white}
     .stApp { bottom: 80px; }
    </style>
    """
    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1,

    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer2():
    myargs = [
        "👨🏼‍💻 Made by ",
        link("https://www.hi-paris.fr/", "Laurène David, Gaëtan Brison, Fabio Pizzati, Stéphane Lathuilière"),
        "🚀"
    ]
    layout(*myargs)


if __name__ == "__main__":
    footer2()