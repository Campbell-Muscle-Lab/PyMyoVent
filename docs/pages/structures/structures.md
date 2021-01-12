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
- In general, each **PyMyoVent** simulation is divided into three separated parts, in which the user has control on them via defining three main text files in [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value)):

1. [Model file](model/model.html)
2. [Protocol file](protocol/protocol.html)
3. [Output handler file](output_handler/output_handler.html)

- For running a simulation with **PyMyoVent**, the user needs to define the pathway strings to the location of these three user-defined files in the `batch.json` file located in `path_to_PyMyoVent_repo/dmo_files` directory.

## Batch
- In batch file, each single simulation is defined as a `job` that contains the pathway strings to the location of three types of input text file in [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value)):

- For example, the following batch file includes one `job` representing one simulation.

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

- Or the following batch file includes multiple jobs:

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
