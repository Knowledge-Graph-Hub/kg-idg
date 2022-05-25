#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A small script to produce subgraphs
(i.e., holdouts) for NEAT runs.
'''

import click  #type: ignore
from ensmallen import Graph #type: ignore

@click.command()
@click.option("--nodes",
               required=True,
               nargs=1,
               help="""The name of the graph node file to use as input.""")
@click.option("--edges",
               required=True,
               nargs=1,
               help="""The name of the graph edge file to use as input.""")
def run(nodes, edges):

    input_graph = Graph.from_csv(
        directed=False,
        node_path=nodes,
        edge_path=edges,
        verbose=True,
        nodes_column='id',
        node_list_node_types_column='category',
        default_node_type='biolink:NamedThing',
        sources_column='subject',
        destinations_column='object',
        edge_list_edge_types_column='predicate'
        )

    print("Generating training and validation subgraphs...")

    pos_train_edge_graph, pos_valid_edge_graph = input_graph.random_holdout(train_size=0.8)
    pos_valid_edge_graph.dump_edges("pos_valid_edges.tsv", edge_type_column='predicate')

    negative_graph = input_graph.sample_negatives(input_graph.get_edges_number())
    negative_graph = negative_graph.remove_disconnected_nodes()
    
    neg_train_edge_graph, neg_valid_edge_graph = negative_graph.random_holdout(train_size=0.8)
    neg_train_edge_graph.dump_edges("neg_train_edges.tsv", edge_type_column='predicate')
    neg_valid_edge_graph.dump_edges("neg_valid_edges.tsv", edge_type_column='predicate')

    print("Complete.")

if __name__ == '__main__':
  run()
