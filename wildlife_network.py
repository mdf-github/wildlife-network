import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
import collections
import powerlaw

""" RELEVANT FUNCTIONS """

class FullDataFrame(object):
	"""Methods to extract the original (all data) CSV file."""
	def __init__(self, csv_name, csv_dir=os.getcwd()):
		self.csv_name = csv_name
		self.csv_dir = csv_dir
		self.csv_name_root = os.path.splitext(self.csv_name)[0]
		self.df = self.set_dataframe()

	def set_dataframe(self, new_df=None):
		"""Overwrites the variable df. Useful for filtering."""
		if new_df is None:
			df = self.get_dataframe()
		else:
			df = new_df
		return df

	def get_dataframe(self):
		"""Convert full csv file to pandas dataframe for easy referencing"""
		csv_dir = self.csv_dir
		csv_name = self.csv_name		
		datacsv = os.path.join(csv_dir, csv_name)
		# Note that country 'NA' should not be read as NaN
		# Add keep_default_na=False, and only read empty cells as NaN
		df = pd.read_csv(datacsv, keep_default_na=False, na_values=[''])
		
		return df

class CountryDataFrame(object):
	"""
	Methods for a particular dataframe. The dataframe can be derived
	from an instance of FullDataFrame.
	"""
	def __init__(self, df, csv_name_root='test', csv_dir=os.getcwd()):
		self.df = df
		self.csv_name_root = csv_name_root
		self.csv_dir = csv_dir

	def get_country_list(self, years=None, print_output=False):
		"""Get list of countries without duplicates."""
		df = self.df

		if years is not None:
			df = df[df['Year'].isin(years)]

		importers = list(df['Importer'].unique())
		exporters = list(df['Exporter'].unique())

		all_countries = list(set(importers+exporters)) ## removes duplicates
		if print_output:
			print('Country list: ' + all_countries)
			print('Number of countries: ' + len(all_countries))

		return all_countries	

	def get_years(self):
		df = self.df
		years = sorted(list(df['Year'].unique()))
		return years

	## def get_country_node_info(self, years=None):
	## 	"""
	## 	Output node information.
	## 	Format: {node: [year1, year2, ...]}
	## 	"""
	## 	if years is None:
	## 		years = self.get_years()

	## 	for year in years:
	## 		country_list = self.get_country_list(years=[year])

	def create_df_by_imex(self):
		"""Create new DataFrame showing net imports and exports."""
		df = self.df

		years = self.get_years()
		new_df = pd.DataFrame()
		new_df['Country'] = self.get_country_list()

		for index, row in new_df.iterrows():
			country = row['Country']
			# Get the total counts
			total_imports = len(df[df['Importer'] == country])
			total_exports = len(df[df['Exporter'] == country])
			new_df.loc[index, 'Total imports'] = total_imports
			new_df.loc[index, 'Total exports'] = total_exports
			new_df.loc[index, 'Net imports'] = total_imports - total_exports

			# Get the counts per year
			for year in years:
				col_name = {}
				col_name['im'] = str(year) + '_import_counts'
				col_name['ex'] = str(year) + '_export_counts'
				col_name['net'] = str(year) + '_net_import_counts'

				# Subset the data by year
				df_sub = df[df['Year'] == year]

				# Count import/export frequency
				counts = {}
				counts['im'] = len(df_sub[df_sub['Importer'] == country])
				counts['ex'] = len(df_sub[df_sub['Exporter'] == country])
				counts['net'] = counts['im'] - counts['ex']

				# Create the import and export frequency columns
				for label in col_name.iterkeys():
					new_df.loc[index, col_name[label]] = counts[label] 

		# Write to  CSV
		filename = '{csvname}_imex.csv'.format(csvname=self.csv_name_root)
		new_df.to_csv(os.path.join(self.csv_dir, filename))

class ImportExportPairs(object):
	"""Get information on import/export pairs."""

	def __init__(self, df, weight_scheme='freq'):
		self.df = df
		self.weight_scheme = weight_scheme
		self.imex_freq_dict = self.get_imex_freq_dict()

		self.imex_weight_dict = self.get_imex_weight_dict()
		self.edge_list = self.get_weighted_edge_list()

	def get_imex_freq_dict(self):
		"""
		Gets frequencies of trade as a dictionary:
		{(importer_country, exporter_country): freq}
		"""
		df = self.df

		imex_freq_dict = {} ## {(importer, exporter): freq}
		imex_freq_tuples = [] ## [(importer, exporter, freq), ...]
		for index, row in df.iterrows(): ## directed edge format: (from, to, weight)
			importer = row['Importer']
			exporter = row['Exporter']

			imex_tuple = (importer, exporter)
			if imex_tuple not in imex_freq_dict.iterkeys():
				freq = 1
			else:
				freq = imex_freq_dict[imex_tuple] + 1 ## increment the frequency by 1

			# Update the dictionary
			imex_freq_dict[imex_tuple] = freq

		return imex_freq_dict

	def get_imex_weight_dict(self):
		"""
		Gets weights as a dictionary:
		{(importer_country, exporter_country): weight}.
		Relatively simple function, but allows us to decouple weights from
		frequencies if necessary.
		"""
		imex_weight_dict = {}
		for imex_tuple, freq in self.imex_freq_dict.iteritems():
			importer, exporter = imex_tuple
			if self.weight_scheme is None:
				weight = 1.0
			if self.weight_scheme == 'freq':
				weight = freq

			imex_weight_dict[imex_tuple] = weight

		return imex_weight_dict

	def get_weighted_edge_list(self):
		"""
		Creates edge list with weights for adding into graph.
		By default, weight scheme is by frequency.
		"""
		edge_list = []

		for imex_tuple, weight in self.imex_weight_dict.iteritems():
			importer, exporter = imex_tuple
			edge_list.append( (importer, exporter, weight) )

		return edge_list

class GraphInfo(object):
	def __init__(self, countrydf, graphtype='digraph'):
		"""
		Inherit instance of CountryDataFrame
		(we won't inherit the class, seems more complicated).
		"""
		self.df = countrydf
		self.G = self.make_graph(graphtype)
		self.in_degrees = self.G.in_degree(weight='weight')
		self.out_degrees = self.G.out_degree(weight='weight')
		self.cent_dict = self.get_centrality_dict()
		self.bet_cen = nx.betweenness_centrality(G)
		self.clo_cen = nx.betweenness_centrality(G)
		self.eig_cen = nx.eigenvector_centrality(G)

	def make_graph(self, graphtype):
		if graphtype == 'digraph':
			self.G = nx.DiGraph()
		elif graphtype == 'multidigraph':
			self.G = nx.MultiDiGraph()

	def add_nodes(self, nodelist):
		years = countrydf.get_years()
		df_sub = df[df['Year'] == year]
		for year in years:
			countrylist = df_sub['Importer']
		

	def get_centrality_dict(self):
		cent_dict = {}
		cent_dict['bet'] = nx.betweenness_centrality(G)
		cent_dict['clo'] = nx.closeness_centrality(G)
		cent_dict['eig'] = nx.eigenvector_centrality(G)

		return cent_dict

	def get_centrality_csv(self):
		cen_df = pd.DataFrame()
		nodelist = G.nodes()

		cen_df['Country'] = nodelist

		for index, row in cen_df.iterrows():
			country = row['Country']
			for label in ['bet', 'clo', 'eig']:
				cen_df.loc[index, label] = self.cent_dict[label][country]

		cen_df.to_csv('centrality_list.csv')

	def plot_degree_files(self):
		in_degrees = self.in_degrees
		out_degrees = self.out_degrees

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
		plt.clf()

'''####### ACTUAL COMPUTATIONS START HERE #########'''

data = FullDataFrame('ivory.csv')
df = CountryDataFrame(data.df, csv_name_root='test') 

cdf.create_df_by_imex()

# Create a weighted edge
weight_scheme = 'freq'
imex_pairs = ImportExportPairs(df, weight_scheme=weight_scheme)

## # Create the directed graph
## graph_info = GraphInfo(df)

## # Add nodes and edges
## G.add_nodes_from(data.get_country_list())
## G.add_weighted_edges_from(imex_pairs.edge_list)

## # Get degree distribution
## graph_info = GraphInfo(G)
## ## graph_info.plot_degree_files()
## graph_info.get_centrality_csv()




# Draw
## plt.clf()
## nx.draw(G, with_labels=True)
## plt.savefig('ivory_network.png', dpi=400)
## plt.close()

## add country list output
## get G