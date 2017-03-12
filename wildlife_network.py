import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import os
import collections
import powerlaw

""" RELEVANT FUNCTIONS """

class CountryDataFrame(object):
	"""
	Class containing information about the raw CSV data.
	Recommended for pandas-only manipulation (no networkx).
	"""
	def __init__(self, csv_name, csv_dir=os.getcwd()):
		self.csv_name = csv_name
		self.csv_dir = csv_dir
		self.df = self.get_dataframe()
		self.all_countries = self.get_country_list()

	def get_dataframe(self):
		csv_dir = self.csv_dir
		csv_name = self.csv_name

		"""Convert csv file to pandas dataframe for easy referencing"""
		datacsv = os.path.join(csv_dir, csv_name)
		# Note that country 'NA' should not be read as NaN; add keep_default_na=False
		# Only read empty cells as NaN
		df = pd.read_csv(datacsv, keep_default_na=False, na_values=[''])
		
		# Subset the columns for what we need
		## selected_columns = ['Importer', 'Exporter', 'Importer reported quantity',
		## 					'Exporter reported quantity', 'Term', 'Unit',
		## 				]
		## df = df[selected_columns]

		## df = df.head(20)
		return df

	def get_country_list(self, print_output=False):
		"""Get list of countries without duplicates."""
		df = self.df

		importers = list(df['Importer'].unique())
		exporters = list(df['Exporter'].unique())

		all_countries = list(set(importers+exporters)) ## removes duplicates
		if print_output:
			print('Country list: ' + all_countries)
			print('Number of countries: ' + len(all_countries))

		return all_countries

	def create_df_by_imex(self):
		"""Create new DataFrame showing net imports and exports."""
		df = self.df

		years = sorted(list(df['Year'].unique()))
		new_df = pd.DataFrame()
		new_df['Country'] = self.all_countries
		for year in years:
			new_df[str(year) + '_import_counts'] = None
			new_df[str(year) + '_import_counts'] = None

		for year in years:		
			im_col_name = str(year) + '_import_counts'
			ex_col_name = str(year) + '_export_counts'
			for index, row in new_df.iterrows():
				country = row['Country']
				df_sub = df[df['Year'] == year]

				im_count = len(df_sub[df_sub['Importer'] == country])
				ex_count = len(df_sub[df_sub['Exporter'] == country])

				new_df.loc[index, im_col_name] = im_count
				new_df.loc[index, ex_col_name] = ex_count

		# Write to  CSV
		filename = '{csvname}_imex.csv'.format(csvname=self.csv_name)
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
		Gets weighted list of edges as (importer_country, exporter_country, weight).
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
		"""Gets weights."""
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


class DegreeInfo(object):
	def __init__(self, G):
		self.in_degrees = G.in_degree(weight='weight')
		self.out_degrees = G.out_degree(weight='weight')

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

data = CountryDataFrame('ivory.csv')
df = data.df
data.create_df_by_imex()

imex_pairs = ImportExportPairs(df, weight_scheme=None)

# Create the directed graph
G = nx.DiGraph()

# Add nodes and edges
G.add_nodes_from(data.all_countries)
G.add_weighted_edges_from(imex_pairs.edge_list)

# Get degree distribution
degree_info = DegreeInfo(G)
degree_info.plot_degree_files()

# Draw
plt.clf()
nx.draw(G, with_labels=True)
plt.savefig('ivory_network.png', dpi=400)
plt.close()