---
Title: Output handler
nav_order: 3
has_children: False
parent: Structures
---
# Output handler
{:.no_toc}

* TOC
{:toc}


## Output handler

- Output-handler accounts for handling the output files from a simulation. The output data can be stored in a spread sheet with extension format of `.csv` or `.excel` by defining `simulation_output_file_string` in the output handler file. Also the output data can be visualized in a default format by defining `summary_image_file_string` as the pathway directory for saving the `summary_image.png`.

- A user can define more `user_defined` figures in [multipanel format](http://campbell-muscle-lab.github.io/PyCMLutilities/pages/demos/plots/multipanel/multipanel.html) by defining two parameters:

1. `template_file_string` : Path to the directory where the template for [multipanel format](http://campbell-muscle-lab.github.io/PyCMLutilities/pages/demos/plots/multipanel/multipanel.html) in [JSON format](http://en.wikipedia.org/wiki/JSON#:~:text=JavaScript%20Object%20Notation%20(JSON%2C%20pronounced,or%20any%20other%20serializable%20value)) is located.

2. `output_file_string` : Path to the directory where a user wants to save the user_defined figure in [multipanel format](http://campbell-muscle-lab.github.io/PyCMLutilities/pages/demos/plots/multipanel/multipanel.html).

````
{
    "simulation_output_file_string": "path_to_output_data.csv",
    "summary_image_file_string": "path_to_summary_figure.png",
    "user_defined_images":
    {
        "user_defined":
        [
            {
                "template_file_string": "path_to_template_file.json",
                "output_file_string": "path_to_user_defined_figure.png"
            }
        ]
    }
}
````
