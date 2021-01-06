---
Title: Structures
nav_order: 4
has_children: True
---
# Structures
{:.no_toc}

* TOC
{:toc}

## Overview
**PyMyoVent** uses a bundle of text files in [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value)) for handling different aspects of a single simulation.

## Batch
In batch file, each single simulation is defined as a `job` that contains the pathways to three types of input text file in [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value)):

1. Model file
2. Protocol file
3. Output handler file

These files are explained in following of this page.

For example, the following batch file includes one `job`.
````
{
    "PyMyoVent_batch":
    {
        "job":
        [
            {
                "model_file_string": "path_to_model_file.json",
                "protocol_file_string": "path_to_protocol_file.json",
                "output_handler_file_string": "path_to_output_handler_file.json"
            }
        ]
    }
}
````

Or the following batch file includes multiple jobs:
````
{
    "PyMyoVent_batch":
    {
        "job":
        [
            {
                "model_file_string": "path_to_model_file_1.json",
                "protocol_file_string": "path_to_protocol_file_1.json",
                "output_handler_file_string": "path_to_output_handler_file_1.json"
            },
            {
                "model_file_string": "path_to_model_file_2.json",
                "protocol_file_string": "path_to_protocol_file_2.json",
                "output_handler_file_string": "path_to_output_handler_file_2.json"
            },
            {
                "model_file_string": "path_to_model_file_3.json",
                "protocol_file_string": "path_to_protocol_file_3.json",
                "output_handler_file_string": "path_to_output_handler_file_3.json"
            }
        ]
    }
}
````
