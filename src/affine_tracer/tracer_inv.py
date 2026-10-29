import numpy as np
import scipy
import networkx as nx
from icecream import ic
import copy

from .tracer import node, polytree, Split, NodesSum, NodesSub, RNodesSub, apply_linear_all

def lapply_linear_all(graph: nx.DiGraph, v):

    # sorted_list = list(nx.topological_sort(graph))


    # check if this is needed!!
    # first_empty_node = node(operator=1, operation=Id)
    # graph.add_node(first_empty_node)
    # graph.add_edge(first_empty_node, sorted_list[0])


    # sources = [n for n in graph.nodes() if graph.in_degree(n) == 0]
    # starting_node = [n for n in graph.nodes() if graph.in_degree(n) == 0][0]
    sorted_list = list(nx.topological_sort(graph))
    sink = sorted_list[-1]
    source = sorted_list[0]
    sink.value = v
    # v_app = v

    for node_local in reversed(sorted_list):
        if node_local.value is not None:
            node_local.operation.lapply_linear(node_local, graph)
        ic(node_local.tag)

        # come back to this!!!!
        # for ans in graph.predecessors(node_local):
        #     clear_node_value_nx(ans, graph)
    v_app = source.value
    graph_reset_nx(graph)
    return v_app
    

def apply_node(node, v):
    ic(v)
    v = node.operation.apply(node, v)
    node.value = v
    ic(v)

    if len(node.descendents) > 1:
        node.value = v
    if len(node.descendents) > 0:
        v = apply_node(node.descendents[0], v)
    return v

def graph_reset_nx(graph: nx.DiGraph):
    for node_local in graph.nodes:
        node_local.value = None
    pass


def clear_node_value_nx(node, graph):
    if node.val_use >= graph.out_degree(node):
        node.value = None
        # ic(node.tag)
        # ic('-----------------------------------')
    pass


def add_extranode(graph: polytree):

    m_graph = copy.deepcopy(graph)

    for node_local in m_graph.nodes:
        # ic(node_local.list_ans())
        ic(node_local.tag)

        if len(node_local.descendents) > 1:
            # node_local_dup = 
            new_node = node(operator = node_local.descendents, operation= Split, ancestors = [node_local])
            new_node.descendents = node_local.descendents
            m_graph.add_node(new_node)
            for node_des in node_local.descendents:
                ic(node_des.ancestors[0])
                ic(node_local)
                ic(new_node)
                ic(node_des.ancestors[0] == node_local)
                new_list = [new_node if nd_l==node_local else nd_l for nd_l in node_des.ancestors]
                ic(new_list)
                ic(node_des.ancestors)
                node_des.ancestors = new_list
                if node_des.operation == NodesSum:
                    if node_des.operator[0] == node_local:
                        node_des.operator[0] = new_node
                    if node_des.operator[1] == node_local:
                        node_des.operator[1] = new_node    
            node_local.descendents = [new_node]

            ic(node_local.tag)
            ic(new_node.tag)

        # graph.list_node_details()
        ic('-------------------')


    return m_graph

def to_nX(tracer: polytree):

    G = nx.DiGraph()
    id_list = set()
    for node_local in tracer.nodes:
        # ic(id_list)
        # ic(node_local.tag)
        # ic(nx.get_node_attributes(G, "label"))
        if node_local.tag not in id_list:
            G.add_node(node_local, label = node_local.tag)
            id_list.add(node_local.tag)
        for node_des in node_local.descendents:
            # ic(node_des.tag)
            if node_des.tag not in id_list:
                G.add_node(node_des, label = node_des.tag)
                id_list.add(node_des.tag)
            G.add_edge(node_local, node_des)
    G.graph["last_tag_val"] = tracer.tag_val

    return G

def add_extranode_nX(G: nx.DiGraph):
    
    m_graph = copy.deepcopy(G)
    last_id = m_graph.graph["last_tag_val"]
    ic(last_id)
    ic(chr(last_id))

    node_list = list(m_graph.nodes())
    for node_local in node_list:
        # ic(node_local.list_ans())
        ic(m_graph.nodes[node_local]["label"])

        list_successors = list(m_graph.successors(node_local))
        if len(list_successors) > 1:
            ic(m_graph.nodes[node_local]["label"])
            ic(list_successors)
            new_node = node(operator = list_successors, operation= Split, ancestors = [node_local], tag = chr(last_id))
            new_node.descendents = node_local.descendents
            m_graph.add_node(new_node, label = chr(last_id))
            last_id = last_id + 1

            m_graph.add_edge(node_local, new_node)

            for node_des in list_successors:
                m_graph.add_edge(new_node, node_des)
                m_graph.remove_edge(node_local, node_des)
                new_list = [new_node if nd_l==node_local else nd_l for nd_l in node_des.ancestors]
                node_des.ancestors = new_list
                if node_des.operation == NodesSum:
                    if node_des.operator[0] == node_local:
                        node_des.operator[0] = new_node
                    if node_des.operator[1] == node_local:
                        node_des.operator[1] = new_node  
                if node_des.operation == NodesSub:
                    if node_des.operator[0] == node_local:
                        node_des.operator[0] = new_node
                    if node_des.operator[1] == node_local:
                        node_des.operator[1] = new_node  
                if node_des.operation == RNodesSub:
                    if node_des.operator[0] == node_local:
                        node_des.operator[0] = new_node
                    if node_des.operator[1] == node_local:
                        node_des.operator[1] = new_node  

                
        #     # node_local_dup = 
        #     new_node = node(operator = node_local.descendents, operation= Split, ancestors = [node_local]) done
        #     new_node.descendents = node_local.descendents done
        #     m_graph.add_node(new_node) done
        #     for node_des in node_local.descendents:
        #         new_list = [new_node if nd_l==node_local else nd_l for nd_l in node_des.ancestors]
        #         node_des.ancestors = new_list
        #         if node_des.operation == NodesSum:
        #             if node_des.operator[0] == node_local:
        #                 node_des.operator[0] = new_node
        #             if node_des.operator[1] == node_local:
        #                 node_des.operator[1] = new_node    
        #     node_local.descendents = [new_node] done

        #     ic(node_local.tag)
        #     ic(new_node.tag)

        # graph.list_node_details()
            ic('-------------------')
            ic(node_local.operator)


    return m_graph

def func_VD_v2(V, tracer_M_nX):
    aft_VD = lapply_linear_all(tracer_M_nX, V)
    return aft_VD

def func_DV_v2(V, tracer_M):
    aft_DV = apply_linear_all(tracer_M, V.T)
    return aft_DV

def func_VSM_v2(V, tracer_G, tracer_M, tracer_M_nX):
    # val_dict['V'] = V
    tr1 = func_DV_v2(V, tracer_M).T
    tr_int = func_VD_v2(V, tracer_M_nX).T
    tr2 = apply_linear_all(tracer_G, tr_int)
    return tr1 + tr2.T

def func_VG_v2(V, A, tracer_M_nX):
    # This can still be optimised with tracer_G_rev
    egg_VG = V - (func_VD_v2(V , tracer_M_nX) @ A)
    return egg_VG

def func_VG_VSM_v2(V, A, tracer_G, tracer_M, tracer_M_nX):
    # val_dict['V'] = V
    common_term = func_VD_v2(V , tracer_M_nX)
    aft_VG = V - (common_term @ A)
    tr1 = func_DV_v2(V, tracer_M).T
    tr_int = common_term.T
    tr2 = apply_linear_all(tracer_G, tr_int)
    aft_VSM = tr1 + tr2.T
    return aft_VG, aft_VSM


# -----------------------------------CHECK IF THE FOLLOWING IS NEEDED-----------------------------------

# def swap_operation_old(G, node_local, depth):
#     # ic(node_local.tag)
    
#     if node_local.operation == NodesSum:
#         ic('here1')
#         ic(node_local.tag)
#         # des_list = nx.ancestors(G, node_local)
#         # ic(des_list)
#         # ic(list(G.predecessors(node_local)))
#         pred_list = list(G.predecessors(node_local))
#         # ic(list(pred_list))
#         comp_node = nx.lowest_common_ancestor(G, pred_list[0], pred_list[1])
#         for node_ans in pred_list:
#             # ic('------------')
#             # ic(node_ans.tag)
#             ans_list = nx.ancestors(G, node_ans) | {node_ans}
#             beyond_comp = nx.ancestors(G, comp_node)
#             ans_list_up_to_comp = (ans_list - beyond_comp) | {comp_node}
#             G_sub = nx.subgraph(G, ans_list_up_to_comp)
#             ic(node_ans.tag)
#             # labels = nx.get_node_attributes(G_sub, "label")
#             # nx.draw(G_sub, with_labels=True, labels=labels)
#             # plt.show()
#             # 
#             # sub_comp_node = swap_operation(G_sub, node_ans)
#             swap_operation_all(G_sub, depth=depth+1)
#         ic(depth)
#         ic(node_local.tag)
#         ic(node_local.operation)
#         ic(list(pred_list))
#         ic(comp_node.tag)
#         ic(node_local.operator[0].tag)
#         ic(node_local.tag)
#         ic('^^^^^^^^^^^^^^^^^^^^^^^^^')
#         path = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         try:    
#             # ---------------------path[1]-----------------should give me the correct order--------------------------especially useful for NodeSub and RNodeSub
#             ic(path[1].tag)
#             ic(path[-1].tag)
#         except:
#             pass
#         comp_node.operation = node_local.operation
#         node_local.operation = Split
#         next_node = list(G.predecessors(comp_node))[0]

#     elif node_local.operation == NodesSub:
#         # ic('here1')
#         # ic(node_local.tag)
#         # des_list = nx.ancestors(G, node_local)
#         # ic(des_list)
#         # ic(list(G.predecessors(node_local)))
#         pred_list = list(G.predecessors(node_local))
#         # ic(list(pred_list))
#         comp_node = nx.lowest_common_ancestor(G, pred_list[0], pred_list[1])
#         for node_ans in pred_list:
#             # ic('------------')
#             # ic(node_ans.tag)
#             ans_list = nx.ancestors(G, node_ans) | {node_ans}
#             beyond_comp = nx.ancestors(G, comp_node)
#             ans_list_up_to_comp = (ans_list - beyond_comp) | {comp_node}
#             G_sub = nx.subgraph(G, ans_list_up_to_comp)
#             # 
#             # sub_comp_node = swap_operation(G_sub, node_ans)
#             swap_operation_all(G_sub, depth=depth+1)
#         # ic(list(pred_list))
#         # ic(comp_node.tag)
#         # ic(node_local.operator[0].tag)
#         # ic(node_local.operator[1].tag)
#         # ic(node_local.tag)
#         # ic('^^^^^^^^^^^^^^^^^^^^^^^^^')
#         path0 = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         path1 = list(nx.shortest_path(G, comp_node, node_local.operator[1]))
#         # ic(path[0].tag)
#         for nodes in path0:
#             ic(nodes.tag)
#         for nodes in path1:
#             ic(nodes.tag)
#         try:    
#             # ---------------------path[1]-----------------should give me the correct order--------------------------especially useful for NodeSub and RNodeSub
#             ic(path0[1].tag)
#             ic(path1[1].tag)
#         except:
#             pass
#         comp_node.operation = node_local.operation
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         try:
#             comp_node.operator[0] = path0[1]
#         except:
#             comp_node.operator[0] = node_local
#         try:
#             comp_node.operator[1] = path1[1]
#         except:
#             comp_node.operator[1] = node_local
#         node_local.operation = Split
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         next_node = list(G.predecessors(comp_node))[0]

#     elif node_local.operation == RNodesSub:
#         # ic('here1')
#         # ic(node_local.tag)
#         # des_list = nx.ancestors(G, node_local)
#         # ic(des_list)
#         # ic(list(G.predecessors(node_local)))
#         pred_list = list(G.predecessors(node_local))
#         # ic(list(pred_list))
#         comp_node = nx.lowest_common_ancestor(G, pred_list[0], pred_list[1])
#         for node_ans in pred_list:
#             # ic('------------')
#             # ic(node_ans.tag)
#             ans_list = nx.ancestors(G, node_ans) | {node_ans}
#             beyond_comp = nx.ancestors(G, comp_node)
#             ans_list_up_to_comp = (ans_list - beyond_comp) | {comp_node}
#             G_sub = nx.subgraph(G, ans_list_up_to_comp)
#             # 
#             # sub_comp_node = swap_operation(G_sub, node_ans)
#             swap_operation_all(G_sub, depth=depth+1)
#         # ic(list(pred_list))
#         # ic(comp_node.tag)
#         # ic(node_local.operator[0].tag)
#         # ic(node_local.operator[1].tag)
#         # ic(node_local.tag)
#         # ic('^^^^^^^^^^^^^^^^^^^^^^^^^')
#         path0 = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         path1 = list(nx.shortest_path(G, comp_node, node_local.operator[1]))
#         # ic(path[0].tag)
#         for nodes in path0:
#             ic(nodes.tag)
#         for nodes in path1:
#             ic(nodes.tag)
#         try:    
#             # ---------------------path[1]-----------------should give me the correct order--------------------------especially useful for NodeSub and RNodeSub
#             ic(path0[1].tag)
#             ic(path1[1].tag)
#         except:
#             pass
#         comp_node.operation = node_local.operation
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         try:
#             comp_node.operator[0] = path0[1]
#         except:
#             comp_node.operator[0] = node_local
#         try:
#             comp_node.operator[1] = path1[1]
#         except:
#             comp_node.operator[1] = node_local
#         node_local.operation = Split
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         next_node = list(G.predecessors(comp_node))[0]

#     else:
#         # ic('here2')
#         try:
#             next_node = list(G.predecessors(node_local))[0]
#             # ic('££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££')
#             # ic(node_local.tag)
#             # ic(next_node.tag)
#             # ic(node_local.operation)
#         except:
#             next_node = None

#     # try:
#     #     ic(next_node.tag)
#     # except:
#     #     ic(next_node)
#     return next_node
        
# def swap_operation_all_old(G, depth):
#     # ic(depth)
#     # ic('Starting swap_op_all')
#     sorted_list = list(nx.topological_sort(G))
#     node_last = sorted_list[-1]
#     node_local = node_last

#     while node_local is not None:
#         # ic(node_local is None)
#         # ic(node_local is not None)
#         # ic('------------------------------------------------------------------------------')
#         # ic(node_local.tag)
#         # ic(node_local.operation)
#         node_local = swap_operation(G, node_local, depth)
#         # should I move to a different node after this?? - you do Disha, sari maadi nodu swalpa 
#         # try:
#         #     ic(node_local.tag)
#         #     ic('?????????????????????????????????????????????????????????????????????????')
#         # except:
#         #    ic('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
#         #    ic(node_local is None)

#     # try:
#     #     ic(node_local.tag) 
#     # except:       
#     #     ic('done here')
#     # ic('wtf is happening here')

#     return 0

# def swap_operation(G, node_local, depth):
#     # ic(node_local.tag)
    
#     if node_local.operation == NodesSum:
#         # ic('here1')
#         # ic(node_local.tag)
#         # des_list = nx.ancestors(G, node_local)
#         # ic(des_list)
#         # ic(list(G.predecessors(node_local)))
#         pred_list = list(G.predecessors(node_local))
#         # ic(list(pred_list))
#         comp_node = nx.lowest_common_ancestor(G, pred_list[0], pred_list[1])

#         ic(depth)
#         ic(node_local.tag)
#         ic(node_local.operation)
#         ic(list(pred_list))
#         ic(comp_node.tag)
#         ic(node_local.operator[0].tag)
#         ic(node_local.tag)
#         ic('^^^^^^^^^^^^^^^^^^^^^^^^^')
#         # path = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         # try:    
#         #     # ---------------------path[1]-----------------should give me the correct order--------------------------especially useful for NodeSub and RNodeSub
#         #     ic(path[1].tag)
#         #     ic(path[-1].tag)
#         # except:
#         #     pass
#         comp_node.operation = node_local.operation
#         path0 = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         path1 = list(nx.shortest_path(G, comp_node, node_local.operator[1]))
#         # ic(path[0].tag)
#         try:
#             comp_node.operator[0] = path0[1]
#         except IndexError:
#             comp_node.operator[0] = node_local
#         try:
#             comp_node.operator[1] = path1[1]
#         except IndexError:
#             comp_node.operator[1] = node_local
#         node_local.operation = Split
#         # next_node = list(G.predecessors(comp_node))[0]
#         comp_node.swap = True
#         node_local.swap = True

#     elif node_local.operation == NodesSub:
#         # ic('here1')
#         # ic(node_local.tag)
#         # des_list = nx.ancestors(G, node_local)
#         # ic(des_list)
#         # ic(list(G.predecessors(node_local)))
#         pred_list = list(G.predecessors(node_local))
#         # ic(list(pred_list))
#         ic(node_local.tag)
#         for nl in pred_list:
#             ic(nl.tag)
#         comp_node = nx.lowest_common_ancestor(G, pred_list[0], pred_list[1])

#         # ic(list(pred_list))
#         # ic(comp_node.tag)
#         # ic(node_local.operator[0].tag)
#         # ic(node_local.operator[1].tag)
#         # ic(node_local.tag)
#         # ic('^^^^^^^^^^^^^^^^^^^^^^^^^')
#         path0 = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         path1 = list(nx.shortest_path(G, comp_node, node_local.operator[1]))
#         # ic(path[0].tag)
#         for nodes in path0:
#             ic(nodes.tag)
#         for nodes in path1:
#             ic(nodes.tag)
#         try:    
#             # ---------------------path[1]-----------------should give me the correct order--------------------------especially useful for NodeSub and RNodeSub
#             ic(path0[1].tag)
#             ic(path1[1].tag)
#         except:
#             pass
#         comp_node.operation = node_local.operation
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         try:
#             comp_node.operator[0] = path0[1]
#         except IndexError:
#             comp_node.operator[0] = node_local
#         try:
#             comp_node.operator[1] = path1[1]
#         except IndexError:
#             comp_node.operator[1] = node_local
#         node_local.operation = Split
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         # next_node = list(G.predecessors(comp_node))[0]
#         comp_node.swap = True
#         node_local.swap = True

#     elif node_local.operation == RNodesSub:
#         # ic('here1')
#         # ic(node_local.tag)
#         # des_list = nx.ancestors(G, node_local)
#         # ic(des_list)
#         # ic(list(G.predecessors(node_local)))
#         pred_list = list(G.predecessors(node_local))
#         # ic(list(pred_list))
#         comp_node = nx.lowest_common_ancestor(G, pred_list[0], pred_list[1])

#         # ic(list(pred_list))
#         # ic(comp_node.tag)
#         # ic(node_local.operator[0].tag)
#         # ic(node_local.operator[1].tag)
#         # ic(node_local.tag)
#         # ic('^^^^^^^^^^^^^^^^^^^^^^^^^')
#         path0 = list(nx.shortest_path(G, comp_node, node_local.operator[0]))
#         path1 = list(nx.shortest_path(G, comp_node, node_local.operator[1]))
#         # ic(path[0].tag)
#         for nodes in path0:
#             ic(nodes.tag)
#         for nodes in path1:
#             ic(nodes.tag)
#         try:    
#             # ---------------------path[1]-----------------should give me the correct order--------------------------especially useful for NodeSub and RNodeSub
#             ic(path0[1].tag)
#             ic(path1[1].tag)
#         except:
#             pass
#         comp_node.operation = node_local.operation
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         try:
#             comp_node.operator[0] = path0[1]
#         except IndexError:
#             comp_node.operator[0] = node_local
#         try:
#             comp_node.operator[1] = path1[1]
#         except IndexError:
#             comp_node.operator[1] = node_local
#         node_local.operation = Split
#         ic(comp_node.operator[0].tag)
#         ic(comp_node.operator[1].tag)
#         # next_node = list(G.predecessors(comp_node))[0]
#         comp_node.swap = True
#         node_local.swap = True

#     else:
#         pass
#         # ic('here2')
#         # try:
#         #     next_node = list(G.predecessors(node_local))[0]
#         #     # ic('££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££')
#         #     # ic(node_local.tag)
#         #     # ic(next_node.tag)
#         #     # ic(node_local.operation)
#         # except:
#         #     next_node = None

#     # try:
#     #     ic(next_node.tag)
#     # except:
#     #     ic(next_node)
#     pass
        
# def swap_operation_all(G, depth):
#     visit_order = list(reversed(list(nx.topological_sort(G))))
#     # ic(depth)
#     # ic('Starting swap_op_all')
#     # sorted_list = list(nx.topological_sort(G))
#     # node_last = sorted_list[-1]
#     # node_local = node_last


#     for node_local in visit_order:
#         if not getattr(node_local, 'swap', False):

#             # ic(node_local is None)
#             # ic(node_local is not None)
#             # ic('------------------------------------------------------------------------------')
#             # ic(node_local.tag)
#             # ic(node_local.operation)
#             ic(node_local.tag)
#             swap_operation(G, node_local, depth)
#             # should I move to a different node after this?? - you do Disha, sari maadi nodu swalpa 
#             # try:
#             #     ic(node_local.tag)
#             #     ic('?????????????????????????????????????????????????????????????????????????')
#             # except:
#             #    ic('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
#             #    ic(node_local is None)

#         # try:
#         #     ic(node_local.tag) 
#         # except:       
#         #     ic('done here')
#         # ic('wtf is happening here')

#     return 0

# def preprocess_tracer(tracer: polytree):
#     nxG = to_nX(tracer)
#     m_graph = add_extranode_nX(nxG)
#     swap_operation_all(m_graph, depth = 0)
#     r_graph = m_graph.reverse()
#     return r_graph