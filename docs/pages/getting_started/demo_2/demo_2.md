### Run a defined model

1. Open a command prompt
  + If you don't know how
    + type cmd in the Search field of your start menu
    + or Google it to find instructions that work for you

1. Change the directory to the Python_code folder of your repository
   + If you installed PyMyoVent in `c:\users\your_username_here\GitHub\PyMyoVent`  
you can type  
`cd c:\users\your_username_here\GitHub\PyMyoVent\Python_code`  
and press enter

1. In the command window, type  
`python PyMyoVent.py run_defined_model ..\demo_files\demo_2\demo_2_model.xml`  
and press enter
  + This command ran a model specified by the demo_2_model.xml file shown above

1. Wait a few seconds and you should see the model running in the command window

1. Now open file explorer (the program you use to look for files on your hard-drive)
  + Go to the base folder of your repository
    + for example, `c:\users\your_username_here\GitHub\PyMyoVent`
  + Now look in the `temp\demo_2` folder
  + You should see the following images
![Summary](demo_2_summary.png)
![Pressure Volume](demo_2_pv.png)
![Flows](demo_2_flows.png)
![Half-sarcomere fluxes](demo_2_hs_fluxes.png)






