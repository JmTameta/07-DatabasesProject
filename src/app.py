#! /usr/bin/python3

"""
This is an example Flask | Python | Psycopg2 | PostgreSQL
application that connects to the 7dbs database from Chapter 2 of
_Seven Databases in Seven Weeks Second Edition_
by Luc Perkins with Eric Redmond and Jim R. Wilson.
The CSC 315 Virtual Machine is assumed.
John DeGood
degoodj@tcnj.edu
The College of New Jersey
Spring 2020
----
One-Time Installation
You must perform this one-time installation in the CSC 315 VM:
# install python pip and psycopg2 packages
sudo pacman -Syu
sudo pacman -S python-pip python-psycopg2
# install flask
pip install flask
----
Usage
To run the Flask application, simply execute:
export FLASK_APP=app.py 
flask run
# then browse to http://127.0.0.1:5000/
----
References
Flask documentation:  
https://flask.palletsprojects.com/  
Psycopg documentation:
https://www.psycopg.org/
This example code is derived from:
https://www.postgresqltutorial.com/postgresql-python/
https://scoutapm.com/blog/python-flask-tutorial-getting-started-with-flask
https://www.geeksforgeeks.org/python-using-for-loop-in-flask/
"""

import psycopg2
from config import config
from flask import Flask, render_template, request

import json
from urllib.parse import urlencode

# Connect to the PostgreSQL database server
def connect(query):
	conn = None
	try:
		# read connection parameters
		params = config()

		# connect to the PostgreSQL server
		print('Connecting to the %s database...' % (params['database']))
		conn = psycopg2.connect(**params)
		print('Connected.')
	  
		# create a cursor
		cur = conn.cursor()
		
		# execute a query using fetchall()
		cur.execute ('CALL setup_building_sqft_calc();')
		cur.execute(query)
		rows = cur.fetchall()

		# close the communication with the PostgreSQL
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if conn is not None:
		    conn.close()
		    print('Database connection closed.')
	# return the query result from fetchall()
	return rows
 
# app.py
app = Flask(__name__)

monthDict = {
	"1": "Jan",
	"2": "Feb",
	"3": "Mar",
	"4":"Apr",
	"5": "May",
	"6": "Jun",
	"7": "Jul",
	"8": "Aug",
	"9": "Sep",
	"10": "Oct",
	"11": "Nov",
	"12": "Dec"
}

''' *************************************************************
landing page display building percentages
************************************************************* '''
@app.route("/")
def form():
		
	# call database	
	rows = connect('SELECT b_type, SUM(sq_ft) FROM buildings GROUP BY b_type;')
	
	# create arrays to hold b_type attribute name & their sum sq_ft
	building_types = [] # all buildings by b_type
	building_areas = []	# summation of sq_ft per building type
	for x in rows:
		building_types.append (x[0])
		building_areas.append (x[1])

	print(building_types)
	print(building_areas)
	
	# quick charts json create	
	config = {
	   "type": "outlabeledPie",
	   "data": {
		   "labels": building_types,
		   "datasets": [{
			   "label": "Foo",
			   "backgroundColor": ["#FF3784", "#36A2EB", "#4BC0C0", "#F77825", "#9966FF"],
			   "data": (building_areas)
		   }]
	},
	   "options": {
			"title": {
				"display": True, 
				"text": "TCNJ Building Type (sq_ft)",
			},	   
			"plugins": {
			   "legend": False,
			   "outlabels": {
			   "text": "%l %p",
			   "color": "white",
			   "stretch": 15,
			   "font": {
			       "resizable": True,
			       "minSize": 8,
			       "maxSize": 12
			       }
			   }
		   }
	   }
	}

	params = {
	   'chart': json.dumps(config),
	   'width': 300,
	   'height': 250,
	   'backgroundColor': 'white'
	}
	
	# creating graphing url 	
	graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
	
	#try graph_url = graph_url to display graph image on my-form.html 
	return render_template('my-form.html', rows = rows, graph_url = graph_url)

''' *************************************************************
get specific month metrics
************************************************************* '''
@app.route('/metrics-month', methods = ['POST'])
def month_metrics():
	if (request.form['energy'] == 'ng_energy'):
		rows = connect('SELECT month, year, meter_name, cost, therms FROM ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' and cost is not null and therms is not null;')
		
		# ****************** therm chart creation ***********************
		chart_rows = connect('SELECT year, SUM(therms) FROM ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')

		# create arrays to hold year followed by therms
		years = [] # hold years
		therms = []	# hold therms
		for x in chart_rows:
			years.append (x[0])
			therms.append (x[1])

		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"label": 'Usage',
				"backgroundColor": 'navy',
				"borderColor": 'navy',
				"data": therms,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natural Gas Usage for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Therms'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		# ****************** cost chart creation ***********************
		chart_rows = connect('SELECT year, SUM(cost) FROM ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')

		cost = []
		for x in chart_rows:
			cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"label": 'Cost',
				"backgroundColor": 'green',
				"borderColor": 'green',
				"data": cost,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natural Gas Cost for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [
				{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
			
	elif (request.form['energy'] == 'el_energy'):	
		rows = connect('SELECT month, year, meter_name, cost, kwh FROM ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] + ' and cost is not null and kwh is not null;')

		chart_rows = connect('SELECT year, SUM(kwh) FROM ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')

		# create arrays to hold year followed by therms
		years = [] # years of each usage period
		kwh = []	# kwh used for each specific month
		for x in chart_rows:
			years.append (x[0])
			kwh.append (x[1])

		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"label": 'Usage',
				"backgroundColor": 'rgb(255, 202,0)',
				"borderColor": 'rgb(255, 202,0)',
				"data": kwh,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Usage for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [
				{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'kWh'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)

		chart_rows = connect('SELECT year, SUM(cost) FROM ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')

		cost = []
		for x in chart_rows:
			cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"label": 'Cost',
				"backgroundColor": 'green',
				"borderColor": 'green',
				"data": cost,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Cost for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [
				{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
			
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 250,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)

	return render_template('my-result.html', rows=rows, energy_graph_url=energy_graph_url, cost_graph_url = cost_graph_url)

''' *************************************************************
get specific year metrics
************************************************************* '''
@app.route('/metrics-year', methods = ['POST'])
def year_metrics():
	if (request.form['energy'] == 'ng_energy'):
		rows = connect('SELECT month, year, meter_name, cost, therms FROM ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' and cost is not null and therms is not null;')
		
		# ****************** therm chart creation ***********************
		chart_rows = connect('SELECT month, SUM(therms) FROM ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')

		# create arrays to hold year followed by therms
		months = [] # hold months
		therms = []	# hold therms
		for x in chart_rows:
			months.append (monthDict [str(x[0])])
			therms.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"label": 'Usage',
				"backgroundColor": 'navy',
				"borderColor": 'navy',
				"data": therms,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natural Gas Usage for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Month'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Therms'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		# ****************** cost chart creation ***********************
		chart_rows = connect('SELECT month, SUM(cost) FROM ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')

		cost = []
		for x in chart_rows:
			cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"label": 'Cost',
				"backgroundColor": 'green',
				"borderColor": 'green',
				"data": cost,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natural Gas Cost for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [
				{
					"scaleLabel": {
						"display": True,
						"labelString": 'Month'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)


	elif (request.form['energy'] == 'el_energy'):	
		rows = connect('SELECT month, year, meter_name, cost, kwh FROM ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] + ' and cost is not null and kwh is not null;')
		
		# ****************** therm chart creation ***********************
		chart_rows = connect('SELECT month, SUM(kwh) FROM ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')

		# create arrays to hold year followed by therms
		months = [] # hold months
		kwh = []	# hold therms
		
		for x in chart_rows:
			months.append (monthDict [str(x[0])])
			kwh.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"label": 'Usage',
				"backgroundColor": 'rgb(255, 202,0)',
				"borderColor": 'rgb(255, 202,0)',
				"data": kwh,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Usage for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Month'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'kWh'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		# ****************** cost chart creation ***********************
		chart_rows = connect('SELECT month, SUM(cost) FROM ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')

		cost = []
		for x in chart_rows:
			cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"label": 'Cost',
				"backgroundColor": 'green',
				"borderColor": 'green',
				"data": cost,
				"fill": "false",
			  }
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Cost for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [
				{
					"scaleLabel": {
						"display": True,
						"labelString": 'Month'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)	

	return render_template('my-result.html', rows=rows, energy_graph_url = energy_graph_url, cost_graph_url = cost_graph_url)



''' *************************************************************
get specific year & building type 
************************************************************* '''
@app.route ('/view-building-type-year', methods = ['POST'])
def building_type_year():
	if (request.form['energy'] == 'ng_energy'):
		rows = connect ('SELECT (' + request.form['b_type'] + '* (SELECT sum(cost) from ' + request.form['energy']+ ' where year = ' + request.form['year'] + ' and cost is not null and therms is not null)) as cost_result, (' + request.form['b_type'] + '* (SELECT sum(therms) from ' + request.form['energy'] + ' where year = ' + request.form['year'] + 'and cost is not null and therms is not null)) as therms_result from sq_ft_percentage;')

	# ****************** therm chart creation ***********************
		chart_rows = connect('SELECT month, SUM(therms), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(therms)) from ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')

		# create arrays to hold year followed by therms
		months = [] # hold years
		therms = []	# sum kwh
		building_therms = []
		for x in chart_rows:
			months.append (x[0])
			therms.append (x[1])
			building_therms.append (x[2])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "navy",
				"backgroundColor": 'navy',
				"fill": False,
				"data": therms
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "brown", 
				"data": building_therms	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natuaral Gas Usage for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Therms'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		chart_rows = connect('SELECT sum(cost), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(cost)) from ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')
		
		cost = []
		building_cost = [] 
		
		for x in chart_rows:
			cost.append (x[0])
			building_cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "navy",
				"backgroundColor": 'navy',
				"fill": False,
				"data": cost
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "green", 
				"data": building_cost	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natural Cost for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)

	elif (request.form['energy'] == 'el_energy'):
		rows = connect ('SELECT (' + request.form['b_type'] + '* (SELECT sum(cost) from ' + request.form['energy']+ ' where year = ' + request.form['year'] + ' and cost is not null and kwh is not null)) as cost_result, (' + request.form['b_type'] + '* (SELECT sum(kwh) from ' + request.form['energy'] + ' where year = ' + request.form['year'] + 'and cost is not null and kwh is not null)) as kwh_result from sq_ft_percentage;')

		chart_rows = connect('SELECT month, SUM(kwh), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(kwh)) from ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')

		# create arrays to hold year followed by therms
		months = [] # hold months
		kwh = []	# sum kwh
		building_kwh = []
		for x in chart_rows:
			months.append (x[0])
			kwh.append (x[1])
			building_kwh.append (x[2])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "navy",
				"backgroundColor": 'navy',
				"fill": False,
				"data": kwh
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "brown", 
				"data": building_kwh	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Energy Usage for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Therms'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		chart_rows = connect('SELECT sum(cost), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(cost)) from ' + request.form['energy'] + ' WHERE year = ' + request.form['year'] +' GROUP BY month ORDER BY month;')
		
		cost = []
		building_cost = [] 
		
		for x in chart_rows:
			cost.append (x[0])
			building_cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": months,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "navy",
				"backgroundColor": 'navy',
				"fill": False,
				"data": cost
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "green", 
				"data": building_cost	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electric Cost for ' + request.form['year'],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)

	return render_template('my-result.html', rows=rows, energy_graph_url = energy_graph_url, cost_graph_url = cost_graph_url)		

@app.route ('/view-building-type-month', methods = ['POST'])
def building_type_month():
	if (request.form['energy'] == 'ng_energy'):
		rows = connect ('SELECT (' + request.form['b_type'] + '* (SELECT sum(cost) from ' + request.form['energy']+ ' where month = ' + request.form['month'] + ' and cost is not null and therms is not null)) as cost_result, (' + request.form['b_type'] + '* (SELECT sum(therms) from ' + request.form['energy'] + ' where month = ' + request.form['month'] + 'and cost is not null and therms is not null)) as therms_result from sq_ft_percentage;')
	# ****************** therm chart creation ***********************
		chart_rows = connect('SELECT year, SUM(therms), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(therms)) from ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')

		# create arrays to hold year followed by therms
		years = [] # hold years
		therms = []	# sum kwh
		building_therms = []
		for x in chart_rows:
			years.append (x[0])
			therms.append (x[1])
			building_therms.append (x[2])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "navy",
				"backgroundColor": 'navy',
				"fill": False,
				"data": therms
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "brown", 
				"data": building_therms	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natuaral Gas Usage for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Therms'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		chart_rows = connect('SELECT sum(cost), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(cost)) from ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')
		
		cost = []
		building_cost = [] 
		
		for x in chart_rows:
			cost.append (x[0])
			building_cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "navy",
				"backgroundColor": 'navy',
				"fill": False,
				"data": cost
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "green", 
				"data": building_cost	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Natural Gas Cost for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)

	elif (request.form['energy'] == 'el_energy'):
		rows = connect ('SELECT (' + request.form['b_type'] + '* (SELECT sum(cost) from ' + request.form['energy']+ ' where month = ' + request.form['month'] + ' and cost is not null and kwh is not null)) as cost_result, (' + request.form['b_type'] + '* (SELECT sum(kwh) from ' + request.form['energy'] + ' where month = ' + request.form['month'] + 'and cost is not null and kwh is not null)) as kwh_result from sq_ft_percentage;')
		# ****************** therm chart creation ***********************
		chart_rows = connect('SELECT year, SUM(kwh), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(kwh)) from ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')

		# create arrays to hold year followed by therms
		years = [] # hold years
		kwh = []	# sum kwh
		building_kwh = []
		for x in chart_rows:
			years.append (x[0])
			kwh.append (x[1])
			building_kwh.append (x[2])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "rgb(255, 202, 0)",
				"backgroundColor": 'rgb(255, 202,0)',
				"fill": False,
				"data": kwh
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "brown", 
				"data": building_kwh	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Usage for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'kWh'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		# creating graphing url 	
		energy_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)
		
		chart_rows = connect('SELECT sum(cost), ((select ' + request.form['b_type'] + ' from sq_ft_percentage) * sum(cost)) from ' + request.form['energy'] + ' WHERE month = ' + request.form['month'] +' GROUP BY year ORDER BY year;')
		
		cost = []
		building_cost = [] 
		
		for x in chart_rows:
			cost.append (x[0])
			building_cost.append (x[1])
		
		config = {
		  "type": 'line',
		  "data": {
			"labels": years,
			"datasets": [
			  {
				"type": "line", 
				"label": "total usage",
				"borderColor": "rgb(255, 202, 0)",
				"backgroundColor": 'rgb(255, 202,0)',
				"fill": False,
				"data": cost
			  },
			{ 
				"type": "bar",
				"label": request.form['b_type'] + " usage",
				"backgroundColor": "green", 
				"data": building_cost	
			}
			],
		  },
		  "options": {
			"title": {
			  "display": "true",
			  "text": 'Electricity Cost for ' + monthDict[request.form['month']],
			},
			"scales": {
				"xAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'Year'
					}
				}],
				"yAxes": [{
					"scaleLabel": {
						"display": True,
						"labelString": 'USD'
					}
				}]				
			},
		  },
		}

		params = {
		   'chart': json.dumps(config),
		   'width': 300,
		   'height': 200,
		   'backgroundColor': 'white'
		}
		
		cost_graph_url = 'https://quickchart.io/chart?%s' % urlencode(params)

	return render_template('my-result.html', rows=rows, energy_graph_url = energy_graph_url, cost_graph_url = cost_graph_url)			

if __name__ == '__main__':
    app.run(debug = True)
