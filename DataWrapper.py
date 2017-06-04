import networkx as nx
import json


class DataWrapper(object):
    def __init__(self, graph_path='data/dc_graph_final.txt',
                 data_path='data/hour_5_weekday_0_speed.json'):
        self._graph_file_path = graph_path
        self._data_file_path = data_path

    def data_wrapper(self):
        undi_g = self._load_graph()
        nodes_list = list(undi_g.nodes())
        nodes_map = dict()
        V = range(0, len(nodes_list))
        for i in V:
            nodes_map[nodes_list[i]] = i
        E = []
        edges_map = dict()
        for edge in undi_g.edges(data=True):
            u_i = nodes_map[edge[0]]
            v_i = nodes_map[edge[1]]
            tmc_id = edge[2]['tmc_id']
            edge__ = (u_i, v_i)
            edges_map[tmc_id] = edge__
            E.append(edge__)
        Obs = dict()
        with open(self._data_file_path) as f:
            for each_line in f.readlines():
                items_ = json.loads(each_line)
                tmc_id = items_['tmc']
                indicator = []
                for item_ in items_['data']:
                    if item_:
                        if item_[0][0] < 0.9 * item_[0][2]:
                            indicator.append(1)
                        else:
                            indicator.append(0)
                if len(indicator) != 44:
                    indicator = [0] * 44
                Obs[edges_map[tmc_id]] = indicator
        return V, E, Obs, undi_g

    def _load_graph(self):
        """
        :return: an undirected graph.
        """
        undi_g = nx.Graph()
        with open(self._graph_file_path) as f:
            all_lines = f.readlines()
            for each_line in all_lines[0:1383]:
                items_ = json.loads(each_line)
                (u, v) = items_['node: ']
                undi_g.add_node((u, v))
            for each_line in all_lines[1383:]:
                items_ = json.loads(each_line)
                node_i = (items_['u'][0], items_['u'][1])
                node_j = (items_['v'][0], items_['v'][1])
                id_ = items_['tmc']['tmc_id']
                undi_g.add_edge(node_i, node_j, tmc_id=id_)
        return undi_g

    @staticmethod
    def test_wrapper():
        dw = DataWrapper()
        V, E, Obs, G = dw.data_wrapper()
        print('number of nodes: {}'.format(len(V)))
        print('number of edges: {}'.format(len(E)))
        print('number of cc: {}'.format(nx.number_connected_components(G)))


def main():
    DataWrapper.test_wrapper()


if __name__ == '__main__':
    main()
