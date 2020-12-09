from kedro.pipeline import node, Pipeline
from free_parking_to.pipelines.data_engineering.nodes import testing

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=testing,
                outputs="parking",
                inputs=None,
                name="extracting xml data"
            )
        ]
    )