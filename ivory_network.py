import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os

# Relevant functions
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

	df = df.head(20)
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


'''####### CODE STARTS HERE #########'''

df = get_dataframe('ivory.csv')

# Create the directed graph
G = nx.DiGraph()

# Add countries as nodes
all_countries = get_country_list(df)
edge_list = get_edge_list()

G.add_nodes_from(all_countries)
G.add_weighted_edges_from(edge_list)

# Draw
nx.draw(G, with_labels=True)
plt.show()