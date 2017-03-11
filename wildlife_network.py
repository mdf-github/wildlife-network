import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
import collections
import powerlaw

""" RELEVANT FUNCTIONS """
def get_dataframe(csv_name, csv_dir=os.getcwd()):
	"""Convert csv file to pandas dataframe for easy referencing"""
	datacsv = os.path.join(csv_dir, csv_name)
	# Note that country 'NA' should not be read as NaN; add keep_default_na=False
	df = pd.read_csv(datacsv, keep_default_na=False)
	
	# Subset the columns for what we need
	## selected_columns = ['Importer', 'Exporter', 'Importer reported quantity',
	## 					'Exporter reported quantity', 'Term', 'Unit',
	## 				]
	## df = df[selected_columns]

	## df = df.head(20)
	return df

def get_country_list(df, print_output=False):
	"""Get list of countries without duplicates."""
	importers = list(df['Importer'].unique())
	exporters = list(df['Exporter'].unique())

	all_countries = list(set(importers+exporters)) ## removes duplicates
	if print_output:
		print('Country list: ' + all_countries)
		print('Number of countries: ' + len(all_countries))

	return all_countries

def generate_weight():
	"""
	Useless function for now; still need to figure out how to compute weights
	"""
	return 1.0

def get_edge_list(add_weight=None):
	"""Get list of edges as (importer_country, exporter_country, weight)."""
	edge_list = []
	for index, row in df.iterrows():
		# directed edge format: (from, to, weight)
		if add_weight is None:
			weight = 1.0
		else:
			weight = generate_weight()	
		# Create the edge_list
		edge_tuple = (row['Importer'], row['Exporter'], weight )
		edge_list.append(edge_tuple)
		
	return edge_list

def degree_info(G):
	"""shamelessly copied from the jupyter notebooks"""
	# Add weight parameter to in-degree and out-degree
	in_degrees = G.in_degree(weight='weight')
	out_degrees = G.out_degree(weight='weight')

	fig_size= [18,13]

	#plt.rcParams["figure.figsize"] = fig_size
	plt.rcParams.update({'font.size': 22, "figure.figsize": fig_size})


	#Histogram of in-degrees, Plot and save to png
	plt.clf()
	plt.hist(in_degrees.values(), bins=300, normed=False)
	plt.title('In degree distribution')
	plt.savefig('in-degree.png')
	## plt.show()

	#Plot log-log of in-degree distribution
	plt.clf()
	plt.yscale('log') #set y scale to be log
	plt.xscale('log') #set x scale to be log
	#create a dictionary where key is degree and value is the number of times that degree is found
	#See the python collections Counter for more information 
	in_degree_counts = dict(collections.Counter(in_degrees.values())) 
	#Create scatter plot with degree on x-axis and counts on y-axis (red colour, x marker and size 150)
	plt.scatter(in_degree_counts.keys(), in_degree_counts.values(), c='r', marker='x', s=150)
	plt.xlim((.9, 1e3)) #set x axis limits
	plt.ylim((0, 1e3)) #set y axis limits
	plt.xlabel('degree')
	plt.ylabel('Frequency')
	plt.title('In-degree distribution')
	plt.savefig('indegree_loglog.png', dpi=400)
	## plt.show()

	fit = powerlaw.Fit(in_degree_counts.values())

	R, p = fit.distribution_compare('exponential','exponential',  normalized_ratio=True)
	print R, p
	R, p = fit.distribution_compare('power_law','lognormal',  normalized_ratio=True)
	print R, p
	R, p = fit.distribution_compare('exponential','power_law',  normalized_ratio=True)
	print R, p

	print fit.power_law.alpha
	print fit.power_law.xmin


	#Histogram of out-degrees, plot and save to png
	plt.clf()
	plt.hist(out_degrees.values(), bins=300, normed=False)
	plt.title('Out degree distribution')
	plt.savefig('out-degree.png')
	## plt.show()


	#Plot log-log of in-degree distribution
	plt.clf()
	plt.yscale('log') #set y scale to be log
	plt.xscale('log') #set x scale to be log
	#create a dictionary where key is degree and value is the number of times that degree is found
	#See the python collections Counter for more information 
	out_degree_counts = dict(collections.Counter(out_degrees.values())) 
	#Create scatter plot with degree on x-axis and counts on y-axis (green colour, o marker and size 150)
	plt.scatter(out_degree_counts.keys(), out_degree_counts.values(), c='g', marker='o', s=150)
	plt.xlim((.9, 1e3)) #set x axis limits
	plt.ylim((0, 1e3)) #set y axis limits
	plt.xlabel('degree')
	plt.ylabel('Frequency')
	plt.title('Out-degree distribution')
	## plt.show()
	plt.savefig('outdegree_loglog.png', dpi=400)


'''####### ACTUAL COMPUTATIONS START HERE #########'''

df = get_dataframe('ivory.csv')

# Create the directed graph
G = nx.DiGraph()

# Add nodes and edges
all_countries = get_country_list(df)
edge_list = get_edge_list()

G.add_nodes_from(all_countries)
G.add_weighted_edges_from(edge_list)

# Get degree distribution
degree_info(G)

# Draw
plt.clf()
nx.draw(G, with_labels=True)
plt.savefig('ivory_network.png', dpi=400)