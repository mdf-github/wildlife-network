import networkx as nx
import pandas as pd

G = nx.read_gexf('test.gexf')

print(len(list(nx.strongly_connected_components(G))))
for graph in nx.strongly_connected_components(G):
	print graph

## print(len(list(nx.connected_components(nx.Graph(G)))))
## top_countries = ['US', 'CN', 'HK']

def fail(G): #a python function that will remove a random node from the graph G
	n = random.choice(G.nodes())  #pick a random node
	G.remove_node(n) # remove that random node, attached edges automatically removed.
	
def attack_degree(G): #remove node with maximum degree
	degrees = G.degree() # get dcitonary where key is node id, value is degree
	max_degree = max(degrees.values()) # find maximum degree value from all nodes
	max_keys = [k for k,v in degrees.items() if v==max_degree] #get all nodes who have the maximum degree (may be more than one)
	G.remove_node(max_keys[0]) #remove just the first node with max degree, we will remove others next
	
def attack_betweenness(G): #note - not currently used, but try it!
	betweenness = nx.betweenness_centrality(G) # get dictionary where key is node id and value is betweenness centrality
	max_betweenenss = max(betweenness.values()) # find maximum degree value from all nodes
	max_keys = [k for k,v in betweenness.items() if v==max_betweenness] #get all nodes who have the maximum degree (may be more than one)
	G.remove_node(max_keys[0]) #remove just the first node with max degree, we will remove others next

def attack_node(G, country):
	G.remove_node(country)

print('new')
for country in ['US', 'HK', 'CN']:
	G.remove_node(country)
	print(len(list(nx.strongly_connected_components(G))))




class GraphInfo(object):
	def __init__(self, G):
		self.G = G
		self.in_degrees = self.G.in_degree(weight='weight')
		self.out_degrees = self.G.out_degree(weight='weight')
		self.cent_dict = self.get_centrality_dict()
		self.bet_cen = nx.betweenness_centrality(G)
		self.clo_cen = nx.betweenness_centrality(G)
		self.eig_cen = nx.eigenvector_centrality(G)

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

		cen_df.to_csv('centrality_list_new.csv')

	## def get_components(self):

