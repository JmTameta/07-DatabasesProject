<!-- TEAM INTRODUCTION -->

<h1 align="center">Team 0107</h1>
<h2 align="center">
  Team Members: 
  <br />
  Jm Tameta, Matt Sacco, Matt Shea, Meghan McConnell, Sarah Phung, Val Roberts
  <br />
  ACC 311/CSC 315
  <br />
  Energy Demand
</h2>


<!-- PROJECT BREAKDOWN -->
## About The Project
### Problem 
Currently The College of New Jersey does not have a centralized database that provides information regarding the energy consumption of all buildings on campus. In addition there does not exist a user-friendly web application associated with said database; therefore one must search through multiple excel sheets to find and analyze the data they need. Furthermore due to the lack of a database, visualization tools such as graphs and infographics are not readily available. 

### Solution
In order to address the problem stated above our team will design, develop, and implement a centralized database that will focus on the two different energy sources used throughout campus: natural gas and electricity. Our initial approach will be evaluating our current datasets, focusing on the different energy usage and associated cost for each building on campus, and calculating the cost for future buildings. We can not state yet if we’re going to focus on residential halls or academic buildings because we have not determined the relationship between the buildings and the list of electric and natural gas meters.
However, our backup plan if we are unable to obtain the relationship between the meters and the on campus buildings, we will instead approach the entire campus’s energy consumption by focusing more on the square footage of buildings. We are currently evaluating if we can create the relationship between a building’s square footage and the energy it can potentially consume. 


## Getting Started
Run infoLoad_v2.sql to load in default data for school.

buildings contain the following fields.

 - **Name : (string)** Which contains the name of the building. Main key.
 - **b_type : (string:enum <Academic, Admin Services, Athletic, Residence Hall/Dormitory, Other, Student Services>)** which will specify the type of building it is.
 - **year_built : (integer)** which is the year that the building was made.
 - **sq_f : (integer)** which is the square footage of the building.

**ng_energy** and **el_energy** have a similar structure except for therms vs kwh as their unit for measurement.

 - **month : (int)** Is the numerical representation of the month. Part of main key.
 - **year : (int)** Is the year. Part of main key.
 - **meter_name : (string)** is the meter's id. Part of main key.
 - **cost : (float)** is the numerical cost of that month's entry.
 - **therms/kwh : (int)** Therms are used in ng_energy, and kwh is used in el_energy. Describe the number of units of said energy type used and generated during that month.

Once loaded in, run using flask run commands and access the launching page, which will look similar to this :

![](https://github.com/TCNJ-degoodj/cab-project-01-7/blob/main/doc/img/launchAreaGraph.png)

The user may use the left hand navigation panel to access different visualizations of the data by timeframe, as well as look at the percentage of energy usage and cost based on the given percentage shown in the main landing table.

## License
Distributed under the open source GNU GPL License.

## Contact
CSC 315 Students
<br />
Jm Tameta - tametaj1@tcnj.edu
<br />
Sarah Phung - phungs1@tcnj.edu
<br />
Val Roberts - robertv6@tcnj.edu
<br />
ACC 311 Students
<br />
Matt Sacco - saccom2@tcnj.edu
<br />
Matt Shea - sheam6@tcnj.edu
<br />
Meghan McConnell - 	mcconnm3@tcnj.edu


## Acknowledgements


https://github.com/othneildrew/Best-README-Template/blob/master/README.md
