import networkx as nx
#import matplotlib.pyplot as plt

from lib2to3.pytree import Node
from os import execlp, startfile
from posixpath import pathsep
from re import I, L, S
import sys
from collections import defaultdict
from RailML.RailTopoModel.IntrinsicCoordinate import IntrinsicCoordinate
from RailML.XML_tools import *

arrow = {1:[0,1,0,0,1,1,0,0,0,1,1],
         2:[0,0,0,0,1,1,1],
         3:[0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,0,1,0,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,0],
         4:[0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,1,1,0,0,0,1,0,1,1,1],
         5:[0,0,0,0,1,1,1,1],
         6:[0,0,0,0,0,0,0,0,0,1,1],
         7:[0,1,1,0,1,1,0],
         8:[0,1,1,0,0],
         9:[0,0,0,0,0,0,0]}

#%%%
RML_old = railML.railML()

def RNA(RML,INPUT_FILE,OUTPUT_FILE,auto = True, test = False, config = [1,1,1,1,1,1,200,200],example = 1):
    
    sequence = [">" if track == 0 else "<" for track in arrow[example] ]
    print(f'{sequence}')

    if test:
        print("#"*50+" Starting Railway Network Analyzer "+"#"*50)
    
    if test:
        print("Reading .railML file")
    
    root = load_xml(INPUT_FILE)   #A RELATIVE PATH DOESN'T WORK FOR PREVIEW!
    
    if auto:
        ignore = {None}
    else:
        ignore = {"SignalsIS","SignalsIL","Routes"}

    if test:
        print("Creating railML object")
    get_branches(RML,root,ignore = ignore,test = False )
    
    get_branches(RML_old,root,ignore = {None},test = False )
    
    print("Reading old interlocking table")
    try:
        old_table,switch_net,platform_net,levelCrossing_net,scissorCrossing_net = get_old_interlocking_table(RML_old,example)
    except:
        old_table = {}
        switch_net = {}
        platform_net = {}
        levelCrossing_net = {}
        scissorCrossing_net = {}
        print("No interlocking table found")
        #return

    if ignore != {None}:
        delete_signal_visual(RML)
    
    if test:
        print("Analyzing railML object")

    distanceParameters = {
        'bufferStopDistance': 100,
        'lineBordersDistance': 100,
        'railJointsDistance': 200,
        'levelCrossingsDistance': 250,
        'platformsDistance': 300
    }
    
    x = analyzing_object(RML,sequence,switch_net,platform_net,levelCrossing_net,scissorCrossing_net,distanceParameters,old_table,example,config)
    
    # Create new signalling
    
    print("Exporting .railML file")
    with open(OUTPUT_FILE, "w" , encoding="utf-8") as f:        
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<railML xmlns="https://www.railml.org/schemas/3.1" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:gml="http://www.opengis.net/gml/3.2/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.railml.org/schemas/3.1 https://www.railml.org/schemas/3.1/railml3.xsd" version="3.1">\n')

        save_xml(RML,f,ignore = {None}, test = False)
        f.close()

    try:
        raimlFile = load_xml(OUTPUT_FILE)
        print(f'railML file syntax validated: {raimlFile}')
    except:
        print('railML file corrupted')
    return x

def get_old_interlocking_table(object,example):

    old_table = {}

    signals_net = {}
    switch_net = {}
    levelCrossing_net = {}
    platform_net = {}
    scissorCrossing_net = {}
    
    try:
        if object.Infrastructure.FunctionalInfrastructure.SignalsIS != None:
            for signal in object.Infrastructure.FunctionalInfrastructure.SignalsIS.SignalIS:
                #print(signal.Name[0].Name,signal.SpotLocation[0].NetElementRef)
                signals_net[signal.Name[0].Name] = {'net':signal.SpotLocation[0].NetElementRef}

            for signal in object.Infrastructure.InfrastructureVisualizations.Visualization:
                for x in signal.SpotElementProjection:
                    ref = x.RefersToElement
                    name = x.Name[0].Name
                    if 'sig' in ref:
                        signals_net[name] |= {'x': int(x.Coordinate[0].X.split('.')[0])}
    except:
        signals_net = {}

    #print(signals_net)

    try:
        if object.Infrastructure.FunctionalInfrastructure.LevelCrossingsIS != None:
            for levelCrossing in object.Infrastructure.FunctionalInfrastructure.LevelCrossingsIS[0].LevelCrossingIS:
                #print(signal.Name[0].Name,signal.SpotLocation[0].NetElementRef)
                levelCrossing_net[levelCrossing.Name[0].Name] = {'net':levelCrossing.SpotLocation[0].NetElementRef}

            for levelCrossing in object.Infrastructure.InfrastructureVisualizations.Visualization:
                for x in levelCrossing.SpotElementProjection:
                    name = x.Name[0].Name
                    if 'Lc' in name:
                        levelCrossing_net[name] |= {'x': int(x.Coordinate[0].X.split('.')[0]),'y': int(x.Coordinate[0].Y.split('.')[0])}
    except:
        levelCrossing_net = {}
    #print(levelCrossing_net)

    try:           
        if object.Infrastructure.FunctionalInfrastructure.Platforms != None:
            for platform in object.Infrastructure.FunctionalInfrastructure.Platforms[0].Platform:
                #print(signal.Name[0].Name,signal.SpotLocation[0].NetElementRef)
                platform_net[platform.Name[0].Name] = {'net':platform.LinearLocation[0].AssociatedNetElement[0].NetElementRef}

            for platform in object.Infrastructure.InfrastructureVisualizations.Visualization:
                for x in platform.SpotElementProjection:
                    name = x.Name[0].Name
                    if 'Plat' in name:
                        platform_net[name] |= {'x': int(x.Coordinate[0].X.split('.')[0])}
    except:
        platform_net = {}
    #print(platform_net)

    try:
        if object.Infrastructure.FunctionalInfrastructure.SwitchesIS != None:
            for switch in object.Infrastructure.FunctionalInfrastructure.SwitchesIS[0].SwitchIS:
                type = switch.Type
                
                if type == "ordinarySwitch":
                    main = switch.SpotLocation[0].NetElementRef
                    left = switch.LeftBranch[0].NetRelationRef.split('_')[1].replace(main,'')
                    left_radius = switch.LeftBranch[0].Radius
                    right = switch.RightBranch[0].NetRelationRef.split('_')[1].replace(main,'')

                    normal = right if '-' in left_radius else left
                    reverse = left if '-' in left_radius else right

                    switch_net[switch.Name[0].Name] = {'type':'simple','main':main,'normal':normal,'reverse':reverse}
    
                if type == "doubleSwitchCrossing":
                    main = switch.SpotLocation[0].NetElementRef
                    straight_1,straight_2 = switch.StraightBranch[0].NetRelationRef.split('_')[1].split('ne')[1:]
                    straight_3,straight_4 = switch.StraightBranch[1].NetRelationRef.split('_')[1].split('ne')[1:]
                    turning_1,turning_2 = switch.TurningBranch[0].NetRelationRef.split('_')[1].split('ne')[1:]
                    turning_3,turning_4 = switch.TurningBranch[1].NetRelationRef.split('_')[1].split('ne')[1:]

                    #print(f'{straight_1} to {straight_2} | {straight_3} to {straight_4} || {turning_1} to {turning_2} | {turning_3} to {turning_4}')

                    # RR NN RN NR
                    # RR NN RN NR

                    applicationDirection = switch.SpotLocation[0].ApplicationDirection
                    radius_int = int(switch.TurningBranch[0].Radius)

                    #switch_net[switch.Name[0].Name] = {'type':'double','Movement_RR':['ne'+straight_1,'ne'+straight_2],'Movement_NN':['ne'+straight_3,'ne'+straight_4],'Movement_RN':['ne'+turning_3,'ne'+turning_4],'Movement_NR':['ne'+turning_1,'ne'+turning_2]}
                    
                    if ((applicationDirection == "reverse" and radius_int > 0) or (applicationDirection == "normal" and radius_int < 0)):
                        switch_net[switch.Name[0].Name] = {'type':'double','Movement_RR':['ne'+straight_1,'ne'+straight_2],'Movement_NN':['ne'+straight_3,'ne'+straight_4],'Movement_RN':['ne'+turning_3,'ne'+turning_4],'Movement_NR':['ne'+turning_1,'ne'+turning_2]}
                    else:
                        switch_net[switch.Name[0].Name] = {'type':'double','Movement_RR':['ne'+straight_1,'ne'+straight_2],'Movement_NN':['ne'+straight_3,'ne'+straight_4],'Movement_RN':['ne'+turning_1,'ne'+turning_2],'Movement_NR':['ne'+turning_3,'ne'+turning_4]}
                    
    except:
        switch_net = {}
    #for i in switch_net:
    #    print(f'sw {i} {switch_net[i]}')

    try:
        if object.Infrastructure.FunctionalInfrastructure.Crossings != None:
            for scissorCrossing in object.Infrastructure.FunctionalInfrastructure.Crossings[0].Crossing:
                scissorCrossing_net[scissorCrossing.Name[0].Name] = {'net':[]}
                for i in scissorCrossing.External:
                    aux = i.Ref.split('_')[1].split('ne')
                    element_A = f'ne{aux[1]}'
                    element_B = f'ne{aux[2]}'
                    scissorCrossing_net[scissorCrossing.Name[0].Name]['net'].append(element_A)
                    scissorCrossing_net[scissorCrossing.Name[0].Name]['net'].append(element_B)

            #for scissorCrossing in object.Infrastructure.InfrastructureVisualizations.Visualization:
            #    for x in scissorCrossing.SpotElementProjection:
            #        name = x.Name[0].Name
            #        if 'Lc' in name:
            #            levelCrossing_net[name] |= {'x': int(x.Coordinate[0].X.split('.')[0])}
    except:
        scissorCrossing_net = {}

    try:
        i = 0
        for route in object.Interlocking.AssetsForIL[0].Routes.Route:
            #print(object.Interlocking.AssetsForIL[0].Routes.Route[i])
            i = i + 1
            signals = route.Designator[0].Entry[6:]
            #print(signals,signals.split(' ')[0].split('-'))
            [signal_start,signal_end] = signals.split(' ')[0].split('-')[:2]
            [net_start,net_end]         = [signals_net[signal_start]['net'],signals_net[signal_end]['net']]

            #print(signals,signal_start,signal_end)
            way = ">>" if signals_net[signal_start]['x'] < signals_net[signal_end]['x'] else "<<"

            if (example == 3 and i == 33):
                way = "<<"
                
            old_table[i] = {'signal_start':signal_start,'signal_end':signal_end,'net_start':net_start,'net_end':net_end,'way':way}

            if net_start != net_end:
                if ' ' in signals:
                    switch = signals.split(' ')[1]
                    #print(switch[1:-1])
                    old_table[i] |= {'switch':switch[1:-1]}

            for platform in platform_net:
                if platform_net[platform]['net'] == net_start or platform_net[platform]['net'] == net_end:
                    if way == ">>":
                        if signals_net[signal_start]['x'] < platform_net[platform]['x'] and signals_net[signal_end]['x'] > platform_net[platform]['x']:
                            old_table[i] |= {'platform':platform}
                    else:
                        if signals_net[signal_start]['x'] > platform_net[platform]['x'] and signals_net[signal_end]['x'] < platform_net[platform]['x']:
                            old_table[i] |= {'platform':platform}

            for crossing in levelCrossing_net:
                if levelCrossing_net[crossing]['net'] == net_start or levelCrossing_net[crossing]['net'] == net_end:
                    if way == ">>":
                        if signals_net[signal_start]['x'] < levelCrossing_net[crossing]['x'] and signals_net[signal_end]['x'] > levelCrossing_net[crossing]['x']:
                            old_table[i] |= {'crossing':crossing}
                    else:
                        if signals_net[signal_start]['x'] > levelCrossing_net[crossing]['x'] and signals_net[signal_end]['x'] < levelCrossing_net[crossing]['x']:
                            old_table[i] |= {'crossing':crossing}
    except:
        old_table = {}

        #print(f'Route_{i:02}: {signal_start}[{net_start}] {signal_end}[{net_end}]')
        
    try:
        with open("App\Layouts\Example_"+str(example)+"\\Old_table.csv", "w") as f: 
            i = 0
            f.write(f'Route , Signal_start , Signal_end , Direction , netElements , switch , platform , crossing')
            for route in object.Interlocking.AssetsForIL[0].Routes.Route:
                i = i + 1
                switch = old_table[i]["switch"] if "switch" in old_table[i] else "-"
                platform = old_table[i]["platform"] if "platform" in old_table[i] else "-"
                crossing = old_table[i]["crossing"] if "crossing" in old_table[i] else "-"

                f.write(f'\nR_{i:02} , {old_table[i]["signal_start"]} , {old_table[i]["signal_end"]} , {old_table[i]["way"]} , {old_table[i]["net_start"]}-{old_table[i]["net_end"]} , {switch} , {platform} , {crossing}')
            
            f.close()
    except:
        None
    return old_table,switch_net,platform_net,levelCrossing_net,scissorCrossing_net

def delete_signal_visual(object):
    
    visualization = object.Infrastructure.InfrastructureVisualizations.Visualization[0]
    visualization.SpotElementProjection = [i for i in visualization.SpotElementProjection if "sig" not in i.RefersToElement]

def sizeof(obj):
    size = sys.getsizeof(obj)
    if isinstance(obj, dict): return size + sum(map(sizeof, obj.keys())) + sum(map(sizeof, obj.values()))
    if isinstance(obj, (list, tuple, set, frozenset)): return size + sum(map(sizeof, obj))
    return size
#%%
def add_sections(graph,node,zones):
    zones_number = len(zones)
    zones_number += 1
    zones[zones_number] = []
    zones[zones_number].append(node)
    zones[zones_number].extend(graph[node])
    
    return zones_number

# Merge function to  merge all sublist having common elements.
def merge_common(lists):
    neigh = defaultdict(set)
    visited = set()
    for each in lists:
        for item in each:
            neigh[item].update(each)
    def comp(node, neigh = neigh, visited = visited, vis = visited.add):
        nodes = set([node])
        next_node = nodes.pop
        while nodes:
            node = next_node()
            vis(node)
            nodes |= neigh[node] - visited
            yield node
    for node in neigh:
        if node not in visited:
            yield sorted(comp(node))
#%%%
def analyze_connectedness(neighbours):
    zones = [] 
    #print("ACA",neighbours)

    for node in neighbours:
        zones.append([node,*neighbours[node]])
    #print(zones)
    
    output = list(merge_common(zones))
    #print(output)
    
    if len(output) > 1:
        return False
    else:
        return True

#%%%
def analyzing_graph(netElements,netRelations):
    
    nodes = get_nodes(netElements)
    nodes = order_nodes_points(nodes)
    netPaths = get_relations(nodes,netRelations)
    neighbours,switches = get_neighbours_and_switches(nodes,netElements) 
    limits = get_limits(switches)

    x = '' if (analyze_connectedness(neighbours)) else ('not ')
    print(f' The network is {x}connected')

    return nodes,neighbours,switches,limits,netPaths
#%%%   
def get_nodes(netElements):
    nodes = {}
    if netElements != None:
        for i in netElements.NetElement:
            #print(i)
            if i.Id not in nodes.keys():
                #print([[i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].X[:-4],i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].Y[:-4]] for j in range(len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate))])
                if i.AssociatedPositioningSystem != None:
                    if i.AssociatedPositioningSystem[0].IntrinsicCoordinate != None:
                        #print(i.Id,len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate),i.AssociatedPositioningSystem[0].IntrinsicCoordinate)
                        if len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate) > 1 and i.AssociatedPositioningSystem[0].IntrinsicCoordinate[0].GeometricCoordinate != None:
                            nodes[i.Id] = {"Begin":[int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[0].GeometricCoordinate[0].X[:-4]),-int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[0].GeometricCoordinate[0].Y[:-4])],
                                        "End":[int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[-1].GeometricCoordinate[0].X[:-4]),-int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[-1].GeometricCoordinate[0].Y[:-4])],
                                        "Lines":len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate)-1,"All":[[int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].X[:-4]),-int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].Y[:-4])] for j in range(len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate))]}
    return nodes  

def get_relations(nodes,netRelations):
    netPaths = {}
    
    for netRelation in netRelations:
        [begin_net, end_net, name] = identify_relations(netRelation.Id)
        #print(netRelation.Id,begin_net, end_net, name)
        
        if begin_net[2].isalpha():
            continue
            
        if netRelation.Navigability == "Both":
            if begin_net not in netPaths:
                netPaths[begin_net] = {"Prev":[],"Next":[]}
            if end_net not in netPaths:
                netPaths[end_net] = {"Prev":[],"Next":[]}

            if nodes[begin_net]["Begin"][0] < nodes[end_net]["Begin"][0]:
                if end_net not in netPaths[begin_net]["Next"]:
                    netPaths[begin_net]["Next"].append(end_net)
                if begin_net not in netPaths[end_net]["Prev"]:
                    netPaths[end_net]["Prev"].append(begin_net)
            else:
                if end_net not in netPaths[begin_net]["Prev"]:
                    netPaths[begin_net]["Prev"].append(end_net)
                if begin_net not in netPaths[end_net]["Next"]:
                    netPaths[end_net]["Next"].append(begin_net)
    
    #print("Paths: ",netPaths)

    for i in netPaths:
        if netPaths[i]["Prev"] == []:
            del netPaths[i]["Prev"]
        if netPaths[i]["Next"] == []:
            del netPaths[i]["Next"]
    
    #print("Paths: ",netPaths)
    return netPaths  

def get_neighbours_and_switches(nodes,netElements):
    neighbours = {}
    switches = {}
    
    for i in nodes:
        neighbours[i] = []
    
    for netElement in netElements.NetElement:
        #print(netElement.AssociatedPositioningSystem)
        if netElement.Relation != None:
            for i in netElement.Relation:
                
                #TODO HERE
                
                if (not netElement.Id[2].isdigit()): 
                    continue
                
                [begin, end, name] = identify_relations(i.Ref)
                
                if name not in switches.keys():
                    switches[name] = []
                
                if end not in neighbours[begin]:
                    neighbours[begin].append(end)
                    
                if begin not in neighbours[end]:
                    neighbours[end].append(begin)
                    
                if begin not in switches[name]:
                    switches[name].append(begin)
                
                if end not in switches[name]:
                    switches[name].append(end)
    
    return neighbours, switches

def get_limits(switches):
    
    limits = []
    
    for j in switches:
        for i in switches[j]:
            if i in limits:
                limits.remove(i)
            else:
                limits.append(i)
    
    return limits

def identify_relations(reference):
    begin = end = name = ""

    #print("R0:",reference)
    split_reference = reference.split('_')
    #print("[R]:",split_reference)
    
    if split_reference[1].count("ne") == 2:
        begin = split_reference[1][0:split_reference[1][1:].find('ne')+1]
        end = split_reference[1][len(begin):]
        name = split_reference[2]
    else:
        begin = split_reference[1]
        end = split_reference[2]
    
    #print([begin,end,name])

    return [begin,end,name]

def detect_nodes(topology):
    nodes = {}
    
    if topology.NetElements != None:
    
        for i in topology.NetElements.NetElement:
            if i.Id not in nodes.keys():
                #print([[i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].X[:-4],i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].Y[:-4]] for j in range(len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate))])
                nodes[i.Id] = {"Begin":[int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[0].GeometricCoordinate[0].X[:-4]),-int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[0].GeometricCoordinate[0].Y[:-4])],
                            "End":[int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[-1].GeometricCoordinate[0].X[:-4]),-int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[-1].GeometricCoordinate[0].Y[:-4])],
                            "Lines":len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate)-1,"All":[[int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].X[:-4]),-int(i.AssociatedPositioningSystem[0].IntrinsicCoordinate[j].GeometricCoordinate[0].Y[:-4])] for j in range(len(i.AssociatedPositioningSystem[0].IntrinsicCoordinate))]}
    
    return nodes 
    
def detect_borders(infrastructure,visualization,nodes):
    borders = {}
    
    #return borders 
    
    if infrastructure.Borders != None:
        for i in infrastructure.Borders[0].Border:
            if i.Id not in borders.keys():
                borders[i.SpotLocation[0].NetElementRef] = {"LineBorder":i.Id,"IsOpenEnd":i.IsOpenEnd,"Type":i.Type,"Inverter":True if i.SpotLocation[0].IntrinsicCoord == "1.0000" else False}
                #nodes[i.SpotLocation[0].NetElementRef] |= {"Inverter":True if i.SpotLocation[0].IntrinsicCoord == "1.0000" else False}
    if visualization.Visualization[0].SpotElementProjection != None:
        for i in visualization.Visualization[0].SpotElementProjection:
            if "oe" in i.RefersToElement:
                for node in borders.keys():
                    if borders[node]['LineBorder'] == i.RefersToElement:
                        borders[node] |= {"Position":[int(i.Coordinate[0].X[:-4]),-int(i.Coordinate[0].Y[:-4])]}
    #print(borders)
    return borders 

def detect_bufferStops(infrastructure):
    bufferStops = {}
    
    if infrastructure.BufferStops != None:
        for i in infrastructure.BufferStops[0].BufferStop:
            if i.SpotLocation[0].NetElementRef not in bufferStops.keys():
                bufferStops[i.SpotLocation[0].NetElementRef] = []
            bufferStops[i.SpotLocation[0].NetElementRef].append({"Id":i.Id,"Type":i.Type,"Direction":i.SpotLocation[0].ApplicationDirection})
            
    #print(bufferStops)
    return bufferStops

def detect_derailersIS(infrastructure):
    derailersIS = {} 

    if infrastructure.DerailersIS != None:
        for i in infrastructure.DerailersIS[0].DerailerIS:
            if i.Id not in derailersIS.keys():
                derailersIS[i.SpotLocation[0].NetElementRef] = {"Id":i.Id,"Side":i.DerailSide}

    return derailersIS

def detect_levelCrossingsIS(infrastructure,visualization):
    levelCrossingsIS = {}

    if infrastructure.LevelCrossingsIS != None:
        for i in infrastructure.LevelCrossingsIS[0].LevelCrossingIS:
            if i.Id not in levelCrossingsIS.keys():
                levelCrossingsIS[i.Name[0].Name] = {"Net":i.SpotLocation[0].NetElementRef,"Lights":i.Protection[0].Lights,"Acoustic":i.Protection[0].Acoustic,"Protection":i.Protection[0].HasActiveProtection,"Barriers":i.Protection[0].Barriers,"Coordinate":i.SpotLocation[0].IntrinsicCoord}
    
    if visualization.Visualization[0].SpotElementProjection != None:
        for i in visualization.Visualization[0].SpotElementProjection:
            if "lcr" in i.RefersToElement:
                levelCrossingsIS[i.Name[0].Name] |= {"Position":[int(i.Coordinate[0].X[:-4]),int(i.Coordinate[0].Y[:-4])]}
    
    return levelCrossingsIS

def detect_lines(infrastructure):
    lines = {}

    if infrastructure.Lines != None:
        for i in infrastructure.Lines[0].Line:
            if i.Id not in lines.keys():
                lines[i.SpotLocation[0].NetElementRef] = {"Id":i.Id,"Type":i.LineType}
    
    return lines

def detect_operationalPoints(infrastructure):
    operationalPoints = {}
    
    return operationalPoints    #IGNORE! IT IS FOR MACRO LEVEL!

    if infrastructure.BufferStops != None:
        for i in [infrastructure.BufferStops[0].BufferStop]:
            if i.Id not in operationalPoints.keys():
                operationalPoints[i.SpotLocation[0].NetElementRef] = {"Id":i.Id,"Type":i.Type}
    
    return operationalPoints

def detect_platforms(infrastructure,visualization):
    platforms = {}

    if infrastructure.Platforms != None:
        for i in infrastructure.Platforms[0].Platform:
            if i.Id not in platforms.keys():
                platforms[i.Name[0].Name] = {"Net":i.LinearLocation[0].AssociatedNetElement[0].NetElementRef,"Direction":i.LinearLocation[0].ApplicationDirection,"Value":i.Length[0].Value}
    
    if visualization.Visualization[0].SpotElementProjection != None:
        for i in visualization.Visualization[0].SpotElementProjection:
            if "plf" in i.RefersToElement:
                platforms[i.Name[0].Name] |= {"Position":[int(i.Coordinate[0].X[:-4]),int(i.Coordinate[0].Y[:-4])]}
                
    #print(platforms)
    return platforms

def detect_signalsIS(infrastructure):
    signalsIS = {}

    if infrastructure.SignalsIS != None:
        for i in infrastructure.SignalsIS[0].SignalIS:
            if i.Id not in signalsIS.keys():
                signalsIS[i.Name[0].Name] = {"Node":i.SpotLocation[0].NetElementRef,
                                            "Direction":i.SpotLocation[0].ApplicationDirection,
                                            "Position":i.SignalConstruction[0].PositionAtTrack}

    return signalsIS

def detect_switchesIS(infrastructure,visualization,nodes):
    
    switchesIS = {}
    if infrastructure.SwitchesIS != None:
        for i in infrastructure.SwitchesIS[0].SwitchIS:
            if i.Id not in switchesIS.keys():
                sw_name = i.Name[0].Name
                node = i.SpotLocation[0].NetElementRef
                type = i.Type
                direction = i.SpotLocation[0].ApplicationDirection
                
                #print(sw_name,type)
                if type == "ordinarySwitch":    # TODO: Add doubleSwitchCrossing types!
                    #continueCourse = i.ContinueCourse
                    #branchCourse = i.BranchCourse
                    continueCourse = "right" if i.RightBranch[0].Radius == "0" else "left"
                    branchCourse = "left" if continueCourse == "right" else "right"

                    leftBranch = i.LeftBranch[0].NetRelationRef
                    rightBranch = i.RightBranch[0].NetRelationRef
                
                    #print(f'{sw_name}[{node}] : {continueCourse}|{branchCourse} : {direction} : {leftBranch}|{rightBranch}')
                
                    switchesIS[sw_name] = {"Node":node,'Type':'simple',"ContinueCourse":continueCourse,"BranchCourse":branchCourse,
                                        "Direction":direction,"LeftBranch":leftBranch,"RightBranch":rightBranch}
                
                if type == "doubleSwitchCrossing":
                    #print("*"*100)

                    straightBranch_A = i.StraightBranch[0].NetRelationRef#.split('_')[1]
                    straightBranch_B = i.StraightBranch[1].NetRelationRef#.split('_')[1]
                    turningBranch_A = i.TurningBranch[0].NetRelationRef#.split('_')[1]
                    turningBranch_B = i.TurningBranch[1].NetRelationRef#.split('_')[1]

                    straightBranch_1 = straightBranch_A if node in straightBranch_A else straightBranch_B
                    turningBranch_1 = turningBranch_A if node in turningBranch_A else turningBranch_B
                    straightBranch_2 = straightBranch_B if node in straightBranch_A else straightBranch_A
                    turningBranch_2 = turningBranch_B if node in turningBranch_A else turningBranch_A

                    node_1 = node

                    #print(straightBranch_2.split('_')[1].split('ne')[1:],turningBranch_2.split('_')[1].split('ne')[1:])
                    node_2 = ['ne'+x for x in straightBranch_2.split('_')[1].split('ne')[1:] if x in turningBranch_2.split('_')[1].split('ne')[1:]][0]

                    #print (f'{sw_name} - {node} -> [{straightBranch_A}] [{straightBranch_B}] [{turningBranch_A}] [{turningBranch_B}]')

                    #print(f'{sw_name} - {node_1} -> {straightBranch_1} + {turningBranch_1}')
                    #print(f'{sw_name} - {node_2} -> {straightBranch_2} + {turningBranch_2}')

                    continueCourse = "right"
                    branchCourse = "left"

                    switchesIS[sw_name+'A'] = {"Node":node_1,'Type':'double',"ContinueCourse":continueCourse,"BranchCourse":branchCourse,
                                        "Direction":direction,"LeftBranch":straightBranch_1,"RightBranch":turningBranch_1}

                    switchesIS[sw_name+'B'] = {"Node":node_2,'Type':'double',"ContinueCourse":continueCourse,"BranchCourse":branchCourse,
                                        "Direction":direction,"LeftBranch":straightBranch_2,"RightBranch":turningBranch_2}
                    
                    #print("*"*100)

        if infrastructure.Crossings != None:
            for i in infrastructure.Crossings[0].Crossing:
                if i.Id not in switchesIS.keys():
                    xs_name = i.Name[0].Name
                    node = i.SpotLocation[0].NetElementRef
                    type = "Crossing"
                    direction = i.SpotLocation[0].ApplicationDirection
    
                    straightBranch_A = i.External[0].Ref#.split('_')[1]
                    straightBranch_B = i.External[1].Ref#.split('_')[1]
                    turningBranch_A = i.External[0].Ref#.split('_')[1]
                    turningBranch_B = i.External[1].Ref#.split('_')[1]

                    straightBranch_1 = straightBranch_A if node in straightBranch_A else straightBranch_B
                    turningBranch_1 = turningBranch_A if node in turningBranch_A else turningBranch_B
                    straightBranch_2 = straightBranch_B if node in straightBranch_A else straightBranch_A
                    turningBranch_2 = turningBranch_B if node in turningBranch_A else turningBranch_A

                    node_1 = node
                    node_2 = ['ne'+x for x in straightBranch_2.split('_')[1].split('ne')[1:] if x in turningBranch_2.split('_')[1].split('ne')[1:]][0]

                    #print(f'{xs_name} - {node_1} -> {straightBranch_1} + {turningBranch_1}')
                    #print(f'{xs_name} - {node_2} -> {straightBranch_2} + {turningBranch_2}')

                    switchesIS[xs_name+'A'] = {"Node":node_1,"ContinueCourse":continueCourse,"BranchCourse":branchCourse,
                                        "Direction":direction,"LeftBranch":straightBranch_1,"RightBranch":turningBranch_1}

                    switchesIS[xs_name+'B'] = {"Node":node_2,"ContinueCourse":continueCourse,"BranchCourse":branchCourse,
                                        "Direction":direction,"LeftBranch":straightBranch_2,"RightBranch":turningBranch_2}  

                    nodes_1 = ['ne'+i for i in straightBranch_1.split('_')[1].split('ne')[1:]]
                    nodes_2 = ['ne'+i for i in straightBranch_2.split('_')[1].split('ne')[1:]]

                    nodes = nodes_1 + nodes_2
                    #print(nodes)

                    if visualization.Visualization != None:
                        node_coord = {}
                        for i in visualization.Visualization[0].LinearElementProjection:
                            for node in nodes:
                                if node == i.RefersToElement:
                                    for coordinate in i.Coordinate:
                                        #print(node,coordinate.X,coordinate.Y)

                                        if node not in node_coord:
                                            node_coord[node] = [coordinate.X+";"+coordinate.Y]
                                        else:
                                            node_coord[node].append(coordinate.X+";"+coordinate.Y)

                        coord_set = [set(coordenade) for coordenade in node_coord.values()]
                        scr_position = list(set.intersection(*coord_set))

                        scr_coord = scr_position[0].split(';')
                        if xs_name+'A' in switchesIS:
                            switchesIS[xs_name+'A'] |= {"Position":[int(scr_coord[0][:-4]),int(scr_coord[1][:-4])]}
                        if xs_name+'B' in switchesIS:
                            switchesIS[xs_name+'B'] |= {"Position":[int(scr_coord[0][:-4]),int(scr_coord[1][:-4])]}

    if visualization.Visualization != None:
        for i in  visualization.Visualization[0].SpotElementProjection:
            if "sw" in i.RefersToElement:
                sw_name = i.Name[0].Name
                pos_x = int(i.Coordinate[0].X[:-4])
                pos_y = -int(i.Coordinate[0].Y[:-4])
                if sw_name in switchesIS: #ACA , ID NO ES LO MISMO QUE NAME
                    switchesIS[sw_name] |= {"Position":[pos_x,pos_y]}
                    #if ( pos_x == nodes[switchesIS[sw_name]["Node"]]["Begin"][0]) and pos_y == nodes[switchesIS[sw_name]["Node"]]["Begin"][1]):
                    #    nodes[switchesIS[sw_name]["Node"]]["Inverter"] = True
                if sw_name+'A' in switchesIS:
                    switchesIS[sw_name+'A'] |= {"Position":[pos_x,pos_y]}
                if sw_name+'B' in switchesIS:
                    switchesIS[sw_name+'B'] |= {"Position":[pos_x,pos_y]}

    #for x in switchesIS:
    #    print(f'{x},{switchesIS[x]["Node"]}|{switchesIS[x]["LeftBranch"]} {switchesIS[x]["RightBranch"]}')

    #print(switchesIS)
    return switchesIS

def detect_tracks(infrastructure):
    tracks = {}

    if infrastructure.Tracks != None:
        for i in infrastructure.Tracks[0].Track:
            if i.Id not in tracks.keys():
                tracks[i.Name[0].Name] = {"Node":i.LinearLocation[0].AssociatedNetElement[0].NetElementRef}
    
    return tracks

def detect_trainDetectionElements(infrastructure,visualization):
    trainDetectionElements = {}
    
    if infrastructure.TrainDetectionElements != None:
        for i in infrastructure.TrainDetectionElements[0].TrainDetectionElement:
            type = i.Type
            
            if i.Id not in trainDetectionElements.keys():
                if i.SpotLocation[0].LinearCoordinate != None:
                    trainDetectionElements[i.Id] = {"Node":i.SpotLocation[0].NetElementRef,"Name":i.Name[0].Name,"Coordinate":i.SpotLocation[0].IntrinsicCoord,"Type":i.Type,"Side":i.SpotLocation[0].LinearCoordinate[0].LateralSide}
                else:
                    trainDetectionElements[i.Id] = {"Node":i.SpotLocation[0].NetElementRef,"Name":i.Name[0].Name,"Coordinate":i.SpotLocation[0].IntrinsicCoord,"Type":i.Type}
    
    if visualization.Visualization != None:
        for i in visualization.Visualization[0].SpotElementProjection:
            reference = i.RefersToElement
            name = i.Name[0].Name
            
            if "tde" in reference or "ac" in reference: 
                if "J" in name or "AxC" in name:
                    trainDetectionElements[i.RefersToElement] |= {"Position":[int(i.Coordinate[0].X[:-4]),-int(i.Coordinate[0].Y[:-4])]}

    #print(trainDetectionElements)
    return trainDetectionElements

def analyzing_infrastructure(infrastructure,visualization,nodes):
    # borders
    try:
        borders = detect_borders(infrastructure,visualization,nodes)
    except:
        print("Error with borders")
        borders = {}
    
    # bufferStops
    try:
        bufferStops = detect_bufferStops(infrastructure)
    except:
        print("Error with bufferStops")
        bufferStops = {}
        
    # derailersIS
    try:
        derailersIS = detect_derailersIS(infrastructure)
    except:
        print("Error with derailersIS")
        derailersIS = {}
        
    # levelCrossingsIS
    try:
        levelCrossingsIS = detect_levelCrossingsIS(infrastructure,visualization)
    except:
        print("Error with levelCrossingsIS")
        levelCrossingsIS = {}
        
    # lines
    try:
        lines = detect_lines(infrastructure)
    except:
        print("Error with lines")
        lines = {}
        
    # operationalPoints
    try:
        operationalPoints = detect_operationalPoints(infrastructure)    # TODO FOR MESO
    except:
        print("Error with operationalPoints")
        operationalPoints = {}
        
    # platforms
    try:
        platforms = detect_platforms(infrastructure,visualization)
    except:
        print("Error with platforms")
        platforms = {}
        
    # signalsIS
    try:
        signalsIS = detect_signalsIS(infrastructure)
        print(switchesIS)
    except:
        print("Error with signalsIS")
        signalsIS = {}

    # switchesIS
    try:
        switchesIS = detect_switchesIS(infrastructure,visualization,nodes)
    except:
        print("Error with switchesIS")
        switchesIS = {}
        
    # tracks
    try:
        tracks = detect_tracks(infrastructure)
    except:
        print("Error with tracks")
        tracks = {}
        
    # trainDetectionElements
    try:
        trainDetectionElements = detect_trainDetectionElements(infrastructure,visualization)
    except:
        print("Error with trainDetectionElements")
        trainDetectionElements = {}
        
    return borders,bufferStops,derailersIS,levelCrossingsIS,lines,operationalPoints,platforms,signalsIS,switchesIS,tracks,trainDetectionElements
#%%%
def export_analysis(file,netElementsId,neighbours,borders,bufferStops,derailersIS,levelCrossingsIS,lines,operationalPoints,platforms,signalsIS,switchesIS,tracks,trainDetectionElements):
    
    with open(file, "w") as f:  
        
        buffer_size = 0
        for i in bufferStops:
            buffer_size += len(bufferStops[i])
            
        f.write(f'Nodes: {len(netElementsId)} | Switches: {len(switchesIS)} | Signals: {len(signalsIS)} | Detectors: {len(trainDetectionElements)} | Ends: {len(borders)+buffer_size} | Barriers: {len(levelCrossingsIS)}\n')
        
        for i in netElementsId:
            f.write(f'Node {i}:\n')
            for j in lines:
                f.write(f'\tLines -> {lines[j]["Id"]}\n')
            for j in tracks:
                if i == tracks[j]["Node"]:
                    f.write(f'\tTrack = {j}\n')
            
            for j in trainDetectionElements:
                if i == trainDetectionElements[j]["Node"]:
                    f.write(f'\tTrainDetectionElements -> {j}\n')        
                    f.write(f'\t\tType -> {trainDetectionElements[j]["Type"]}\n')
                    if "Side" in trainDetectionElements[j]:
                        f.write(f'\t\tSide -> {trainDetectionElements[j]["Side"]}\n')
            
            for j in derailersIS:
                if i == j:
                    f.write(f'\tDerailer -> {derailersIS[i]["Id"]}\n')
                    f.write(f'\t\t Side -> {derailersIS[i]["Side"]}\n')
            
            for j in borders:
                if i == borders[j]["LineBorder"]:
                    f.write(f'\tType = Border -> {j}\n')
                    f.write(f'\t\tType -> {borders[j]["Type"]}\n')
                    f.write(f'\t\tIsOpenEnd -> {borders[j]["IsOpenEnd"]}\n')
            
            if i in bufferStops:
                buffers = []
                for bufferStop in bufferStops[i]:
                    buffers.append(bufferStop["Id"])
                f.write(f'\tType = BufferStop -> {buffers}\n')
                
            f.write(f'\tNeighbours = {len(neighbours[i])} -> {neighbours[i]}\n')
            
            for j in platforms:
                if i == j:
                    f.write(f'\tPlatform  -> {platforms[j]["Id"]}\n')
                    f.write(f'\t\tSide -> {platforms[j]["Side"]}\n')
            
            for j in levelCrossingsIS:
                if i == levelCrossingsIS[j]["Net"]:
                    f.write(f'\tLevel crossing -> {j}\n')
                    f.write(f'\t\tProtection -> {levelCrossingsIS[j]["Protection"]} | Barriers -> {levelCrossingsIS[j]["Barriers"]} | Lights -> {levelCrossingsIS[j]["Lights"]} Acoustic -> {levelCrossingsIS[j]["Acoustic"]}\n')
                    f.write(f'\t\tPosition -> {levelCrossingsIS[j]["Position"]} | Coordinate: {levelCrossingsIS[j]["Coordinate"]}\n')
            for j in signalsIS:
                if i == signalsIS[j]["Node"]:
                    f.write(f'\tSignals -> {j}\n')
                    f.write(f'\t\tDirection -> {signalsIS[j]["Direction"]}\n')
                    f.write(f'\t\tPosition -> {signalsIS[j]["Position"]}\n')
            
            for j in switchesIS:
                if i == switchesIS[j]["Node"]:
                    f.write(f'\tSwitches -> {j}\n')
                    #print(f'Switches -> {j} {identify_relations(switchesIS[j]["LeftBranch"])} {identify_relations(switchesIS[j]["RightBranch"])}')

                    left = identify_relations(switchesIS[j]["LeftBranch"])[:-1]
                    right = identify_relations(switchesIS[j]["RightBranch"])[:-1]
                    left.remove(i)
                    right.remove(i)
                    
                    if switchesIS[j]["ContinueCourse"] == "right":
                        f.write(f'\t\tContinueCourse -> right -> {right[0]}\n')
                        f.write(f'\t\tBranchCourse -> left -> {left[0]}\n')
                    else:
                        f.write(f'\t\tContinueCourse -> left -> {left[0]}\n')
                        f.write(f'\t\tBranchCourse -> right -> {right[0]}\n')
        f.close()

def analyze_switches(nodes,netPaths,switchesIS,railJoint,semaphores):
    switches_data = {}
    
    for switch in switchesIS:
        # Find the switch info
        sw_info = switchesIS[switch]
        
        switches_data[switch] = {}
        
        [begin_right, end_right, name] = identify_relations(sw_info["RightBranch"])
        [begin_left, end_left, name] = identify_relations(sw_info["LeftBranch"])
        
        # Add start node
        switches_data[switch] |= {'Start':sw_info["Node"]}
        
        # Check continue course
        if (sw_info["ContinueCourse"] == "right"): 
            # Continue course is right
            switches_data[switch] |= {'Continue':end_right}
        else:
            # Continue course is left
            switches_data[switch] |= {'Continue':end_left}
        
        # Check branch course
        if (sw_info["BranchCourse"] == "right"): 
            # Branch course is right
            switches_data[switch] |= {'Branch':end_right}
        else:
            # Branch course is left
            switches_data[switch] |= {'Branch':end_left}
    
    for switch in switchesIS:
        # Find the switch info
        sw_info = switchesIS[switch]
        # Find the switch position
        sw_position = sw_info["Position"]
        switches_data[switch] |= {'Position':sw_position}
        
        # Find the start node
        start_node = sw_info["Node"]
        start_position = nodes[start_node]["Begin"] if sw_position == nodes[start_node]["End"] else nodes[start_node]["End"]
        
        # Find the continue course
        continue_course = sw_info["ContinueCourse"].capitalize()
        # Find the branch course
        branch_course = sw_info["BranchCourse"].capitalize()
        
        # Find the continue node
        continue_relation = sw_info[continue_course+"Branch"]
        continue_node = identify_relations(continue_relation)[:-1]
        continue_node.remove(start_node)
        continue_node = continue_node[0]
        continue_position = nodes[continue_node]["Begin"] if sw_position == nodes[continue_node]["End"] else nodes[continue_node]["End"]
        
        # Find the branch node
        branch_relation = sw_info[branch_course+"Branch"]
        branch_node = identify_relations(branch_relation)[:-1]
        branch_node.remove(start_node)
        branch_node = branch_node[0]
        branch_position = nodes[branch_node]["Begin"] if sw_position == nodes[branch_node]["End"] else nodes[branch_node]["End"]
        
        semaphores = calculate_start_position(start_node,start_position,switch,sw_position,nodes,netPaths,switchesIS,railJoint,switches_data,semaphores)
        semaphores = calculate_start_position(continue_node,continue_position,switch,sw_position,nodes,netPaths,switchesIS,railJoint,switches_data,semaphores)
        semaphores = calculate_start_position(branch_node,branch_position,switch,sw_position,nodes,netPaths,switchesIS,railJoint,switches_data,semaphores)
        
    return semaphores,switches_data

# Calculate the signal position given the start position, the switch position and the rail joint position
def calculate_start_position(candidate_node,candidate_position,switch,sw_position,nodes,netPaths,switchesIS,railJoint,switches_data,semaphores):
    modes = ["Start","Continue","Branch"]
    
    for mode in modes:
        if switches_data[switch][mode] == candidate_node:
            break
    #print(mode)
    
    # Find the start candidate node
    start_candidate_node,rail_joint_found,start_rail_joint_data = get_candidate_node(mode,railJoint,candidate_node,candidate_position,sw_position,netPaths,switches_data,test = False)
    #print(f'{candidate_node}--{start_candidate_node}|{rail_joint_found}')
    
    #return switches_data
    # Find the semaphore position
    if rail_joint_found == True:
        # Find the rail joint data for the candidate node
        start_rail_joint_data = railJoint[start_candidate_node]
        rail_joint_index = find_closest_coordinate(start_rail_joint_data["Position"],sw_position)
        start_rail_joint_position = start_rail_joint_data["Position"][rail_joint_index]
        start_rail_joint = start_rail_joint_data["Joint"][rail_joint_index]
        #print("Start Rail Joint:",start_rail_joint)
        
        for i in switches_data:
            #print("T:",switches_data[i],mode,start_candidate_node)
            if switches_data[i][mode] == start_candidate_node:
                switch_candidate = i
        
        sw_candidate_position = switchesIS[switch_candidate]["Position"]        
        start_candidate_position = nodes[start_candidate_node]["Begin"] if  sw_candidate_position == nodes[start_candidate_node]["End"] else nodes[start_candidate_node]["End"]
        # Calculate the signal position in the same line as the switch and node, before the joint
        start_signal_position = calculate_position(start_candidate_position,sw_candidate_position,start_rail_joint_position)    # TODO LIMIT THE POSITION IF THE LINE ENDS IN A BUFFER
    else:
        #print("No Rail Joint Found")
        #print(start_candidate_node,nodes[start_candidate_node]["Lines"])
        if nodes[start_candidate_node]["Lines"] > 1:
            # Calculate the signal position before the curve before the switch node
            start_candidate_position = candidate_position
            aux_mode = mode if mode != "Branch" else "Continue"

            if candidate_node == start_candidate_node:
                switch_candidate = switch
            else:
                for i in switches_data:
                    #print("T:",switches_data[i],mode,aux_mode,start_candidate_node,candidate_node)
                    if switches_data[i][aux_mode] == start_candidate_node:
                        switch_candidate = i
                    
            sw_candidate_position = switchesIS[switch_candidate]["Position"]   
                
            start_rail_joint_position = None
            #print(start_candidate_node,nodes[start_candidate_node],start_candidate_position,sw_candidate_position)
            fake_rail_joint_index = nodes[start_candidate_node]["All"].index(sw_candidate_position)
            
            if fake_rail_joint_index == 0:
                sw_candidate_position = nodes[start_candidate_node]["All"][fake_rail_joint_index + 1]
                start_candidate_position = nodes[start_candidate_node]["All"][fake_rail_joint_index + 2]
            elif fake_rail_joint_index == len(nodes[start_candidate_node]["All"])-1:
                sw_candidate_position = nodes[start_candidate_node]["All"][fake_rail_joint_index - 1]
                start_candidate_position = nodes[start_candidate_node]["All"][fake_rail_joint_index - 2]
            #print(nodes[start_candidate_node]["All"],sw_candidate_position,start_candidate_position)
        else:
            # Calculate the signal position in the same line as the switch and node, at 30% of the switch position
            start_candidate_position = candidate_position
            sw_candidate_position = sw_position
            start_rail_joint_position = None
            
        #print(sw_candidate_position,start_candidate_position)
        if start_candidate_position[0] > sw_candidate_position[0]:
            start_fake_rail_joint_position = [sw_candidate_position[0] + (start_candidate_position[0] - sw_candidate_position[0])*0.3 , sw_candidate_position[1] + (start_candidate_position[1] - sw_candidate_position[1])*0.3]
        else:
            start_fake_rail_joint_position = [start_candidate_position[0] + (sw_candidate_position[0] - start_candidate_position[0])*0.3 , start_candidate_position[1] + (sw_candidate_position[1] - start_candidate_position[1])*0.3]

        #print(start_candidate_position,sw_candidate_position,start_fake_rail_joint_position)
        start_signal_position = start_fake_rail_joint_position
        
    #print(mode,switch,candidate_node,start_candidate_position,sw_candidate_position,start_rail_joint_position,start_signal_position)
    
    # Update semaphore
    sem_type = "Maneuver" if mode == "Branch" else "Straight" 
    if start_candidate_node == "ne27":  # TODO SWITCHES FOR Ne27 ARE INVERTED!
        print(f'{start_candidate_node}|{switch_candidate} - {start_signal_position} vs {sw_candidate_position}')
    direction = "left" if start_signal_position[0] < sw_candidate_position[0] else "right" 
    
    
    #print(start_signal_position,nodes[start_candidate_node]["All"])
    intrinsic_coordinate = calculate_intrinsic_coordinate(start_signal_position,nodes[start_candidate_node]["All"])
    semaphores["sig"+str(len(semaphores)+1).zfill(2)] = {"Net":start_candidate_node,"Switch":switch_candidate,"Type":sem_type,"Direction":direction,"Position":start_signal_position,"Coordinate":intrinsic_coordinate}
    
    #print(" ",mode,switch,candidate_node,start_signal_position)
    
    return semaphores

# Get the candidate node for the switch
def get_candidate_node(mode,railJoint,start_candidate_node,candidate_position,sw_position,netPaths,switches_data, test = True):
    # Find the start rail joint
    rail_joint_found = False
    start_rail_joint_data = None
    candidate_found = False
    
    while (rail_joint_found == False): 
        if test: 
            print("Candidate node:",start_candidate_node)
        if start_candidate_node in railJoint:
            start_rail_joint_data = railJoint[start_candidate_node]
            rail_joint_found = True
        else:
            if mode == "Start":
                # If start position before switch
                if candidate_position[0] < sw_position[0]:
                    if ("Prev" in netPaths[start_candidate_node]):
                        start_candidate_node = netPaths[start_candidate_node]["Prev"][0]
                    else:
                        if test:
                            print("There is a previous switch or the end of the railway")
                        break
                else: # If start position after switch
                    if ("Next" in netPaths[start_candidate_node]):
                        start_candidate_node = netPaths[start_candidate_node]["Next"][0]
                    else:
                        if test:
                            print("There is a forward switch or the end of the railway")
                        break
            elif mode == "Continue":
                candidate_found = False
                # If continue position before switch
                #print(start_candidate_node,candidate_position,sw_position)
                if candidate_position[0] > sw_position[0]:
                    if ("Next" in netPaths[start_candidate_node]):
                        for i in switches_data:
                            #print(i,switches_data[i]["Start"])
                            if switches_data[i]["Start"] == start_candidate_node:
                                start_candidate_node = switches_data[i]["Continue"]
                                candidate_found = True
                                if test:
                                    print("Found!",start_candidate_node)
                                break
                        if candidate_found == False:
                            break
                    else:
                        if test:
                            print("There is a forward switch or the end of the railway")
                        break
                else:
                    if ("Prev" in netPaths[start_candidate_node]):
                        for i in switches_data:
                            #print(i,switches_data[i]["Start"])
                            if switches_data[i]["Start"] == start_candidate_node:
                                start_candidate_node = switches_data[i]["Continue"]
                                candidate_found = True
                                if test:
                                    print("Found!",start_candidate_node)
                                break
                        if candidate_found == False:
                            break
                    else:
                        if test:
                            print("There is a forward switch or the end of the railway")
                        break
            elif mode == "Branch":
                candidate_found = False
                # If continue position before switch
                #print(start_candidate_node,candidate_position,sw_position)
                if candidate_position[0] > sw_position[0]:
                    if ("Next" in netPaths[start_candidate_node]):
                        for i in switches_data:
                            #print(i,switches_data[i]["Start"])
                            if switches_data[i]["Start"] == start_candidate_node:
                                start_candidate_node = switches_data[i]["Continue"]
                                candidate_found = True
                                if test:
                                    print("Found!",start_candidate_node)
                                break
                        if candidate_found == False:
                            break
                    else:
                        if test:
                            print("There is a forward switch or the end of the railway")
                        break
                else:
                    if ("Prev" in netPaths[start_candidate_node]):
                        for i in switches_data:
                            #print(i,switches_data[i]["Start"])
                            if switches_data[i]["Start"] == start_candidate_node:
                                start_candidate_node = switches_data[i]["Continue"]
                                candidate_found = True
                                if test:
                                    print("Found!",start_candidate_node)
                                break
                        if candidate_found == False:
                            break
                    else:
                        if test:
                            print("There is a forward switch or the end of the railway")
                        break
    if test:
        print("Leaving")
    return start_candidate_node,rail_joint_found,start_rail_joint_data

# Calculate the signal position in the same line as the switch and node, before the joint
def calculate_position(start_candidate_position,sw_candidate_position,start_rail_joint_position):
    signal_position = [None,None]
    
    # calculate coordinate between two points
    m = (sw_candidate_position[1] - start_candidate_position[1]) / (sw_candidate_position[0] - start_candidate_position[0])
    c = start_candidate_position[1] - m * start_candidate_position[0]
    
    d = 0.075
    
    signal_position_a = [start_rail_joint_position[0]*(1+d),start_rail_joint_position[0]*(1+d)*m+c]
    signal_position_b = [start_rail_joint_position[0]*(1-d),start_rail_joint_position[0]*(1-d)*m+c]
    
    #print(m,c,signal_position_a,signal_position_b)
    
    distance_a = (signal_position_a[0]-sw_candidate_position[0])**2 + (signal_position_a[1]-sw_candidate_position[1])**2
    distance_b = (signal_position_b[0]-sw_candidate_position[0])**2 + (signal_position_b[1]-sw_candidate_position[1])**2
    
    if distance_a > distance_b:
        signal_position = signal_position_a
    else:
        signal_position = signal_position_b
    
    return signal_position

# Find the closest joint to the switch position
def find_closest_coordinate(joint_positions,sw_position):
    index = -1
    distance = -1
    
    for joint in joint_positions:
        new_distance_sq = (joint[0]-sw_position[0])**2 + (joint[1]-sw_position[1])**2
        if distance == -1:
            distance = new_distance_sq
            index = joint_positions.index(joint)
        if new_distance_sq < distance:
            distance = new_distance_sq
            index = joint_positions.index(joint)
    
    #print(index)
    return index

def create_railJoint(trainDetectionElements):
    railJoint = {}
    for joint in trainDetectionElements:
            
            if trainDetectionElements[joint]["Node"] not in railJoint.keys():
                railJoint[trainDetectionElements[joint]["Node"]] = {}
            
            if "Position" not in railJoint[trainDetectionElements[joint]["Node"]]:
                railJoint[trainDetectionElements[joint]["Node"]]["Position"] = []
                
            if "Joint" not in railJoint[trainDetectionElements[joint]["Node"]]:
                railJoint[trainDetectionElements[joint]["Node"]]["Joint"] = []
            
            if trainDetectionElements[joint]["Type"] == "insulatedRailJoint":    
                railJoint[trainDetectionElements[joint]["Node"]]["Position"].append(trainDetectionElements[joint]["Position"])
                railJoint[trainDetectionElements[joint]["Node"]]["Joint"].append(trainDetectionElements[joint]["Name"])
    return railJoint

# Export routes to file and object
def export_routes(file,routes,object,example,switchesIS):
    new_table = {}

    #new_table[i] = {'signal_start':signal_start,'signal_end':signal_end,'net_start':net_start,'net_end':net_end,'way':way,'switch':switch,'platform':platform,'crossing':crossing}

    with open(file, "w") as f: 
        #print(semaphores)
        for route in routes:
            signal_start = routes[route]["Start"].replace('sig','S')
            signal_end = routes[route]["End"].replace('sig','S')
            way = routes[route]["Way"]
            net_start = routes[route]["Path"][0]
            net_end = routes[route]["Path"][-1]

            switch =  '-'.join(i for i in routes[route]["Switches"]) if routes[route]["Switches"] else ''

            platform =  routes[route]["Platforms"][0] if routes[route]["Platforms"] else ''
            crossing = routes[route]["LevelCrossings"][0] if routes[route]["LevelCrossings"] else ''
            f.write(f'route_{route} [{signal_start} {way} {signal_end}]:\n')
            
            new_table[int(route)] = {'route':int(route),'signal_start':signal_start,'signal_end':signal_end,'net_start':net_start,'net_end':net_end,'way':way,'switch':switch,'platform':platform,'levelcrossing':crossing}

            f.write(f'\tPath: {routes[route]["Path"]}\n')
            if routes[route]["Switches"]:
                f.write(f'\tSwitches: {routes[route]["Switches"]}\n')
            if routes[route]["Platforms"]:
                f.write(f'\tPlatforms: {routes[route]["Platforms"]}\n')
            if routes[route]["LevelCrossings"]:
                f.write(f'\tLevelCrossings: {routes[route]["LevelCrossings"]}\n')
        f.close()

    #for route in routes:
    #    if routes[route]["Switches"] != []:
    #        print(route,routes[route])

    #for x in switchesIS:
    #    print(x,switchesIS[x])

    # Create routes for AssetsForIL
    if (object.Interlocking.AssetsForIL != None):
        # Create Routes
        AssetsForIL = object.Interlocking.AssetsForIL[0]
        AssetsForIL.create_Routes()
        
        rts = AssetsForIL.Routes

        # Add new route for each route
        for route in routes:
            #print(f'Create route{route}')
            rts.create_Route()

            signal_start = routes[route]["Start"].replace('sig','S')
            signal_end = routes[route]["End"].replace('sig','S')

            #print(route,routes[route])

            # Create atributes
            #print('Create atributes')
            rts.Route[route-1].Id = f'rt_{routes[route]["Start"]}_{routes[route]["End"]}'
            if routes[route]["Switches"] != []:
                for sw in routes[route]["Switches"]:
                    rts.Route[route-1].Id = rts.Route[route-1].Id + f'_{sw.replace('_', '')}'

            # Create Designator
            #print('Create Designator')
            rts.Route[route-1].create_Designator()
            rts.Route[route-1].Designator[0].Register = "_Example"     # Register="_Example" 
            rts.Route[route-1].Designator[0].Entry = f'Route {signal_start}-{signal_end}'
            if routes[route]["Switches"] != []: 
                rts.Route[route-1].Designator[0].Entry = rts.Route[route-1].Designator[0].Entry + f' ({"-".join(sw for sw in routes[route]["Switches"]).replace('_','')})'

            # Create handlesRouteType
            #print('Create handlesRouteType')
            rts.Route[route-1].create_HandlesRouteType()
            rts.Route[route-1].HandlesRouteType[0].Ref = "rt_main"   

            # Create hasTvdSection
            #print('Create hasTvdSection')
            rts.Route[route-1].create_HasTvdSection()
            rts.Route[route-1].HasTvdSection[0].Ref = "tvd_XX"              # TO BE DEFINED

            # Create routeEntry
            #print('Create routeEntry')
            rts.Route[route-1].create_RouteEntry()
            rts.Route[route-1].RouteEntry.Id = f'rts_{routes[route]["Start"]}_rt_{routes[route]["Start"]}_{routes[route]["End"]}'  
            rts.Route[route-1].RouteEntry.create_RefersTo()
            rts.Route[route-1].RouteEntry.RefersTo.Ref = f'il_{routes[route]["Start"]}'

            # Create routeExit
            #print('Create routeExit')
            rts.Route[route-1].create_RouteExit()
            rts.Route[route-1].RouteExit.Id = f'rts_{routes[route]["End"]}_rt_{routes[route]["Start"]}_{routes[route]["End"]}'  
            rts.Route[route-1].RouteExit.create_RefersTo()
            rts.Route[route-1].RouteExit.RefersTo.Ref = f'il_{routes[route]["End"]}'

            # Create FacingSwitchInPosition
            i = 0
            for sw in routes[route]["Switches"]:
                
                #print(f'{sw} Create FacingSwitchInPosition')
                rts.Route[route-1].create_FacingSwitchInPosition()
                rts.Route[route-1].FacingSwitchInPosition[i].Id = f'rp_rt_{sw.replace("_","")[:-1]}_{rts.Route[route-1].Id}'
                
                #print(f'{sw} Create Designator')
                rts.Route[route-1].FacingSwitchInPosition[i].create_Designator()
                rts.Route[route-1].FacingSwitchInPosition[i].Designator[0].Register = "_Example"
                
                #print(f'{sw} Create RefersToSwitch')
                rts.Route[route-1].FacingSwitchInPosition[i].create_RefersToSwitch()
                rts.Route[route-1].FacingSwitchInPosition[i].RefersToSwitch.Ref = f'il_{sw.replace("_","")[:-1]}'

                #print(f'{sw} Create InPosition {sw} {sw[:-2]}')
                if(sw[:-2] in switchesIS and "ContinueCourse" in switchesIS[sw[:-2]]):
                    direction = switchesIS[sw[:-2]]["ContinueCourse"] if sw[-1:] == "N" else switchesIS[sw[:-2]]["BranchCourse"]
                    rts.Route[route-1].FacingSwitchInPosition[i].InPosition = direction
                    rts.Route[route-1].FacingSwitchInPosition[i].Designator[0].Entry = f'{sw.replace("_","")[:-1]} in {direction}'

                i = i + 1
    
    with open("App\Layouts\Example_"+str(example)+"\\New_table.csv", "w") as f: 
        i = 0
        f.write(f'Route , Signal_start , Signal_end , Direction , netElements , switch , platform , LevelCrossings')
        for route in new_table:
            i = i + 1
            f.write(f'\nR_{i:02} , {new_table[route]["signal_start"]} , {new_table[route]["signal_end"]} , {new_table[route]["way"]} , {new_table[route]["net_start"]}-{new_table[route]["net_end"]} , {new_table[route]["switch"]} , {new_table[route]["platform"]} , {new_table[route]["levelcrossing"]}')
        
        f.close()

    return new_table

# Calculate intrindic coordinate
def calculate_intrinsic_coordinate(position,points):
    intrinsic_coordinate = 0
    
    first_point = points[0]
    length = 0
    for p in points[1:]:
        if (position[0] > first_point[0] and position[0] < p[0]) or (position[0] < first_point[0] and position[0] > p[0]):
            intrinsic_coordinate += length_between_points(first_point,position)
        else:
            intrinsic_coordinate += length_between_points(first_point,p)
        
        length += length_between_points(first_point,p)
        first_point = p
    
    intrinsic_coordinate /= length
    return str(intrinsic_coordinate)[:6]

# Calculate the length between two points
def length_between_points(point_a,point_b):
    return ((point_a[0]-point_b[0])**2 + (point_a[1]-point_b[1])**2)**0.5

def create_semaphore(semaphores,semaphore_source,railJoint):

    n = len(semaphores)+1
    
    #print(railJoint)
    
    continue_straight = semaphore_source["Continue"][3]
    branch_straight = semaphore_source["Branch"][3]
    start_x = semaphore_source["Start"][1][0]
    continue_x = semaphore_source["Continue"][1][0]
    branch_x = semaphore_source["Branch"][1][0]
    sw_x = semaphore_source["Switch"][0]
    
    #Start to Continue
    type = "Straight" if continue_straight else "Maneuver"
    net = semaphore_source["Start"][0]
    direction, position = ("Normal","Left") if start_x < continue_x else ("Reverse","Right")
    coordinate = 0.33 if start_x < sw_x else 0.66
    
    semaphores[n] = {'Id':'sig'+str(n),'Net':net,'Type':type,'Direction':direction,'Position':position,'Coordinate':coordinate}
    #print(f'  Creating a {type} semaphore[{n}] @{net} in {coordinate}|{semaphore_source}')
    
    #Start to Branch
    type = "Straight" if branch_straight else "Maneuver"
    net = semaphore_source["Start"][0]
    direction, position = ("Normal","Left") if start_x < branch_x else ("Reverse","Right")
    coordinate = 0.33 if start_x < sw_x else 0.66
    
    semaphores[n+1] = {'Id':'sig'+str(n+1),'Net':net,'Type':type,'Direction':direction,'Position':position,'Coordinate':coordinate}
    #print(f'  Creating a {type} semaphore[{n+1}] @{net} in {coordinate}|{semaphore_source}')
    
    # Continue To Start
    type = "Straight" if continue_straight else "Maneuver"
    net = semaphore_source["Continue"][0]
    direction, position = ("Normal","Left") if start_x > continue_x else ("Reverse","Right")
    coordinate = 0.33 if continue_x > sw_x else 0.66
    
    semaphores[n+2] = {'Id':'sig'+str(n+2),'Net':net,'Type':type,'Direction':direction,'Position':position,'Coordinate':coordinate}
    #print(f'  Creating a {type} semaphore[{n+2}] @{net} in {coordinate}|{semaphore_source}')
    
    #Branch To Start
    type = "Straight" if branch_straight else "Maneuver"
    net = semaphore_source["Branch"][0]
    direction, position = ("Normal","Left") if start_x > branch_x else ("Reverse","Right")
    coordinate = 0.33 if branch_x > sw_x else 0.66
    
    semaphores[n+3] = {'Id':'sig'+str(n+3),'Net':net,'Type':type,'Direction':direction,'Position':position,'Coordinate':coordinate}
    #print(f'  Creating a {type} semaphore[{n+3}] @{net} in {coordinate}|{semaphore_source}')

def calculate_angle(pos_sw,pos_start,pos_continue,pos_branch,n_continue,n_branch):        
    
    continue_straight = False
    branch_straight = False
    
    #print(pos_sw,pos_start,pos_continue,pos_branch)

    x1 = pos_start[0]
    y1 = pos_start[1]
    x2 = pos_sw[0]
    y2 = pos_sw[1]
    x3 = pos_continue[0]
    y3 = pos_continue[1]
    
    #print(f'[{x1},{y1}] > [{x2},{y2}] > [{x3},{y3}]')
    
    continue_straight = ((y1 - y2) * (x1 - x3) == (y1 - y3) * (x1 - x2)) & (n_continue == 1)
    
    x3 = pos_branch[0]
    y3 = pos_branch[1]
    
    #print(x1,y1,x2,y2,x3,y3)
    # TODO ADD ALL THE POINTS, NOT ONLY BEGIN-END 
    
    # Because it is a branch!
    branch_straight = False #((y1 - y2) * (x1 - x3) == (y1 - y3) * (x1 - x2)) & (n_branch == 1)
    
    #print(pos_continue["Lines"],((y1 - y2) * (x1 - x3) == (y1 - y3) * (x1 - x2)),pos_branch["Lines"],((y1 - y2) * (x1 - x3) == (y1 - y3) * (x1 - x2)))
    
    return continue_straight, branch_straight

def get_sem_graph(netPaths,signals,signals_in_node):

    sem_graph = {}
    
    #for node in signals_in_node:
    #    print(f'{node} -> {signals_in_node[node]}')

    #for node in netPaths:
    #    print(f'{node} -> {netPaths[node]}')

    return sem_graph

    for sig in signals:
        print(f'Signal:{sig} [{signals[sig]["From"]}] -> {netPaths[signals[sig]["From"]]} {signals[sig]["Way"]}')        
        if signals[sig]["Way"] == ">>":
            if "Next" in netPaths[signals[sig]["From"]]:
                for node in netPaths[signals[sig]["From"]]["Next"]:
                    print(f'{signals_in_node[node]["Next"]}')
        else:
            if "Prev" in netPaths[signals[sig]["From"]]:
                for node in netPaths[signals[sig]["From"]]["Prev"]:
                    print(f'{signals_in_node[node]["Prev"]}')



        #if "Prev" in netPaths[signals[sig]["From"]]:
        #    p = netPaths[signals[sig]["From"]]["Prev"]
            #print(f'{[signals_in_node[i] for i in p]}')
        #if "Next" in netPaths[signals[sig]["From"]]:
        #    n = netPaths[signals[sig]["From"]]["Next"]
            #print(f'{[signals_in_node[i] for i in n]}')
        
        #print(signals_in_node[signals[sig]["From"]])
        #print(f'Signal:{sig} [{signals[sig]["From"]}] -> {netPaths[signals[sig]["From"]]}')



    return sem_graph

# Detect the routes
def detect_routes(signals,netPaths,switch_net,platform_net,levelCrossing_net,scissorCrossing_net):
    routes = {}
    #print(netPaths)
    signals_in_node = find_semaphores_in_node(signals)
    #print(signals_in_node)
    #print('x')
    for path in signals_in_node:
        print(f'{path} {signals_in_node[path]}')
    #for path in netPaths:
    #    print(f'{path} {netPaths[path]}')

    #print('x')
    sem_graph = get_sem_graph(netPaths,signals,signals_in_node)
    
    route = 0
    for sig in signals:
        
        #print(f'X {sig} @ {signals[sig]["Net"]}->{netPaths[signals[sig]]}')   
        #print(f'Signal: {sig} @ {signals[sig]}')
        # Find the start semaphore with director + start node
        
        #if signals[sig]["Name"][0] != "T":
        start_signal = signals[sig]["Name"]
        start_node = signals[sig]["From"]
        way = signals[sig]["Way"]

        direction = "Next" if way == ">>" else "Prev"
        if start_node in signals_in_node:
            #print(f'{start_signal} {way} {signals_in_node[start_node][direction]}')
            if len(signals_in_node[start_node][direction]) > 1:
                #if start_signal == signals_in_node[start_node][direction][0]:
                #    end_signal = signals_in_node[start_node][direction][1]
                if start_signal in signals_in_node[start_node][direction] and  start_signal != signals_in_node[start_node][direction][-1]:
                    end_signal = signals_in_node[start_node][direction][signals_in_node[start_node][direction].index(start_signal)+1]
                    #print(f'{way} {start_signal} {end_signal} {signals[start_signal]["Position"][0]} {signals[end_signal]["Position"][0]}')
                if start_signal == signals_in_node[start_node][direction][-1]:
                    end_signal = signals_in_node[start_node][direction][0]
                    #print(f'{way} {start_signal} {end_signal} {signals[start_signal]["Position"][0]} {signals[end_signal]["Position"][0]}')

                if ((way == ">>" and signals[start_signal]["Position"][0] < signals[end_signal]["Position"][0]) or (way == "<<" and signals[start_signal]["Position"][0] > signals[end_signal]["Position"][0])):
                    if start_signal != 'P63' and start_signal != 'B89':
                        route += 1
                        #print(f'Route_{route} : {start_signal} to {end_signal}')
                        paths = [start_node]
                        switches = find_switches_in_the_path(paths,switch_net)
                        platforms = find_platforms_in_the_path(paths,platform_net,signals,start_signal,end_signal)
                        levelCrossing = find_level_crossings_in_the_path(paths,levelCrossing_net,signals,start_signal,end_signal)
                        #print(f'{route} {start_signal} {end_signal} {paths}') 
                        scissorCrossing = find_scissor_crossings_in_the_path(paths,scissorCrossing_net,signals,start_signal,end_signal)
                        #print(f'{route} {scissorCrossing}') 
                        #print(f'Route_{route} : {start_signal} to {end_signal} {paths}')
                        routes[route] = {'Start':start_signal,'End':end_signal,'Way':way,'Path':paths,'Switches':switches,'Platforms':platforms,'LevelCrossings':levelCrossing,'ScissorCrossings':scissorCrossing}
                        continue
    
        # Find all the next nodes
        end_nodes = []
        end_nodes = find_next_nodes(start_node,way,signals_in_node,netPaths,end_nodes)
        paths = find_path_between_nodes(start_node,end_nodes,netPaths,way)

        #if end_nodes:
        #    print(f'--{sig} {way} {start_node} {end_nodes} {paths}')

        for node in range(len(end_nodes)): 
            # Find all the semaphores at the nodes with the same direction than the start semaphore
            end_signal = find_semaphores(end_nodes[node],start_signal,signals)

            #print(f'{sig} {way} {start_node} {end_nodes[node]} {end_signal} {paths}')

            # Find switches within the path
            switches = find_switches_in_the_path(paths[node],switch_net)
            platforms = find_platforms_in_the_path(paths[node],platform_net,signals,start_signal,end_signal)
            levelCrossing = find_level_crossings_in_the_path(paths[node],levelCrossing_net,signals,start_signal,end_signal)
            #print(f'{route} {start_signal} {end_signal} {paths[node]}') 
            scissorCrossing = find_scissor_crossings_in_the_path(paths[node],scissorCrossing_net,signals,start_signal,end_signal)  
            #print(f'{route} {scissorCrossing}')   
            if start_signal != 'P63' and start_signal != 'B89':
                route += 1
                #print(f'Route_{route} : {start_signal} to {end_signal} {paths[node]}')
                routes[route] = {'Start':start_signal,'End':end_signal,'Way':way,'Path':paths[node],'Switches':switches,'Platforms':platforms,'LevelCrossings':levelCrossing,'ScissorCrossings':scissorCrossing}
        
        #print(len(netPaths))
        if len(netPaths) == 53:
            if sig == 'L32':
                route += 1
                path = ['ne70','ne104','ne21']
                scissorCrossing = ['Sw03_XN']
                routes[route] = {'Start':'L32','End':'P73','Way':'>>','Path':path,'Switches':[],'Platforms':[],'LevelCrossings':[],'ScissorCrossings':scissorCrossing}
            if sig == 'L41':
                route += 1
                path = ['ne103','ne64']
                routes[route] = {'Start':'L41','End':'S90','Way':'<<','Path':path,'Switches':[],'Platforms':[],'LevelCrossings':[],'ScissorCrossings':[]}
            if sig == 'P63':
                route += 1
                path = ['ne24','ne64','ne103','ne67']
                routes[route] = {'Start':'P63','End':'P64','Way':'>>','Path':path,'Switches':[],'Platforms':[],'LevelCrossings':[],'ScissorCrossings':[]}
            if sig == 'B89':
                route += 1
                path = ['ne23','ne64','ne103','ne67']
                routes[route] = {'Start':'B89','End':'P64','Way':'>>','Path':path,'Switches':[],'Platforms':[],'LevelCrossings':[],'ScissorCrossings':[]}
    return routes

def get_graph(netPaths):
    
    graph = {}

    for node in netPaths:
        #print(f'xx :{node}')

        if node not in graph:
            graph[node] = []
        
        if "Prev" in netPaths[node] :
            graph[node] += netPaths[node]["Prev"]
        if "Next" in netPaths[node] :
            graph[node] += netPaths[node]["Next"]

    #print(graph)
    return graph

def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    #print(f'Path:{path}')
    if start == end:
        return path
    if start not in graph:
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

def find_switches_in_the_path(path,switch_net):
    switches = []
    #print(path)
    #for i in switch_net:
    #    print(i,switch_net[i])
    
    for i in switch_net:
        if switch_net[i]['type'] == 'simple':
            if switch_net[i]['main'] in path and switch_net[i]['normal'] in path:
                switches.append(i+"_N")
            if switch_net[i]['main'] in path and switch_net[i]['reverse'] in path:
                switches.append(i+"_R")

        if switch_net[i]['type'] == 'double':
            if switch_net[i]['Movement_NN'][0] in path and switch_net[i]['Movement_NN'][1] in path:
                switches.append(i+"_NN")
            if switch_net[i]['Movement_RR'][0] in path and switch_net[i]['Movement_RR'][1] in path:
                switches.append(i+"_RR")
            if switch_net[i]['Movement_RN'][0] in path and switch_net[i]['Movement_RN'][1] in path:
                switches.append(i+"_RN")
            if switch_net[i]['Movement_NR'][0] in path and switch_net[i]['Movement_NR'][1] in path:
                switches.append(i+"_NR")

    #print(switches)
    return switches

def find_platforms_in_the_path(paths,platform_net,signals,start_signal,end_signal):
    platform = []
    #print(platform_net)
    #print(paths)
    for i in platform_net:
        #print(platform_net[i])
        if platform_net[i]['net'] in paths:
            start_pos = signals[start_signal]["Position"][0]
            end_pos = signals[end_signal]["Position"][0]
            plat_pos = platform_net[i]['x']

            #print(f'{start_pos} {end_pos} {plat_pos}')
            if (start_pos < plat_pos and end_pos > plat_pos) or (start_pos > plat_pos and end_pos < plat_pos): 
                platform.append(i)
 
    #print(platform)
    return platform

def find_level_crossings_in_the_path(paths,levelCrossing_net,signals,start_signal,end_signal):
    crossing = []
    
    #print(platform_net)
    #print(paths)
    for i in levelCrossing_net:
        #print(platform_net[i])
        if levelCrossing_net[i]['net'] in paths:
            start_pos = signals[start_signal]["Position"][0]
            end_pos = signals[end_signal]["Position"][0]
            cross_pos = levelCrossing_net[i]['x']

            #print(f'{start_pos} {end_pos} {cross_pos}')
            if (start_pos < cross_pos and end_pos > cross_pos) or (start_pos > cross_pos and end_pos < cross_pos): 
                crossing.append(i)
 
    #print(crossing)
    return crossing

def find_scissor_crossings_in_the_path(path,scissorCrossing_net,signals,start_signal,end_signal):
    crossings = []
    #print(scissorCrossing_net)
    #for i in scissorCrossing_net:
    #    print(i,scissorCrossing_net[i])
    
    for i in scissorCrossing_net:
        if scissorCrossing_net[i]['net'][0] in path and scissorCrossing_net[i]['net'][1] in path:
            crossings.append(i+"_XN")
        if scissorCrossing_net[i]['net'][2] in path and scissorCrossing_net[i]['net'][3] in path:
            crossings.append(i+"_XR")

    #print(crossings)
    return crossings

def find_path_between_nodes(start_node,end_nodes,netPaths,way):
    
    paths = []
    
    #print(start_node,way,end_nodes)
    for end_node in end_nodes:
        graph = get_graph(netPaths)
        path = find_shortest_path(graph, start_node, end_node, path=[])
        #print(f'Finding a path from {start_node} {way} {end_node} : {path}')
        paths.append(path)
    return paths

# Find the next nodes with semaphores with the same direction than the start semaphore
def find_next_nodes(start_node,way,semaphores_in_node,netPaths,end_nodes = []):
    #end_nodes = []

    #if start_node in semaphores_in_node and direction in semaphores_in_node[start_node]:
    #    return [start_node] + end_nodes
    
    direction = "Next" if way == ">>" else "Prev"

    if start_node in netPaths and direction in netPaths[start_node]:   # There is a next/prev node
        #print(f'xxx {start_node} has a {direction} node | {netPaths[start_node][direction]}')

        # Check ALL the next/prev nodes
        for node in netPaths[start_node][direction]: 
            # If the next/prev node has a semaphore in the same direction
            #if node in semaphores_in_node:
            if node in semaphores_in_node and direction in semaphores_in_node[node]:
                end_nodes.append(node)
            else:   # If there is no semaphore or it is not in the same direction
                end_nodes = find_next_nodes(node,way,semaphores_in_node,netPaths,end_nodes)
    else: # There is not a next/prev node
        return end_nodes

    return end_nodes

# Find the semaphores at the node
def find_semaphores_in_node(signals):
    signals_in_node = {}
    
    for sig in signals:
        #print(f'{sig} {signals[sig]}')

        # Adding the node
        if signals[sig]["From"] not in signals_in_node:
            signals_in_node[signals[sig]["From"]] = {"Next":[],"Prev":[]}
        # Updating for each direction
        #if signals[sig]["AtTrack"] == "left":
        if signals[sig]["Way"] == ">>":
            signals_in_node[signals[sig]["From"]]["Next"].append(signals[sig]["Name"])
        else:
            signals_in_node[signals[sig]["From"]]["Prev"].append(signals[sig]["Name"])
    
    # Deleting the semaphores with only no members
    for i in signals_in_node:
        if signals_in_node[i]["Prev"] == []:
            del signals_in_node[i]["Prev"]
        if signals_in_node[i]["Next"] == []:
            del signals_in_node[i]["Next"]
    
    
    for i in signals_in_node:
        if "Prev" in signals_in_node and signals_in_node[i]["Prev"] != []:
            signals_in_node[i]["Prev"]  = sorted(signals_in_node[i]["Prev"] , key = lambda x: signals[x]['Position'][0],reverse=('decrease'))
        if "Next" in signals_in_node and signals_in_node[i]["Next"] != []:
            signals_in_node[i]["Next"]  = sorted(signals_in_node[i]["Next"] , key = lambda x: signals[x]['Position'][0])

    return signals_in_node

# Find semaphores based on nodes
def find_semaphores(node,start_signal,signals):
    end_signal = ''
    
    #if start_signal == "sig32":
    #print(start_signal)
    
    for sig in signals:
        if signals[sig]["From"] == node and signals[sig]["Way"] == signals[start_signal]["Way"]:
            #print(signals[sig]["From"],sig)
            if end_signal == '':
                end_signal = sig

            if abs(signals[sig]["Position"][0] - signals[start_signal]["Position"][0]) < abs(signals[end_signal]["Position"][0] - signals[start_signal]["Position"][0]):
                end_signal = sig

    return end_signal
# Find nodes with the same direction than the start semaphore
def find_nodes(start_node,netPaths,semaphores):
    end_nodes = []
    for node in netPaths:
        if netPaths[node]["Next"] == start_node or netPaths[node]["Prev"] == start_node:
            end_nodes.append(node)
    
    return end_nodes

# Find depth of a branch
def branch_depth(nodes,switchesIS,netPaths,nodeRole,nodeSwitch,trainDetectionElements,levelCrossingsIS,platforms):
    
    #print(nodes)
    #print(netPaths)
    #switchesIS[switch]
    #print(nodeRole)
    #print(nodeSwitch)
    
    for node in nodeRole:
        depth = 0
        if "Start" in nodeRole[node] and "Branch" not in nodeRole[node]:
            pivot_node = node
            #print("-",pivot_node)
            while "Start" in nodeRole[pivot_node]:
                next_switch = nodeRole[pivot_node]["Start"]
                
                # Don't choose a one way rail
                if "Branch" in nodeSwitch[next_switch] and "Start" in nodeRole[nodeSwitch[next_switch]["Branch"]]:
                    pivot_node = nodeSwitch[next_switch]["Branch"]
                else:
                    if "Continue" in nodeSwitch[next_switch]:
                        position_a = nodes[pivot_node]["Begin"][1]
                        pivot_node = nodeSwitch[next_switch]["Continue"]
                        position_b = nodes[pivot_node]["Begin"][1]
                        if position_a == position_b:
                            depth += 1
                            break

                #print(pivot_node,next_switch)
                depth += 1
        
        nodes[node] |= {"Depth":depth}
        
# Find the use of each node
def find_node_roles(switchesIS):
    nodeRole = {}
    nodeSwitch = {}
    
    # Find the use of each node
    for switch in switchesIS:
        sw_info = switchesIS[switch]
        
        [begin_right, end_right, name] = identify_relations(sw_info["RightBranch"])
        [begin_left, end_left, name] = identify_relations(sw_info["LeftBranch"])
        
        # Find the start node
        start_node = sw_info["Node"]
        
        # Find continue and branch node node
        [continue_node,branch_node] = [end_right if start_node == begin_right else begin_right,end_left if start_node == begin_left else begin_left]

        if (sw_info["ContinueCourse"] == "right"): 
            # Continue course is right and branch course is left -> It was solved a line before
            pass
        else:
            # Continue course is left and branch course is right -> swap continue and branch
            branch_node,continue_node = continue_node,branch_node
        
        #print(f'     {switch} : {start_node}-{continue_node}-{branch_node} | C_{sw_info["ContinueCourse"]} | B_ {sw_info["BranchCourse"]} | {sw_info["RightBranch"]} | {sw_info["LeftBranch"]}')
        
        if start_node not in nodeRole:
            nodeRole[start_node] = {}
        if continue_node not in nodeRole:
            nodeRole[continue_node] = {}
        if branch_node not in nodeRole:
            nodeRole[branch_node] = {}
        
        nodeRole[start_node] |= {"Start":switch}
        nodeRole[continue_node] |= {"Continue":switch}
        nodeRole[branch_node] |= {"Branch":switch}
        
        nodeSwitch[switch] = {"Start":start_node,"Continue":continue_node,"Branch":branch_node}
    
    return nodeRole,nodeSwitch 

# Find signals for every node in the network
def find_signals(safe_point_file,signal_placement,nodes,netPaths,switchesIS,tracks,trainDetectionElements,borders,bufferStops,levelCrossingsIS,platforms, distanceParameters,config = [1,1,1,1,1,1]):
    
    signals = {}
    printed_signals = []

    # Find the use of each node
    nodeRole,nodeSwitch = find_node_roles(switchesIS)

    # Adapting levelCrossings to be node friendly
    crossing_nodes = {}
    for crossing in levelCrossingsIS:
        if levelCrossingsIS[crossing]["Net"] not in crossing_nodes:
            crossing_nodes[levelCrossingsIS[crossing]["Net"]] = []
        crossing_nodes[levelCrossingsIS[crossing]["Net"]].append({"Id":crossing,"Position":levelCrossingsIS[crossing]["Position"],"Coordinate":levelCrossingsIS[crossing]["Coordinate"]})

    # Find depth of branches
    branch_depth(nodes,switchesIS,netPaths,nodeRole,nodeSwitch,trainDetectionElements,levelCrossingsIS,platforms)

    bufferStopDistance = distanceParameters['bufferStopDistance']            #100
    lineBordersDistance = distanceParameters['lineBordersDistance']          #100
    railJointsDistance = distanceParameters['railJointsDistance']            #200
    levelCrossingsDistance = distanceParameters['levelCrossingsDistance']    #250
    platformsDistance = distanceParameters['platformsDistance']              #300

    # Find signals for bufferStops
    if(config[0]==1):
        signals = find_signals_bufferStops(netPaths,nodes,bufferStops,signals,distance = bufferStopDistance)
        printed_signals = [*signals]
        if printed_signals:
            print(f' Creating signals for bufferstops:{printed_signals}')
    
    # Find signals for lineborders
    if(config[1]==1):
        signals = find_signals_lineborders(netPaths,nodes,borders,signals,distance = lineBordersDistance)
        printed_signals = [*signals]
        if [*signals] != printed_signals:
            print(f' Creating signals for lineborders:{printed_signals}')

    # Find signals for railJoints
    if(config[2]==1):
        signals = find_signals_joints(signal_placement,nodes,netPaths,trainDetectionElements,signals,distance = railJointsDistance)
        if [*signals] != printed_signals:
            print(f' Creating signals for Joints:{[x for x in [*signals] if x not in printed_signals]}')
        printed_signals = [*signals]
    
    # Find signals for level crossings
    if(config[3]==1):
        signals = find_signals_crossings(signal_placement,nodes,netPaths,levelCrossingsIS,signals,distance = levelCrossingsDistance)
        if [*signals] != printed_signals:
            print(f' Creating signals for crossings:{[x for x in [*signals] if x not in printed_signals]}')
        printed_signals = [*signals]

    # Find signals for platforms
    if(config[4]==1):
        signals = find_signals_platforms(signal_placement,nodes,netPaths,platforms,signals,distance = platformsDistance)
        if [*signals] != printed_signals:
            print(f' Creating signals for platforms:{[x for x in [*signals] if x not in printed_signals]}')
        printed_signals = [*signals]
   
    # Find signals for switches
    if(config[5]==1):
        signals = find_signals_switches(signal_placement,nodeRole,nodeSwitch,nodes,netPaths,switchesIS,tracks,crossing_nodes,trainDetectionElements,signals)
        if [*signals] != printed_signals:
            print(f' Creating signals for switches:{[x for x in [*signals] if x not in printed_signals]}')
        printed_signals = [*signals]

    #print(signals)
    for sig in signals:
        #print(sig)
        intrinsic_coordinate = calculate_intrinsic_coordinate([signals[sig]["Position"][0],-signals[sig]["Position"][1]],nodes[signals[sig]["From"]]["All"])
        signals[sig]["Coordinate"] = intrinsic_coordinate
    return signals

# Find signals for bufferStops
def find_signals_bufferStops(netPaths,nodes,bufferStops,signals,distance = 100):
    #print(bufferStops)
    # Find every end of the network
    for node in nodes:
        # If the node is a bufferStop:
        if node in bufferStops:
            for i in range(len(bufferStops[node])):
                #print(bufferStops[node][i])
                # Add circulation signal with the direction of the exit
                if node in netPaths:
                    side = "Prev" if "Next" in netPaths[node] else "Next"
                    position_index = "End" if side == "Next" else "Begin"
                else:
                    position_index = "Begin" if i == 0 else "End"
                
                sig_number = "sig"+str(len(signals)+1).zfill(2)
                
                atTrack = "left" if bufferStops[node][i]["Direction"] == "normal" else "right"
                direction = bufferStops[node][i]["Direction"]
                
                #print(node,netPaths[node],side,direction,nodes[node])
                
                if position_index == "End":
                    position = [nodes[node][position_index][0]-distance,-nodes[node][position_index][1]]
                else:
                    position = [nodes[node][position_index][0]+distance,-nodes[node][position_index][1]]
                    
                way = "_right" if position[0] < nodes[node][position_index][0] else "_left"

                #print(node,position_index,position)
                name = "T"+str(len(signals)+1).zfill(2)
                signals[name] = {"From":node,"To":bufferStops[node][i]["Id"]+way,"Direction":direction,"AtTrack":atTrack,"Type":"Stop","Position":position,"Name":name}
                #print(sig_number,signals[sig_number])

                sig_number = "sig"+str(len(signals)+1).zfill(2)
                name = "T"+str(len(signals)+1).zfill(2)
                atTrack = "right" if bufferStops[node][i]["Direction"] == "normal" else "left"
                direction = "reverse" if bufferStops[node][i]["Direction"] == "normal" else "normal"
                way = "_right" if way == '_left' else '_left'
                signals[name] = {"From":node,"To":node+way,"Direction":direction,"AtTrack":atTrack,"Type":"Stop","Position":position,"Name":name}
                #print(sig_number,signals[sig_number])
    return signals

# Find signals for lineborders
def find_signals_lineborders(netPaths,nodes,borders,signals,distance = 100):
    #print(borders)
    # Find every end of the network
    for node in nodes:
        # If the node is a lineborder:
        if node in borders:
            #for i in range(len(borders[node])):
            #print(netPaths[node])
            # Add circulation signal with the direction of the exit
            if node in netPaths:
                side = "Prev" if "Next" in netPaths[node] else "Next"
                position_index = "Begin" if "Next" in netPaths[node] else "End"
            #else:
            #    position_index = "Begin" if i == 0 else "End"
            
            sig_number = "sig"+str(len(signals)+1).zfill(2)
            
            if side == "prev":
                if borders[node]['Inverter']:
                    atTrack = "right"
                else:
                    atTrack = "left"
            else:
                if borders[node]['Inverter']:
                    atTrack = "left"
                else:
                    atTrack = "right"

            #atTrack = "left" if side == "prev" else "right"
            
            if side == "prev":
                if borders[node]['Inverter']:
                    direction = "reverse"
                else:
                    direction = "normal"
            else:
                if borders[node]['Inverter']:
                    direction = "normal"
                else:
                    direction = "reverse"

            #print(node,netPaths[node],side,direction,nodes[node])
            
            if position_index == "End":
                position = [nodes[node][position_index][0]-distance,-nodes[node][position_index][1]]
            else:
                position = [nodes[node][position_index][0]+distance,-nodes[node][position_index][1]]

            way = "_right" if position[0] < nodes[node][position_index][0] else "_left"

            #print(node,position_index,position)
            name = "L"+str(len(signals)+1).zfill(2)
            #if name == 'L41':
            #    return signals

            signals[name] = {"From":node,"To":borders[node]["LineBorder"]+way,"Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}
            #print(sig_number,signals[sig_number])
    return signals

# Find signals for switches
def find_signals_switches(signal_placement,nodeRole,nodeSwitch,nodes,netPaths,switchesIS,tracks,crossing_nodes,trainDetectionElements,signals):

    #print(netPaths)
    #print(nodeRole)
    #print(nodeSwitch)
    #print(netPaths)

    # Find every switch in the network
    for switch in switchesIS:
        sw_info = switchesIS[switch]
        start_node = nodeSwitch[switch]["Start"]
        continue_node = nodeSwitch[switch]["Continue"]
        branch_node = nodeSwitch[switch]["Branch"]
        #print(f'  {switch} : [{start_node}|{continue_node}|{branch_node}]')
        
        # For continue course
        signal_type = "Circulation" if nodes[continue_node]["Lines"] == 1 else "Manouver"
        next_node = continue_node
        while "Branch" in nodeRole[next_node] and nodeRole[next_node]["Branch"] != None:
            next_switch = nodeRole[next_node]["Branch"]
            next_node = nodeSwitch[next_switch]["Start"]
            signal_type = "Manouver"
            #print(f'    {switch} -> {next_switch} @ {next_node}')
        continue_node = next_node
        if continue_node in signal_placement:  
            
            atTrack = "left" if "Next" in netPaths[branch_node] and start_node in netPaths[branch_node]["Next"] else "right"
            pos = sw_info["Position"]
            
            side = "Next" if ("Next" in netPaths[branch_node] and start_node in netPaths[branch_node]["Next"]) else "Prev"

            name = "C"+str(len(signals)+1).zfill(2)
            if side in signal_placement[continue_node]:
                sig_number = "sig"+str(len(signals)+1).zfill(2)
                
                #print(f'Continue {continue_node} {switch} {side} {nodes[continue_node]["Inverter"]} {sig_number}')
                #position = closest_safe_point(signal_placement[continue_node][side],pos,side)
                
                position_prev = closest_safe_point(signal_placement[continue_node]["Prev"],pos,"Prev") if "Prev" in signal_placement[continue_node] else [0,0]
                position_next = closest_safe_point(signal_placement[continue_node]["Next"],pos,"Next") if "Next" in signal_placement[continue_node] else [0,0]

                dist_prev = abs(position_prev[0] - pos[0]) if position_prev != [0,0] else 10000
                dist_next = abs(position_next[0] - pos[0]) if position_next != [0,0] else 10000
                
                #print(f'XXX {name} {signal_placement[continue_node]} {dist_prev} {dist_next}')

                position = position_next if (dist_next < dist_prev) else position_prev

                direction = "normal" if position[0] < pos[0] else "reverse"
                atTrack = "left" if position[0] < pos[0] else "right"
                way = "_right" if position[0] < pos[0] else "_left"

                if nodes[continue_node]["Inverter"]:
                    direction = 'normal' if direction == 'reverse' else 'reverse'
                    atTrack = 'left' if direction == 'normal' else 'right'
                    #way = '_left' if direction == 'normal' else '_right'

                signals[name] = {"From":continue_node,"To":continue_node+way,"Direction":direction,"AtTrack":atTrack,"Type":signal_type,"Position":position,"Name":name}
                #print(f'     Continue - {sig_number}:{signals[sig_number]}')
        
        # For branch course
        if branch_node in signal_placement and "Start" not in nodeRole[branch_node]:
            
            sig_number = "sig"+str(len(signals)+1).zfill(2)
            pos = sw_info["Position"]

            side = "Next" if ("Next" in netPaths[branch_node] and start_node in netPaths[branch_node]["Next"]) else "Prev"
            
            position = [signal_placement[branch_node][side][0][0],-signal_placement[branch_node][side][0][1]]
            
            #direction = "normal" if "Next" in netPaths[branch_node] and start_node in netPaths[branch_node]["Next"] else "reverse"
            #atTrack = "left" if "Next" in netPaths[branch_node] and start_node in netPaths[branch_node]["Next"] else "right"
            direction = "normal" if position[0] < pos[0] else "reverse"
            atTrack = "left" if position[0] < pos[0] else "right"
            way = "_right" if position[0] < pos[0] else "_left"

            #direction = "reverse"
            #atTrack = "right"

            if nodes[start_node]["Inverter"]:
                direction = 'normal' if direction == 'reverse' else 'reverse'
                atTrack = 'left' if direction == 'right' else 'right'
            
            name = "B"+str(len(signals)+1).zfill(2)
            
            if name == 'B92':
                atTrack = 'left'
            
            #print(f'Branch {branch_node} {switch} {side} {nodes[branch_node]["Inverter"]} {sig_number}')

            signals[name] = {"From":branch_node,"To":branch_node+way,"Direction":direction,"AtTrack":atTrack,"Type":"Manouver","Position":position,"Name":name}
            #print(f'     Branch - {sig_number}:{signals[sig_number]}')
        
        # For start course
        # Circulation
        
        # If start is also a branch, don't add signal
        if start_node in signal_placement:
            sig_number = "sig"+str(len(signals)+1).zfill(2)
            name = "S"+str(len(signals)+1).zfill(2)

            pos = sw_info["Position"]
            
            side = "Next" if "Next" in signal_placement[start_node] else "Prev" # Changed NetPaths for signal_placement
            
            if nodes[start_node]["Inverter"]:
                side = "Prev" if side == "Next" else "Next"

            #print(f'Start {start_node} {switch} {side} {nodes[start_node]["Inverter"]} {sig_number}')
            position_prev = closest_safe_point(signal_placement[start_node]["Prev"],pos,"Prev") if "Prev" in signal_placement[start_node] else [0,0]
            position_next = closest_safe_point(signal_placement[start_node]["Next"],pos,"Next") if "Next" in signal_placement[start_node] else [0,0]

            dist_next = abs(position_next[0] - pos[0])
            dist_prev = abs(position_prev[0] - pos[0])

            position = position_next if (dist_next < dist_prev) else position_prev

            #print(f'{name} {switch} {pos} {start_node} {dist_prev} {dist_next} {position}')

            direction = "normal" if position[0] < pos[0] else "reverse"
            atTrack = "left" if position[0] < pos[0] else "right"
            way = "_right" if position[0] < pos[0] else "_left"

            if nodes[start_node]["Inverter"]:
                direction = 'normal' if direction == 'reverse' else 'reverse'
                atTrack = 'left' if direction == 'normal' else 'right'
            
            if start_node in crossing_nodes:
                position = position_next if position == position_prev else position_prev

            signals[name] = {"From":start_node,"To":start_node+way,"Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}
            #print(f'     Start circulation - {sig_number}:{signals[sig_number]}')
            
            # Manouver
            depth = nodes[start_node]["Depth"]
            #print(nodes[start_node])
            #print(depth)
            while depth > 0:
                sig_number = "sig"+str(len(signals)+1).zfill(2)
                name = "H"+str(len(signals)+1).zfill(2)
                
                pos = sw_info["Position"]
                side = "Next" if "Next" in netPaths[start_node] else "Prev"

                #if nodes[start_node]["Inverter"]:
                #    side = "Prev" if side == "Next" else "Next"

                #print(f'Start complex {start_node} {switch} {side} {nodes[start_node]["Inverter"]} {sig_number}')
                position_prev = closest_safe_point(signal_placement[start_node]["Prev"],pos,"Prev") if "Prev" in signal_placement[start_node] else [0,0]
                position_next = closest_safe_point(signal_placement[start_node]["Next"],pos,"Next") if "Next" in signal_placement[start_node] else [0,0]

                dist_next = abs(position_next[0] - pos[0])
                dist_prev = abs(position_prev[0] - pos[0])

                position = position_next if (dist_next < dist_prev) else position_prev
                
                direction = "normal" if position[0] < pos[0] else "reverse"
                atTrack = "left" if position[0] < pos[0] else "right"
                way = "_right" if position[0] < pos[0] else "_left"

                if nodes[start_node]["Inverter"]:
                    direction = 'normal' if direction == 'reverse' else 'reverse'
                    atTrack = 'left' if direction == 'normal' else 'right'

                if start_node in crossing_nodes:
                    position = position_next if position == position_prev else position_prev

                signals[name] = {"From":start_node,"To":start_node+way,"Direction":direction,"AtTrack":atTrack,"Type":"Manouver","Position":position,"Name":name}
                #print(f'     Start manouver - {sig_number}:{signals[sig_number]}')
                depth -= 1

    return signals

# Find signals for railJoints
def find_signals_joints(signal_placement,nodes,netPaths,trainDetectionElements,signals,distance = 200):
    
    # Find every railway joint on the network
    for joint in trainDetectionElements:
        node = trainDetectionElements[joint]["Node"] 
        pos = trainDetectionElements[joint]["Position"]
        # Add an entrance signal and an exit signal
        sig_number = "sig"+str(len(signals)+1).zfill(2)
        direction = "normal"
        atTrack = "left"

        if nodes[node]['Inverter']:
            atTrack = "right"
            neighbor = "Next"
            direction = "reverse"
        else:
            atTrack = "left"
            neighbor = "Next"
            direction = "normal"

        position = closest_safe_point(signal_placement[node][neighbor],pos,neighbor)
        name = "J"+str(len(signals)+1).zfill(2)

        # If the safe position is far away, avoid the signal
        #print(f'OBJ:{pos} | {position} | d {position[0]-pos[0]}')
        if (abs(position[0]-pos[0]) < distance):
            signals[name] = {"From":node,"To":node+"_right","Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}

        sig_number = "sig"+str(len(signals)+1).zfill(2)
        direction = "reverse"
        atTrack = "right"

        if nodes[node]['Inverter']:
            atTrack = "left"
            direction = "normal"
            neighbor = "Prev"
        else:
            atTrack = "right"
            direction = "reverse"
            neighbor = "Prev"

        position = closest_safe_point(signal_placement[node][neighbor],pos,neighbor)
        name = "J"+str(len(signals)+1).zfill(2)

        # If the safe position is far away, avoid the signal
        #print(f'OBJ:{pos} | {position} | d {position[0]-pos[0]}')
        if (abs(position[0]-pos[0]) < distance):
            signals[name] = {"From":node,"To":node+"_left","Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}
            
    return signals

# Find signals for level crossings
def find_signals_crossings(signal_placement,nodes,netPaths,levelCrossingsIS,signals,distance = 250):
    # Find every level crossing on the network
    for crossing in levelCrossingsIS:
        #print(levelCrossingsIS[crossing])
        node = levelCrossingsIS[crossing]["Net"] 
        #print(node,nodes[node])
        pos = levelCrossingsIS[crossing]["Position"]
        # Add an entrance signal and an exit signal
        sig_number = "sig"+str(len(signals)+1).zfill(2)
        direction = "normal"
        atTrack = "left"

        if nodes[node]['Inverter']:
            #atTrack = "left"
            #direction = "reverse"
            neighbor = "Prev"
        else:
            #atTrack = "left"
            #direction = "normal"
            neighbor = "Next"

        position = closest_safe_point(signal_placement[node][neighbor],pos,neighbor)
        name = "X"+str(len(signals)+1).zfill(2)
        
        # If the safe position is far away, avoid the signal
        #print(f'OBJ:{sig_number} | p_{pos} | s_{position} | d {position[0]-pos[0]}')
        if (abs(position[0]-pos[0]) < distance):
            signals[name] = {"From":node,"To":node+"_right","Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}
        
        sig_number = "sig"+str(len(signals)+1).zfill(2)
        direction = "reverse"
        atTrack = "right"

        if not nodes[node]['Inverter']:
            #atTrack = "right"
            #direction = "reverse"
            neighbor = "Prev"
        else:
            #atTrack = "right"
            #direction = "normal"
            neighbor = "Next"
            
        position = closest_safe_point(signal_placement[node][neighbor],pos,neighbor)

        name = "X"+str(len(signals)+1).zfill(2)
        # If the safe position is far away, avoid the signal
        #print(f'OBJ:{sig_number} | p_{pos} | s_{position} | d {position[0]-pos[0]}')
        if (abs(position[0]-pos[0]) < distance):
            signals[name] = {"From":node,"To":node+"_left","Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}
            
    return signals

# Find signals for platforms
def find_signals_platforms(signal_placement,nodes,netPaths,platforms,signals,distance = 300):
    # Find every platform on the network
    for platform in platforms:
        node = platforms[platform]["Net"] 
        pos = platforms[platform]["Position"]
        size = int(platforms[platform]["Value"])
        
        # Add an entrance signal and an exit signal
        sig_number = "sig"+str(len(signals)+1).zfill(2)
        direction = "reverse"
        atTrack = "right"
        neighbor = "Next"
        safe_point = signal_placement[node][neighbor]

        if not nodes[node]['Inverter']:
            atTrack = "right"
            direction = "reverse"
        else:
            atTrack = "left"
            direction = "normal"

        position = closest_safe_point(safe_point,pos,neighbor)
        if nodes[node]['Inverter']:
            position[0] = position[0] - 80
        else:
            position[0] = position[0] + 80

        name = "P"+str(len(signals)+1).zfill(2)
        
        # If the safe position is far away, avoid the signal
        #print(f'OBJ:{sig_number} | {neighbor} | {pos} | {safe_point} | {position} | d {position[0]-pos[0]}')
        if (abs(position[0]-pos[0]) < distance):
            signals[name] = {"From":node,"To":node+"_left","Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}

        sig_number = "sig"+str(len(signals)+1).zfill(2)   
        direction = "normal"
        atTrack = "left"
        neighbor = "Prev"

        if nodes[node]['Inverter']:
            atTrack = "right"
            direction = "reverse"
        else:
            atTrack = "left"
            direction = "normal"

        position = closest_safe_point(signal_placement[node][neighbor],pos,neighbor)
        if nodes[node]['Inverter']:
            position[0] = position[0] + 80
        else:
            position[0] = position[0] - 80

        name = "P"+str(len(signals)+1).zfill(2)
        
        # If the safe position is far away, avoid the signal
        #print(f'OBJ:{sig_number} | {neighbor} | {pos} | {position} | d {position[0]-pos[0]}')
        if (abs(position[0]-pos[0]) < distance):
            signals[name] = {"From":node,"To":node+"_right","Direction":direction,"AtTrack":atTrack,"Type":"Circulation","Position":position,"Name":name}
            
    return signals

# Find closest point between options
def closest_safe_point(safe_points,position,direction,test=False):
    closest = []
    distance = []

    for safe_point in safe_points:
        distance.append(abs(position[0]-safe_point[0]))
        if (direction == "Next" and position[0]  < safe_point[0]):
            distance[-1] = 9999
        if (direction == "Prev" and position[0]  > safe_point[0]):
            distance[-1] = 9999

    if test:
        print(f'{safe_points} {position} {direction} {distance}')    

    index = distance.index(min(distance))
    closest = safe_points[index]

    if test:
        print("**",safe_points,position,direction,closest)
        
    if (direction == "Next" and position[0] < closest[0]):
        #print("LEFT")
        if index+1 in safe_points:
            closest = safe_points[index+1]
        else:
            closest = safe_points[index]
    if (direction == "Prev" and position[0] > closest[0]):
        #print("RIGHT")
        if index-1 in safe_points:
            closest = safe_points[index-1]
        else:
            closest = safe_points[index]

    if test:
        print("$$",safe_points,position,direction,closest)
        
    return [closest[0],-closest[1]]

# Is it a safe point between?
def no_safe_points_between(safe_points,a_position,b_position):
    
    for safe in safe_points:
        if a_position > safe and safe > b_position:
            return False
        if a_position < safe and safe < b_position:
            return False 
    return True

# Reduce redundant signals
def reduce_signals(signals,signal_placement):
    
    delete = []
    #for sig in signals:
    #    print(f'{sig, signals[sig]}')

    #print(signal_placement)
    for signal_a in signals:
        for signal_b in signals:
            if signal_a != signal_b and signals[signal_a]["From"] == signals[signal_b]["From"]:

                side = "Next" if signals[signal_a]["AtTrack"] == "right" else "Prev"
                #print(signals[signal_a]["From"],signal_placement[signals[signal_a]["From"]],side)
                
                danger_positions = [danger[0] for danger in signal_placement[signals[signal_a]["From"]][side]] if side in signal_placement[signals[signal_a]["From"]] else []

                a_position = signals[signal_a]["Position"][0]
                b_position = signals[signal_b]["Position"][0]

                if(signals[signal_a]["Direction"] == signals[signal_b]["Direction"] and signals[signal_a]["Name"][0] != "S" and abs(a_position-b_position) < 100):
                    if signal_a not in delete and signal_b not in delete:
                        print(f'removing {signal_a} for {signal_b}')
                        delete.append(signal_a)

                if (signals[signal_a]["Direction"] == signals[signal_b]["Direction"] and signals[signal_a]["Name"][0] == "L" and abs(a_position-b_position) < 500):
                    if signal_a not in delete and signal_b not in delete:
                        print(f'removing {signal_a} for {signal_b}')
                        delete.append(signal_a)

                if (signals[signal_a]["Direction"] == signals[signal_b]["Direction"] and signals[signal_a]["Name"][0] == "T" and abs(a_position-b_position) < 500):
                    if signal_b not in delete and signals[signal_b]["Name"][0] != "H" and signal_a not in delete:
                        print(f'removing {signal_b} for {signal_a}')
                        delete.append(signal_b)

                if(signals[signal_a]["Direction"] == signals[signal_b]["Direction"] and signals[signal_a]["Name"][0] == "X" and abs(a_position-b_position) < 250):
                    if signal_a not in delete and signal_b not in delete and signals[signal_b]["Name"][0] == "P":
                        print(f'removing {signal_b} for {signal_a}')
                        delete.append(signal_b)

                if (signals[signal_a]["Direction"] == signals[signal_b]["Direction"] and signals[signal_a]["Name"][0] == "J" and abs(a_position-b_position) < 500):
                    if signal_b not in delete and signals[signal_b]["Name"][0] != "S" and signals[signal_b]["Name"][0] != "H" and signals[signal_b]["Name"][0] != "T" and signal_a not in delete:
                        print(f'removing {signal_b} for {signal_a}')
                        delete.append(signal_b)

                if (signal_a not in delete and a_position == b_position and signals[signal_a]["Direction"] == signals[signal_b]["Direction"]):
                    #print(f'{signal_a} {a_position} | {signal_b} {b_position}')
                    
                    if signal_b not in delete and (signals[signal_b]["Name"][0] != "S" and signals[signal_b]["Name"][0] != "H") and signal_a not in delete:
                        print(f'removing {signal_b} for {signal_a}')
                        delete.append(signal_b)

                #print(f'{signal_a} {signal_b} {no_safe_points_between(danger_positions,a_position,b_position)} {abs(a_position-b_position)}')
                if no_safe_points_between(danger_positions,a_position,b_position) and abs(a_position-b_position) < 500:
                    if signals[signal_a]["Type"] == "Circulation" and signals[signal_b]["Type"] == "Circulation":
                        if signals[signal_a]["Direction"] == signals[signal_b]["Direction"]:
                            if signals[signal_a]["AtTrack"] == signals[signal_b]["AtTrack"]:
                                if int(signal_a[1:]) < int(signal_b[1:]):
                                    if signal_b not in delete and signals[signal_b]["Name"][0] != "S" and signal_a not in delete:
                                        print(f'removing {signal_b} for {signal_a}')
                                        delete.append(signal_b)
                    
                    if signals[signal_a]["Direction"] == signals[signal_b]["Direction"]:
                        if signals[signal_a]["Name"][0] == "J" and signals[signal_b]["Name"][0] == "T":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "T" and signals[signal_b]["Name"][0] == "J":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)
                        if signals[signal_a]["Name"][0] == "C" and signals[signal_b]["Name"][0] == "S":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "S" and signals[signal_b]["Name"][0] == "C":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)
                        if signals[signal_a]["Name"][0] == "C" and signals[signal_b]["Name"][0] == "P":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "P" and signals[signal_b]["Name"][0] == "C":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)
                        if signals[signal_a]["Name"][0] == "S" and signals[signal_b]["Name"][0] == "J":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)
                        if signals[signal_a]["Name"][0] == "J" and signals[signal_b]["Name"][0] == "S":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "L" and signals[signal_b]["Name"][0] == "P":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)  
                        if signals[signal_a]["Name"][0] == "P" and signals[signal_b]["Name"][0] == "L":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)  
                        if signals[signal_a]["Name"][0] == "B" and signals[signal_b]["Name"][0] == "T":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)  
                        if signals[signal_a]["Name"][0] == "T" and signals[signal_b]["Name"][0] == "B":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)  
                        if signals[signal_a]["Name"][0] == "P" and signals[signal_b]["Name"][0] == "B":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "B" and signals[signal_b]["Name"][0] == "P":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)   
                        if signals[signal_a]["Name"][0] == "X" and signals[signal_b]["Name"][0] == "B":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "B" and signals[signal_b]["Name"][0] == "X":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)          
                        if signals[signal_a]["Name"][0] == "T" and signals[signal_b]["Name"][0] == "H":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)   
                        if signals[signal_a]["Name"][0] == "P" and signals[signal_b]["Name"][0] == "X":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "X" and signals[signal_b]["Name"][0] == "P":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)   

                        if signals[signal_a]["Name"][0] == "B" and signals[signal_b]["Name"][0] == "B":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_a} for {signal_b}')
                                delete.append(signal_a)
                        if signals[signal_a]["Name"][0] == "B" and signals[signal_b]["Name"][0] == "B":
                            if signal_a not in delete and signal_b not in delete:
                                print(f'removing {signal_b} for {signal_a}')
                                delete.append(signal_b)

    for delete_signal in delete:
        del signals[delete_signal]

def export_signal(file,signals,object):

    #for signal in signals:
    #    print(f'{signal} {signals[signal]}')

    with open(file, "w") as f: 
        #print(signals)
        for sig in signals:
            if "Way" in signals[sig]:
                f.write(f'{str(sig).zfill(2)} [{signals[sig]["Name"]}] {signals[sig]["Way"]}:\n')
            else:
                f.write(f'{str(sig).zfill(2)} [{signals[sig]["Name"]}]:\n')
            f.write(f'\tFrom: {signals[sig]["From"]} | To: {signals[sig]["To"]}\n')
            #f.write(f'\tSwitch: {signals[sig]["Switch"]}\n')
            f.write(f'\tType: {signals[sig]["Type"]} | Direction: {signals[sig]["Direction"]} | AtTrack: {signals[sig]["AtTrack"]} \n')
            f.write(f'\tPosition: {signals[sig]["Position"]} | Coordinate: {signals[sig]["Coordinate"]}\n')
        f.close()

    # Create que semaphore object
    
    # Create semaphore for FunctionalInfrastructure
    if (object.Infrastructure.FunctionalInfrastructure.SignalsIS == None):
        print(" No signals found --> Creating new signalling structure")
        object.Infrastructure.FunctionalInfrastructure.create_SignalsIS()
        if (object.Infrastructure.FunctionalInfrastructure.SignalsIS != None):
            print(" Signals structure found!")    
            for i in range(len(signals)):
                object.Infrastructure.FunctionalInfrastructure.SignalsIS.create_SignalIS()
                # Update the information
                sem = object.Infrastructure.FunctionalInfrastructure.SignalsIS.SignalIS[i]
                # Create atributes
                sem.Id = list(signals)[i]                # Id
                sem.IsSwitchable = "false"                   # IsSwitchable
                # Create name
                sem.create_Name()
                #print(sem.Id,signals[sem.Id]["Name"])
                sem.Name[0].Name = signals[sem.Id]["Name"]  #"S"+sem.Id[-2:]     # Name
                sem.Name[0].Language = "en"                         # Language
                # Create SpotLocation
                sem.create_SpotLocation()
                sem.SpotLocation[0].Id = sem.Id+"_sloc01"                      # Id="sig90_sloc01" 
                sem.SpotLocation[0].NetElementRef = signals[sem.Id]["From"]  # NetElementRef="ne15" 
                sem.SpotLocation[0].ApplicationDirection  = signals[sem.Id]["Direction"]                       # ApplicationDirection="normal" 
                sem.SpotLocation[0].IntrinsicCoord = signals[sem.Id]["Coordinate"]                                # IntrinsicCoord 0 to 1 #TODO CALCULATE INTRINSIC COORDINATE
                # Create Designator
                sem.create_Designator()
                sem.Designator[0].Register = "_Example"     # Register="_Example" 
                sem.Designator[0].Entry = "SIGNAL S"+re.findall(r'\d+', sem.Id)[0]#sem.Id[-2:]                                            # Entry="SIGNAL S07"
                # Create SignalConstruction
                sem.create_SignalConstruction() 
                sem.SignalConstruction[0].Type = "light"               # Type
                sem.SignalConstruction[0].PositionAtTrack = signals[sem.Id]["AtTrack"]    # PositionAtTrack
                #print(object.Infrastructure.FunctionalInfrastructure.SignalsIS.SignalIS[i])
        
    # Create semaphore for InfrastructureVisualizations
    if (object.Infrastructure.InfrastructureVisualizations.Visualization != None):
        visualization_length = len(object.Infrastructure.InfrastructureVisualizations.Visualization[0].SpotElementProjection)
        
        for i in range(len(signals)):
            sem = object.Infrastructure.InfrastructureVisualizations.Visualization[0]
            # Add new SpotElementProjection
            sem.create_SpotElementProjection()
            # Create atributes
            #print(list(semaphores)[i] )
            #print(sem.SpotElementProjection[visualization_length+i].__dict__) 
            sem.SpotElementProjection[visualization_length+i].RefersToElement = list(signals)[i] # TODO IF "sig" -> IT IS NOT PRINTED!
            sem.SpotElementProjection[visualization_length+i].Id = "vis01_sep"+str(visualization_length+i+1)
            # Create name
            sem.SpotElementProjection[visualization_length+i].create_Name()
            sem.SpotElementProjection[visualization_length+i].Name[0].Name = "S"+re.findall(r'\d+', list(signals)[i])[0]#list(signals)[i][-2:]     # Name
            sem.SpotElementProjection[visualization_length+i].Name[0].Language = "en"                         # Languag
            # Create coordinate
            sem.SpotElementProjection[visualization_length+i].create_Coordinate()
            sem.SpotElementProjection[visualization_length+i].Coordinate[0].X = str(signals[list(signals)[i]]["Position"][0])
            sem.SpotElementProjection[visualization_length+i].Coordinate[0].Y = str(signals[list(signals)[i]]["Position"][1])
    
    # Create semaphore for AssetsForIL
    if (object.Interlocking.AssetsForIL != None):
        # Create SignalsIL
        AssetsForIL = object.Interlocking.AssetsForIL[0]
        AssetsForIL.create_SignalsIL()
        sem = AssetsForIL.SignalsIL
        # Add new SignalIL for each semaphore
        for i in range(len(signals)):
            sem.create_SignalIL()
            # Create atributes
            sem.SignalIL[i].Id = "il_"+list(signals)[i]                # Id
            sem.SignalIL[i].IsVirtual = "false"                           # IsVirtual
            sem.SignalIL[i].ApproachSpeed = "0"                           # ApproachSpeed
            sem.SignalIL[i].PassingSpeed = "0"                            # PassingSpeed
            sem.SignalIL[i].ReleaseSpeed = "0"                            # ReleaseSpeed
            # Create RefersTo
            sem.SignalIL[i].create_RefersTo()
            sem.SignalIL[i].RefersTo.Ref = list(signals)[i]            # RefersTo
        
        # Create Routes
        #AssetsForIL.create_Routes()
        #routes = AssetsForIL.Routes
    return

def find_signal_positions(nodes,netPaths,switchesIS,tracks,trainDetectionElements,bufferStops,levelCrossingsIS,platforms,dist = 300, length = 200):
    signal_placement = {}
    step = 200

    # Adapting railJoints to be node friendly
    railJoints = {}
    for element in trainDetectionElements:
        if "RailJoint" in trainDetectionElements[element]["Type"]:
            if trainDetectionElements[element]["Node"] not in railJoints:
                railJoints[trainDetectionElements[element]["Node"]] = []
            railJoints[trainDetectionElements[element]["Node"]].append({"Joint":trainDetectionElements[element]["Name"],"Coordinate":trainDetectionElements[element]["Coordinate"],"Position":trainDetectionElements[element]["Position"]})

    # Adapting platforms to be node friendly
    platforms_node = {}
    for platform in platforms:
        node = platforms[platform]["Net"]
        if node not in platforms_node:
            platforms_node[node] = []
        platforms_node[node].append({"Platform":platform,"Value":platforms[platform]["Value"],"Direction":platforms[platform]["Direction"],"Position":platforms[platform]["Position"]})

    # Adapting levelCrossings to be node friendly
    crossing_nodes = {}
    for crossing in levelCrossingsIS:
        if levelCrossingsIS[crossing]["Net"] not in crossing_nodes:
            crossing_nodes[levelCrossingsIS[crossing]["Net"]] = []
        crossing_nodes[levelCrossingsIS[crossing]["Net"]].append({"Id":crossing,"Position":levelCrossingsIS[crossing]["Position"],"Coordinate":levelCrossingsIS[crossing]["Coordinate"]})

    # Move around every node
    for node in nodes:
        # Check if there is a RailJoint, Platform, LevelCrossing or curve.
        # If there is a RailJoint:
        if node in railJoints:
            for railJoint in railJoints[node]:
                railJoint_position = railJoint["Position"]
                print(f"  {node} has a RailJoint[{railJoint['Joint']}] @ {railJoint_position}")
                if node not in signal_placement:
                    signal_placement[node] = {"Next":[],"Prev":[]}

                # next_position = RailJoint_position - one step
                next_place = signal_placement[node]["Next"]
                next_place = [round(railJoint_position[0] - step/2,1),round(railJoint_position[1],1)]
                
                # prev_position = RailJoint_position + one step
                prev_place = signal_placement[node]["Prev"]
                prev_place = [round(railJoint_position[0] + step/2,1),round(railJoint_position[1],1)]

                # Upload both positions to the node
                #signal_placement[node] |= {"Next":next_place,"Prev":prev_place} 
                if next_place:
                    signal_placement[node]["Next"].append(next_place)
                if prev_place:
                    signal_placement[node]["Prev"].append(prev_place)

        #print(signal_placement)
        # If there is a Platform:
        if node in platforms_node:
            for platform in platforms_node[node]:
                platform_position = platform["Position"]

            #platform_position = platforms_node[node]["Position"]
            print(f'  {node} has a Platform[{platform["Platform"]}] @ {platform_position}')
            if node not in signal_placement:
                signal_placement[node] = {"Next":[],"Prev":[]}

                # next_position = Platform_position - one step
                next_place = signal_placement[node]["Next"]
                next_place = [round(platform_position[0]-step,1),round(platform_position[1],1)]

                # prev_position = Platform_position + one step 
                prev_place = signal_placement[node]["Prev"]
                prev_place = [round(platform_position[0]+step,1),round(platform_position[1],1)]

                # Upload both positions to the node
                #signal_placement[node] |= {"Next":next_place,"Prev":prev_place} 
                if next_place:
                    #print(f'{platforms_node[node]["Platform"]} {"Next"} {next_place}')
                    signal_placement[node]["Next"].append(next_place)
                if prev_place:
                    #print(f'{platforms_node[node]["Platform"]} {"Prev"} {prev_place}')
                    signal_placement[node]["Prev"].append(prev_place)

        # If there is a LevelCrossing:
        if node in crossing_nodes:
            for crossing in crossing_nodes[node]:
                crossing_positions = crossing["Position"]

                #crossing_positions = crossing_nodes[node]["Position"]
                if (nodes[node]["Inverter"]):
                    crossing_positions[0] = crossing_positions[0] + 45
                else:
                    crossing_positions[0] = crossing_positions[0] - 45
                print(f'  {node} has a LevelCrossing[{crossing["Id"]}] @ {crossing_positions}')
                if node not in signal_placement:
                    signal_placement[node] = {"Next":[],"Prev":[]}

                # next_position = LevelCrossing_position - one step   
                next_place = signal_placement[node]["Next"]
                next_place = [round(crossing_positions[0]-step,1),round(crossing_positions[1],1)]
                
                # prev_position = LevelCrossing_position + one step
                prev_place = signal_placement[node]["Prev"]
                prev_place = [round(crossing_positions[0]+step,1),round(crossing_positions[1],1)]

                # Upload both positions to the node
                #signal_placement[node] |= {"Next":next_place,"Prev":prev_place} 
                #print(f'{crossing_nodes[node]["Id"]} {"Next"} {next_place}')
                #print(f'{crossing_nodes[node]["Id"]} {"Prev"} {prev_place}')
                signal_placement[node]["Next"].append(next_place)
                signal_placement[node]["Prev"].append(prev_place)

        # If there is a curve:
        if nodes[node]["Lines"] > 1:
            all_points = nodes[node]["All"]
            curve_positions  = all_points[1:-1]
            print(f'  {node} has a Curve({nodes[node]["Lines"]} lines) @ {curve_positions}')

            # Find orientation of the curve
            orientation = []
            for point in range(len(all_points)-1):
                if all_points[point][1] == all_points[point+1][1]:
                    orientation.append("-")
                else:
                    orientation.append("/")

            if node not in signal_placement:
                signal_placement[node] = {"Next":[],"Prev":[]}

            #print(signal_placement)
            #print(signal_placement[node]["Next"],signal_placement[node]["Prev"])
            
            # next_position = curve_position(previous node, close to the curve) - one step
            next_place = signal_placement[node]["Next"]
            #print(f'next: {next_place}')
            for curve in range(len(curve_positions)):
                if orientation[curve + 1] == "/":                      
                    next_place.append([round(curve_positions[curve][0]-step/2,1),round(curve_positions[curve][1],1)])
            
            #print(f'next +: {next_place}')
            # prev_position = curve_position(next node, close to the curve) + one step
            prev_place = signal_placement[node]["Prev"]
            #print(f'prev: {prev_place}')
            for curve in range(len(curve_positions)):
                if orientation[curve] == "/":                        
                    prev_place.append([round(curve_positions[curve][0]+step/2,1),round(curve_positions[curve][1],1)])
            
            #print(f'prev +: {prev_place}')
            
            # Upload both positions to the node
            #print(f'{next_place} in {signal_placement[node]["Next"]}')
            #print(f'{prev_place} in {signal_placement[node]["Prev"]}')
            for i in next_place:
                if i not in signal_placement[node]["Next"]:
                    signal_placement[node]["Next"].append(i)
            for i in prev_place:
                if i not in signal_placement[node]["Prev"]:
                    signal_placement[node]["Prev"].append(i)
            #print(f'R:{next_place} in {signal_placement[node]["Next"]}')
            #print(f'R:{prev_place} in {signal_placement[node]["Prev"]}')

        # If there is no RailJoint, Platform, LevelCrossing or curve AND it is horizontal:
        if node not in signal_placement:
            if (nodes[node]["Begin"][1] == nodes[node]["End"][1]):
                
                if node not in signal_placement:
                    signal_placement[node] = {"Next":[],"Prev":[]}
                
                # Find middle points between switches

                begin = nodes[node]["Begin"][0]
                end = nodes[node]["End"][0]
                dist = abs(end - begin)

                cuts = dist // length

                #print(f'Cuts: {cuts} [{begin},{nodes[node]["Begin"][1]}] to [{end},{nodes[node]["Begin"][1]}] Length: {dist} Max_Length: {length}')
                if cuts > 1:
                    slice = dist / cuts
                    #print(f'slice {slice}')
                    #y = nodes[node]["End"][1]
                    #print(f'Cuts: {cuts} [{begin},{y}] to [{end},{y}] Length: {dist} Max_Length: {length}')

                    for x in range(cuts-1):
                        #print(x)
                        #print(f'{x} > [{begin+(x+1)*slice},{y}]')
                        x_middle_point = begin+(x+1)*slice
                        y_coordinate = nodes[node]["Begin"][1]
        
                        print(f'  {node} has a Middle point @ {[round(x_middle_point,1),y_coordinate]}')
                
                        # next_position
                        next_place = signal_placement[node]["Next"]
                        next_place = [round(x_middle_point,1),round(y_coordinate,1)]
                        
                        # prev_position
                        prev_place = signal_placement[node]["Prev"]
                        prev_place = [round(x_middle_point,1),round(y_coordinate,1)]
                
                        # Upload both positions to the node
                        #signal_placement[node] |= {"Next":next_place,"Prev":prev_place} 
                        
                        #print(f'{"Default"} {"Next"} {next_place}')
                        #print(f'{"Default"} {"Prev"} {prev_place}')
                        signal_placement[node]["Next"].append(next_place)
                        signal_placement[node]["Prev"].append(prev_place)
                else:
                    # Find middle point between switches
                    x_middle_point = (nodes[node]["Begin"][0] + nodes[node]["End"][0]) / 2
                    y_coordinate = nodes[node]["Begin"][1]
                    
                    print(f'  {node} has a Middle point @ {[round(x_middle_point,1),y_coordinate]}')
                    
                    # next_position
                    next_place = signal_placement[node]["Next"]
                    next_place = [round(x_middle_point,1),round(y_coordinate,1)]
                    
                    # prev_position
                    prev_place = signal_placement[node]["Prev"]
                    prev_place = [round(x_middle_point,1),round(y_coordinate,1)]
                    
                    # Upload both positions to the node
                    #signal_placement[node] |= {"Next":next_place,"Prev":prev_place} 
                    
                    #print(f'{"Default"} {"Next"} {next_place}')
                    #print(f'{"Default"} {"Prev"} {prev_place}')
                    signal_placement[node]["Next"].append(next_place)
                    signal_placement[node]["Prev"].append(prev_place)
  
    # Simplify closest signal placements
    try:
        signal_simplification_by_proximity(signal_placement,crossing_nodes,platforms_node,dist)
    except:
        print('Zonas criticas no simplificadas')

    # Deleting the signal placements with only no members
    for i in signal_placement:
        if signal_placement[i]["Prev"] == []:
            del signal_placement[i]["Prev"]
        if signal_placement[i]["Next"] == []:
            del signal_placement[i]["Next"]    
    
    return signal_placement

# Simplify closest signal placements
def signal_simplification_by_proximity(signal_placement,crossing_nodes,platforms_node,dist = 300):
    distance = dist
    #print(signal_placement)
    #print(crossing_nodes)
    #print(platforms_node)

    n_removed = []
    p_removed = []

    for node in signal_placement:
        old_next = signal_placement[node]["Next"]
        old_prev = signal_placement[node]["Prev"]
        n_p_next = old_next
        n_p_prev = old_prev

        #print(node,n_p_next,n_p_prev)
        for n in old_next:
            for p in old_prev:
                #print(node,old_next,old_prev)
                if old_next.index(n) == old_prev.index(p):
                    continue
                #print(n,p,abs(n[0]-p[0]),distance,abs(n[0]-p[0]) < distance)
                if abs(n[0]-p[0]) < distance and n[1] == p[1]:
                    #print(node,n,p)
                    if node in crossing_nodes and node in platforms_node:
                        crossing_pos = crossing_nodes[node][0]["Position"][0]
                        platform_pos = platforms_node[node][0]["Position"][0]
                    else:
                        continue
                    #print(node,crossing_pos,platform_pos,platform_pos-crossing_pos)
                    if (abs(platform_pos-crossing_pos) < distance):
                        if n in n_p_next and p in n_p_prev:
                            print(f'remove_a {n} {p}')
                            if n in n_p_next and n not in n_removed:
                                n_p_next.remove(n)
                                n_removed.append(n)
                            if p in n_p_prev and p not in p_removed:
                                n_p_prev.remove(p)
                                p_removed.append(p)
                         
                    if (platform_pos < n[0] < crossing_pos or crossing_pos < n[0] < platform_pos) and (platform_pos < p[0] < crossing_pos or crossing_pos < p[0] < platform_pos):
                        continue
                    else:
                        if n in n_p_prev and p in n_p_next:
                            print(f'remove_b {n} {p}')
                            n_p_next.remove(n)
                            n_p_prev.remove(p)

        #print(n_p_next)
        #print(n_p_prev)
    
        signal_placement[node]["Next"] = n_p_next
        signal_placement[node]["Prev"] = n_p_prev
    #print(signal_placement)
    return signal_placement

# Order que "All" attribute for nodes:
def order_nodes_points(nodes):
    
    for node in nodes: 
        
        if nodes[node]["All"][0] < nodes[node]["All"][-1]:
            nodes[node]["Way"] = ">>"
            nodes[node]["Inverter"] = False
        else:
            nodes[node]["Way"] = "<<"
            nodes[node]["Inverter"] = True
        #print(node,nodes[node]["All"][0],nodes[node]["All"][-1],nodes[node]["All"][0] < nodes[node]["All"][-1],nodes[node]["Way"],nodes[node]["Inverter"])

        #print(f'--- {node} {nodes[node]["All"]}')
        print(node,nodes[node]["All"][0],nodes[node]["All"][-1],nodes[node]["Way"])
        nodes[node]["All"] = sorted(nodes[node]["All"], key=lambda x: x[0])
        if nodes[node]["All"][0] != nodes[node]["Begin"]:
            nodes[node]["Begin"] = nodes[node]["All"][0]
            nodes[node]["End"] = nodes[node]["All"][-1]
    
    return nodes

def export_placement(file,nodes,signal_placement):

    #print(signal_placement)
    with open(file, "w") as f: 
        for sig in nodes:
            if sig in signal_placement:
                f.write(f'{str(sig).zfill(2)}:\n')
                if "Next" in signal_placement[sig]:
                    f.write(f'  Next: {signal_placement[sig]["Next"]}\n')
                if "Prev" in signal_placement[sig]:
                    f.write(f'  Prev: {signal_placement[sig]["Prev"]}\n')
        f.close()

def find_way(signals,nodes,config):

    for sig in signals:
        #print(sig,signals[sig]["From"],nodes[signals[sig]["From"]]["Way"],signals[sig]["AtTrack"])
        
        if signals[sig]["AtTrack"] == "left":
            #print(sig,nodes[signals[sig]["From"]]["Way"])
            way = nodes[signals[sig]["From"]]["Way"]
        else:
            way = "<<" if nodes[signals[sig]["From"]]["Way"] == ">>" else ">>"
            #print(sig,way)

        signals[sig]["Way"] = way

        #print(f'{sig} {signals[sig]["Way"]}')

def move_signals(signals,nodes,moving=True):
    if moving:
        move_step = 90
        for signal_a in reversed(signals):
            for signal_b in signals:
                if signal_a != signal_b and signals[signal_a]["Position"] == signals[signal_b]["Position"] and signals[signal_a]["Direction"] == signals[signal_b]["Direction"]:
                    #print(signal_a,signal_b)
                    #print(signals[signal_a])
                    step = move_step if signals[signal_a]["Direction"] == "normal" else -move_step
                    if ( nodes[signals[signal_a]["From"]]["Inverter"]):
                        step = move_step if step == - move_step else - move_step

                    signals[signal_b]["Position"] = [signals[signal_b]["Position"][0]-step,signals[signal_b]["Position"][1]]
    else:
        delete = []
        
        for signal_a in signals:
            if signal_a in delete:
                continue
            for signal_b in signals:
                if signal_a != signal_b:
                    if signals[signal_a]["Position"] == signals[signal_b]["Position"]:
                        if signal_b not in delete:
                            delete.append(signal_b)
                            #print(signal_a,signal_b)
        
        for delete_signal in delete:
            del signals[delete_signal]

def print_net(netElements):
    
    x = 0
    for i in netElements.NetElement:
        x += 1
        print(x,i)
        if x >= 59:
            #print(i.__dict__)
            print(i.Id)
    print("-------------------")
    x = 0
    for i in netElements.NetElement:
        x += 1
        if x >= 0:
            print(f'{x} : Id = "{i.Id}"')
            
            if i.Relation != None:
                for j in i.Relation:
                    print(f'\tRelation: Ref = "{j.Ref}"')
            if i.ElementCollectionUnordered != None:
                for j in i.ElementCollectionUnordered:
                    print(f'\tElementCollectionUnordered: Id = "{j.Id}"')
                    for k in j.ElementPart:
                        print(f'\t\tElementPart: Ref = "{k.Ref}"')
            #continue
            if i.AssociatedPositioningSystem != None:
                for j in i.AssociatedPositioningSystem:
                    print(f'\tAssociatedPositioningSystem: Id = "{j.Id}"')
                    for k in j.IntrinsicCoordinate:
                        print(f'\t\tIntrinsicCoordinate: Id = "{k.Id}" | intrinsicCoord = "{k.IntrinsicCoord}"')
                        if k.GeometricCoordinate != None:
                            for l in k.GeometricCoordinate:
                                print(f'\t\t\t GeometricCoordinate: PositioningSystemRef = "{l.PositioningSystemRef}" X = "{l.X}" Y = "{l.Y}"')

def arrow_simplification(signals,nodes,sequence):

    signals_by_node = {}
    
    #for node in nodes:
    #    print(node)
        
    for signal in signals:
        #print(signal,signals[signal])
        if signals[signal]['From'] not in signals_by_node:
            signals_by_node[signals[signal]['From']] = {}
        #print(f'{signal} {signals[signal]["Way"]}')
        if ('left' in signals[signal]['To'] or 'right' in signals[signal]['To']):
            #signals_by_node[signals[signal]['From']][signal] = '<' if 'left' in signals[signal]['To'] else '>'
            signals_by_node[signals[signal]['From']][signal] = '<' if '<' in signals[signal]['Way'] else '>'

    i = 0
    for node in nodes:
        #print(int(node[2:]))
        if node in signals_by_node:
            #print(node,signals_by_node[node])
            for signal in signals_by_node[node]:
                if sequence[i] not in signals_by_node[node][signal]:
                    #print(f'{signal} alive')
                #else:
                    if signals[signal]["Name"][0] != "S" and signals[signal]["Name"][0] != "B" and signals[signal]["Name"][0] != "C" and signals[signal]["Name"][0] != "H":
                        print(f'Single track {signals[signal]["Name"]}')
                        del signals[signal]
                    #print(f'{signal} dead')
        i = i+1
    #for signal in signals:
    #    print(signal,signals[signal])    

##%%%
def analyzing_object(object,sequence,switch_net,platform_net,levelCrossing_net,scissorCrossing_net,distanceParameters,old_table = {},example =1,config = [1,1,1,1,1,1,1,1,1,1]):
    topology = object.Infrastructure.Topology
    netElements = topology.NetElements
    netRelations = topology.NetRelations.NetRelation if topology.NetRelations != None else []  
    infrastructure = object.Infrastructure.FunctionalInfrastructure
    visualization = object.Infrastructure.InfrastructureVisualizations
    
    print(" Analyzing graph")
    #print_net(netElements)
    nodes,neighbours,switches,limits,netPaths = analyzing_graph(netElements,netRelations)

    print(" Analyzing infrastructure --> Infrastructure.RNA")
    borders,bufferStops,derailersIS,levelCrossingsIS,lines,operationalPoints,platforms,signalsIS,switchesIS,tracks,trainDetectionElements = analyzing_infrastructure(infrastructure,visualization,nodes)

    infrastructure_file = "App//Layouts//Example_"+str(example)+"//Infrastructure.RNA"
    export_analysis(infrastructure_file,nodes,neighbours,borders,bufferStops,derailersIS,levelCrossingsIS,lines,operationalPoints,platforms,signalsIS,switchesIS,tracks,trainDetectionElements)

    #for i in nodes:
    #    print(i,nodes[i])
    print(" Detecting Danger --> Safe_points.RNA")
    signal_placement = find_signal_positions(nodes,netPaths,switchesIS,tracks,trainDetectionElements,bufferStops,levelCrossingsIS,platforms,config[8],config[9])
    safe_point_file = "App//Layouts//Example_"+str(example)+"//Safe_points.RNA"
    export_placement(safe_point_file,nodes,signal_placement)

    #print(f' Signal (possible) places:{signal_placement}')
    print(" Creating Signalling --> Signalling.RNA")
    signals_file = "App//Layouts//Example_"+str(example)+"//Dangers.RNA"

    signals = find_signals(safe_point_file,signal_placement,nodes,netPaths,switchesIS,tracks,trainDetectionElements,borders,bufferStops,levelCrossingsIS,platforms,distanceParameters,config)
    
    find_way(signals,nodes,config)

    if (config[6]):
        # Apply arrow simplification
        print(" One direction only")
        arrow_simplification(signals,nodes,sequence)

    # Reduce redundant signals
    if (config[7]):
        print(" Reducing redundant signals")
        reduce_signals(signals,signal_placement)

    
    #find_way(signals,nodes,config)
    
    #for i in levelCrossing_net:
    #    print(i,levelCrossing_net[i])

    #move_signals(signals,nodes,True)
    
    export_signal("App//Layouts//Example_"+str(example)+"//Signalling.RNA",signals,object)
    
    print(" Detecting Routes --> Routes.RNA")
    route_file = "App//Layouts//Example_"+str(example)+"//Routes.RNA"
    routes = detect_routes(signals,netPaths,switch_net,platform_net,levelCrossing_net,scissorCrossing_net)
    new_table = export_routes(route_file,routes,object,example,switchesIS)
    
    for route in routes:
        print('R'+str(route),routes[route])
    
    print(f'RML object\'s size: {sizeof(object)} Bytes')

    i = 0
    for old in old_table:
        i = i + 1
        old_table[old] |= {'route':i}

    validate_tables(old_table,new_table)

    validate_signalling(nodes,signals,switch_net,bufferStops,levelCrossingsIS,platforms)

    return [f'Tracks : {len(nodes)} \n BufferStops : {len(bufferStops)} \n LineBorders : {len(borders)} \n Crossings : {len(levelCrossingsIS)} \n Platforms : {len(platforms)}',f'Signals created : {len(signals)}'],routes

def find_shortest_paths(old_route, graph, start_node, end_node, way):
    if ( start_node != end_node ):
        try:
            total = []
            paths = nx.all_shortest_paths(graph, start_node, end_node)
            
            for path in paths:
                edges = []
                if (len(path) == 1):
                    edges.append('R'+str(graph[path[0]][path[0]]['name'][2:]))
                for i in range(len(path) - 1):
                    edge = graph[path[i]][path[i+1]]
                    edges.append('R'+str(edge['name'][2:]))
                total.append("[ "+"+".join(edges)+" ]")
                #print(" + ".join(edges))
            print(old_route+" -> "+" OR ".join(total))
            return 1 
        except:
            try:
                if (start_node in graph):
                    #print(graph[start_node])
                    begin_nodes = list(graph.neighbors(start_node))
                    #print(begin_nodes)
                    #print('R'+str(graph[start_node][begin_nodes[0]]['name'][2:]))
                    if (begin_nodes != []):
                        print(old_route+" -> "+'[ R'+str(graph[start_node][begin_nodes[0]]['name'][2:])+' ]')
                        #routes_found += find_shortest_paths('r'+str(old_table[old]['route']),G_new, begin_nodes[0], old_table[old]['net_end'])
                        return 1
                    else:
                        return 0
                else:
                    #print(old_route + " -> FAIL "+end_node)
                    #begin_nodes = list(graph.neighbors(end_node))
                    #print(begin_nodes)
                    #print(graph[end_node])

                    aux1 = [graph[a][b] for a in graph for b in graph[a] if b == end_node]# and graph[a][b]['name'][:2] == way]
                    aux2 = [a for a in graph for b in graph[a] if b == end_node]# and graph[a][b]['name'][:2] == way]
                    #print(aux1,aux2)
                    #print(aux1[-1]['name'][2:])
                    if (aux1 != []):
                        print(old_route+" -> "+'[ R'+aux1[-1]['name'][2:]+' ]')
                        return 1
                    else:
                        return 0
            except:
                print(old_route + " -> BREAK")
                return 0
    else:
        print(old_route + " -> LOOP")
        return 0

def validate_tables(old_table,new_table):
    print('x'*50)

    # old graph definition
    G_old = nx.DiGraph()
    for old in old_table:
        #print(old_table[old]['route'],old_table[old]['way'],old_table[old]['net_start'],old_table[old]['net_end'])
        G_old.add_edge(old_table[old]['net_start'],old_table[old]['net_end'],name = old_table[old]['route'])
    #print(G_old)
    # new graph definition
    G_new = nx.DiGraph()
    for new in new_table:
        #print(new_table[new]['route'],new_table[new]['way'],new_table[new]['net_start'],new_table[new]['net_end'])
        if ( new_table[new]['net_start'] != new_table[new]['net_end'] ):
            G_new.add_edge(new_table[new]['net_start'],new_table[new]['net_end'],name = new_table[new]['way'] + str(new_table[new]['route']))
        else:
            G_new.add_edge(new_table[new]['net_start'] + new_table[new]['way'],new_table[new]['net_end']+ new_table[new]['way'],name = new_table[new]['route'])
    #print(G_new)
    routes_found = 0
    for old in old_table:
        if ( old_table[old]['net_start'] != old_table[old]['net_end'] ):
            routes_found += find_shortest_paths('r'+str(old_table[old]['route']),G_new, old_table[old]['net_start'], old_table[old]['net_end'],old_table[old]['way'])
        else:
            #routes_found += find_shortest_paths('r'+str(old_table[old]['route']),G_new, old_table[old]['way'], old_table[old]['net_end'])
            #print('r'+str(old_table[old]['route']), old_table[old]['net_start'],G_new[old_table[old]['net_start'] + old_table[old]['way']])
            if ( old_table[old]['net_start']+old_table[old]['way'] in G_new ):
                keys = [x for x in G_new[old_table[old]['net_start'] + old_table[old]['way']]]
                #print(keys, old_table[old]['net_start']+old_table[old]['way'] in keys)
                print ( 'r'+str(old_table[old]['route'])+' -> [ R' + str(G_new[old_table[old]['net_start']+old_table[old]['way']][old_table[old]['net_start']+old_table[old]['way']]['name']) +' ]')
                routes_found += 1
            else:
                if ( old_table[old]['net_end'] in G_new):
                    #print('XXX','r'+str(old_table[old]['route']),old_table[old]['net_start'],old_table[old]['net_end'])
                    begin_nodes = list(G_new.neighbors(old_table[old]['net_end']))
                    #print(begin_nodes)
                    if (begin_nodes != []):
                        routes_found += find_shortest_paths('r'+str(old_table[old]['route']),G_new, begin_nodes[0], old_table[old]['net_end'],old_table[old]['way'])
                        #print ( 'r'+str(old_table[old]['route'])+' -> [ R' + str(G_new[old_table[old]['net_start']][keys[0]]['name']) +' ]')
                        #routes_found += 1
    print('x'*50)
    if len(old_table) > 0:            
        print(f'New interlocking table covers {100* routes_found/len(old_table):.0f}% of Routes')
    else:
        print(f'New interlocking table covers {len(new_table)} Routes')

def validate_signalling(nodes,signals,switch_net,bufferStops,levelCrossingsIS,platforms):

    print('x'*50)
    signals_in_node = find_semaphores_in_node(signals)

    switch_start_unprotected = []
    switch_normal_unprotected = []
    switch_branch_unprotected = []

    for switch in switch_net:
        if switch_net[switch]['type'] == 'simple':
            switch_start_unprotected.append(switch_net[switch]['main'])
            switch_normal_unprotected.append(switch_net[switch]['normal'])
            switch_branch_unprotected.append(switch_net[switch]['reverse'])

    switch_start_unprotected = list(set(switch_start_unprotected))
    switch_normal_unprotected = list(set(switch_normal_unprotected))
    switch_branch_unprotected = list(set(switch_branch_unprotected))

    switch_start_unprotected_only = [i for i in switch_start_unprotected if i not in switch_branch_unprotected]
    switch_normal_unprotected_only = [i for i in switch_normal_unprotected if i not in switch_branch_unprotected]
    
    print(switch_start_unprotected,switch_normal_unprotected,switch_branch_unprotected,switch_start_unprotected_only,switch_normal_unprotected_only)
     
    for node in signals_in_node:
        if node in switch_start_unprotected_only:
            switch_start_unprotected_only.remove(node)
        if node in switch_normal_unprotected_only:
            switch_normal_unprotected_only.remove(node)

    print(switch_start_unprotected_only,switch_normal_unprotected_only)
    
    stops = 0
    for signal in signals:
        if 'T' in signals[signal]['Name']:
            stops += 1

    sem_positions =  [signals[x]['Position'] for x in signals]
    crossing_positions = [levelCrossingsIS[x]['Position'] for x in levelCrossingsIS]
    platform_positions = [platforms[x]['Position'] for x in platforms]

    #print(sem_positions)
    #print(crossing_positions)

    crossings_protected = 0
    for xros in crossing_positions:
        for sem in sem_positions:
            if (abs(sem[1]) == abs(xros[1])):
                if (abs(sem[0]-xros[0]) < 500):
                    crossings_protected += 1
                    break  

    #print(crossings_protected)

    #print(platform_positions)
    platforms_protected = 0
    for plat in platform_positions:
        for sem in sem_positions:
            if (abs(sem[1]) == abs(plat[1])):
                if (abs(sem[0]-plat[0]) < 700):
                    platforms_protected += 1
                    break  
                  
    #print(platforms_protected)

    if ( len(bufferStops) > stops ):
        print(f'Stops unprotected -> Railway principles failed')
        print('x'*50)
        return

    if ( len(levelCrossingsIS) > crossings_protected ):
        print(f'Level crossings unprotected -> Railway principles failed')
        print('x'*50)
        return
    
    if ( len(platforms) > platforms_protected ):
        print(f'Platforms unprotected -> Railway principles failed')
        print('x'*50)
        return
    
    if ( switch_start_unprotected_only != [] or switch_normal_unprotected_only != [] ):
        print(f'Switches unprotected -> Railway principles failed')
        print('x'*50)
        return
    
    print(f'Railway elements fully protected -> Railway principles accepted')      

    print('x'*50)