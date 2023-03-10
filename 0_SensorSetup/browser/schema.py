def parse_schema(filepath):
    """
    Reads in a schema file of the form:
    ```
    label1
    label2
    ...
    labelN
    ```
    and returns a list of the labels.
    """
    with open(filepath, "r") as f:
        labels = [line.strip() for line in f.readlines()]
    return labels
