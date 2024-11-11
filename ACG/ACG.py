import sys
sys.path.append('.')

import numpy as np
import math
import networkx as nx
import graphviz as gv

class ACG():
	def create_graph_structure(self,RML,example = 1):

		NetElements =       RML.Infrastructure.Topology.NetElements
		NetRelations =		RML.Infrastructure.Topology.NetRelations
		SwitchesIS =        RML.Infrastructure.FunctionalInfrastructure.SwitchesIS
		LevelCrossingsIS =  RML.Infrastructure.FunctionalInfrastructure.LevelCrossingsIS
		Platforms =         RML.Infrastructure.FunctionalInfrastructure.Platforms
		Borders =           RML.Infrastructure.FunctionalInfrastructure.Borders
		BufferStops =       RML.Infrastructure.FunctionalInfrastructure.BufferStops
		Crossings =         RML.Infrastructure.FunctionalInfrastructure.Crossings
		SignalsIS =         RML.Infrastructure.FunctionalInfrastructure.SignalsIS

		network = {}

		for netElements in NetElements.NetElement:
			if netElements.ElementCollectionUnordered == None:
				network[netElements.Id] = {}

		for netRelations in NetRelations.NetRelation:
			if netRelations.Navigability != 'None' and netRelations.PositionOnA != None:
				aux = netRelations.Id.split('_')[1].split('ne')
				#print(aux)
				#if len(aux) > 3:
				nodeBegin = 'ne'+aux[1]
				nodeEnd = 'ne'+aux[2]
				#print(nodeBegin,nodeEnd)
				if 'Neighbour' not in network[nodeBegin]:	
					network[nodeBegin] |= {'Neighbour':[]}
				if 'Neighbour' not in network[nodeEnd]:	
					network[nodeEnd] |= {'Neighbour':[]}

				network[nodeBegin]['Neighbour'].append(nodeEnd)
				network[nodeEnd]['Neighbour'].append(nodeBegin)

		if SwitchesIS != None: 
			for SwitchIS in SwitchesIS[0].SwitchIS:
				if (SwitchIS.Type == "ordinarySwitch"):

					main = SwitchIS.SpotLocation[0].NetElementRef
					left = SwitchIS.LeftBranch[0].NetRelationRef.split('_')[1].replace(main,'')
					left_radius = SwitchIS.LeftBranch[0].Radius
					right = SwitchIS.RightBranch[0].NetRelationRef.split('_')[1].replace(main,'')

					nodeStart = main
					nodeContinue = left if left_radius == "0" else right
					nodeBranch = right if left_radius == "0"  else left

					if 'Switch' not in network[nodeStart]:
						network[nodeStart] |= {'Switch':[]}
					if 'Switch_C' not in network[nodeContinue]:
						network[nodeContinue] |= {'Switch_C':[]}
					if 'Switch_B' not in network[nodeBranch]:
						network[nodeBranch] |= {'Switch_B':[]}

					network[nodeStart]['Switch'].append(SwitchIS.Name[0].Name)
					network[nodeContinue]['Switch_C'].append(SwitchIS.Name[0].Name)    
					network[nodeBranch]['Switch_B'].append(SwitchIS.Name[0].Name)      
				
				if (SwitchIS.Type == "doubleSwitchCrossing"):
					node = SwitchIS.SpotLocation[0].NetElementRef

					straightBranch_A = SwitchIS.StraightBranch[0].NetRelationRef#.split('_')[1]
					straightBranch_B = SwitchIS.StraightBranch[1].NetRelationRef#.split('_')[1]
					turningBranch_A = SwitchIS.TurningBranch[0].NetRelationRef#.split('_')[1]
					turningBranch_B = SwitchIS.TurningBranch[1].NetRelationRef#.split('_')[1]

					straightBranch_1 = straightBranch_A if node in straightBranch_A else straightBranch_B
					turningBranch_1 = turningBranch_A if node in turningBranch_A else turningBranch_B
					straightBranch_2 = straightBranch_B if node in straightBranch_A else straightBranch_B
					turningBranch_2 = turningBranch_B if node in turningBranch_A else turningBranch_B

					nodeStart = node
					nodeInt = straightBranch_1.split('_')[1].split('ne')[1:]
					nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

					#print(f'S:{nodeStart} {nodeEnd}')
						
					if 'Switch_X' not in network[nodeStart]:
						network[nodeStart] |= {'Switch_X':[]}
					if 'Switch_X' not in network[nodeEnd]:
						network[nodeEnd] |= {'Switch_X':[]}
					if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
						network[nodeStart]['Switch_X'].append(SwitchIS.Name[0].Name)
					if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
						network[nodeEnd]['Switch_X'].append(SwitchIS.Name[0].Name)

					nodeStart = node
					nodeInt = turningBranch_1.split('_')[1].split('ne')[1:]
					nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

					#print(f'T:{nodeStart} {nodeEnd}')
						
					if 'Switch_X' not in network[nodeStart]:
						network[nodeStart] |= {'Switch_X':[]}
					if 'Switch_X' not in network[nodeEnd]:
						network[nodeEnd] |= {'Switch_X':[]}
					if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
						network[nodeStart]['Switch_X'].append(SwitchIS.Name[0].Name)
					if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
						network[nodeEnd]['Switch_X'].append(SwitchIS.Name[0].Name)

					nodeStart = ['ne'+x for x in straightBranch_2.split('_')[1].split('ne')[1:] if x in turningBranch_2.split('_')[1].split('ne')[1:]][0]
					nodeInt = straightBranch_2.split('_')[1].split('ne')[1:]
					nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

					#print(f'S:{nodeStart} {nodeEnd}')
						
					if 'Switch_X' not in network[nodeStart]:
						network[nodeStart] |= {'Switch_X':[]}
					if 'Switch_X' not in network[nodeEnd]:
						network[nodeEnd] |= {'Switch_X':[]}
					if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
						network[nodeStart]['Switch_X'].append(SwitchIS.Name[0].Name)
					if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
						network[nodeEnd]['Switch_X'].append(SwitchIS.Name[0].Name)

					nodeStart = ['ne'+x for x in straightBranch_2.split('_')[1].split('ne')[1:] if x in turningBranch_2.split('_')[1].split('ne')[1:]][0]
					nodeInt = turningBranch_2.split('_')[1].split('ne')[1:]
					nodeEnd = 'ne'+nodeInt[0] if str(nodeStart[2:]) == nodeInt[1] else 'ne'+nodeInt[1]

					#print(f'T:{nodeStart} {nodeEnd}')
						
					if 'Switch_X' not in network[nodeStart]:
						network[nodeStart] |= {'Switch_X':[]}
					if 'Switch_X' not in network[nodeEnd]:
						network[nodeEnd] |= {'Switch_X':[]}
					if SwitchIS.Name[0].Name not in network[nodeStart]['Switch_X']:
						network[nodeStart]['Switch_X'].append(SwitchIS.Name[0].Name)
					if SwitchIS.Name[0].Name not in network[nodeEnd]['Switch_X']:
						network[nodeEnd]['Switch_X'].append(SwitchIS.Name[0].Name)
		
		if LevelCrossingsIS != None:  
			for LevelCrossingIS in LevelCrossingsIS[0].LevelCrossingIS:
				#print(LevelCrossingIS.SpotLocation[0].NetElementRef,LevelCrossingIS.Name[0].Name)
				node = LevelCrossingIS.SpotLocation[0].NetElementRef
				levelCrossing = LevelCrossingIS.Name[0].Name

				if 'LevelCrossing' not in network[node]:
					network[node] |= {'LevelCrossing':[]}
				if levelCrossing not in network[node]['LevelCrossing']:
					network[node]['LevelCrossing'].append(levelCrossing)

		if Platforms != None:
			for Platform in Platforms[0].Platform:
				node = Platform.LinearLocation[0].AssociatedNetElement[0].NetElementRef
				platform = Platform.Name[0].Name

				if 'Platform' not in network[node]:
					network[node] |= {'Platform':[]}
				if platform not in network[node]['Platform']:
					network[node]['Platform'].append(platform)

		if Borders != None:
			for Border in Borders[0].Border:
				node = Border.SpotLocation[0].NetElementRef
				border = Border.Name[0].Name

				if 'Border' not in network[node]:
					network[node] |= {'Border':[]}
				if border not in network[node]['Border']:
					network[node]['Border'].append(border)

		if BufferStops != None:
			for BufferStop in BufferStops[0].BufferStop:
				node = BufferStop.SpotLocation[0].NetElementRef
				bufferStop = BufferStop.Name[0].Name

				if 'BufferStop' not in network[node]:
					network[node] |= {'BufferStop':[]}
				if bufferStop not in network[node]['BufferStop']:
					network[node]['BufferStop'].append(bufferStop)

		if Crossings != None:
			for Crossing in Crossings[0].Crossing:
				crossing = Crossing.Name[0].Name

				Net = Crossing.External[0].Ref.split('_')[1].split('ne')
				node1 = 'ne' + Net[1]        
				node2 = 'ne' + Net[2]  

				Net = Crossing.External[1].Ref.split('_')[1].split('ne')
				node3 = 'ne' + Net[1]        
				node4 = 'ne' + Net[2]  

				if 'Crossing' not in network[node1]:
					network[node1] |= {'Crossing':[]}
				if 'Crossing' not in network[node2]:
					network[node2] |= {'Crossing':[]}
				if 'Crossing' not in network[node3]:
					network[node3] |= {'Crossing':[]}
				if 'Crossing' not in network[node4]:
					network[node4] |= {'Crossing':[]}

				if crossing not in network[node1]['Crossing']:
					network[node1]['Crossing'].append(crossing)
				if crossing not in network[node2]['Crossing']:
					network[node2]['Crossing'].append(crossing)
				if crossing not in network[node3]['Crossing']:
					network[node3]['Crossing'].append(crossing)
				if crossing not in network[node4]['Crossing']:
					network[node4]['Crossing'].append(crossing)

		if SignalsIS != None:
			for SignalIS in SignalsIS.SignalIS:
				node = SignalIS.SpotLocation[0].NetElementRef
				signal = SignalIS.Name[0].Name

				if 'Signal' not in network[node]:
					network[node] |= {'Signal':[]}
				if signal not in network[node]['Signal']:
					network[node]['Signal'].append(signal)
		
		return network

	def print_network(self,network):
		for element in network:
			print(f'{element} {network[element]}\t')

	def create_graph(self,RML,network,example = 1):

		NetRelations =      RML.Infrastructure.Topology.NetRelations
		SignalsIS =         RML.Infrastructure.FunctionalInfrastructure.SignalsIS
		Routes =            RML.Interlocking.AssetsForIL[0].Routes

		#Graph = gv.Graph('finite_state_machine',filename='a.gv', graph_attr={'overlap':'false','rankdir':"LR",'splines':'true','center':'1','labelloc':'t'},node_attr={'fillcolor': 'white', 'style': 'filled,bold', 'pendwidth':'5', 'fontname': 'Courier New', 'shape': 'Mrecord'}) #node_attr={'color': 'lightgreen', 'style': 'filled', 'size' : '8.5'}
		
		Graph = gv.Graph('finite_state_machine',filename='a.gv', graph_attr={'overlap':'scale','newrank':"true",'splines':'true','center':'1','labelloc':'t','ratio':'compress','size':'300,300!'},node_attr={'fillcolor': 'white', 'style': 'filled,bold', 'pendwidth':'5', 'fontname': 'Courier New', 'shape': 'Mrecord'}) #node_attr={'color': 'lightgreen', 'style': 'filled', 'size' : '8.5'}

		G_Topology = nx.Graph()

		Signal_net = {}
		Signal_labels = {}
		for SignalIS in SignalsIS.SignalIS:
			Signal_net[SignalIS.Id] = {'net':SignalIS.SpotLocation[0].NetElementRef, 'equivalent':SignalIS.Designator[0].Entry[7:]}

		for NetRelation in NetRelations.NetRelation:
			if (NetRelation.Navigability != "None" and any(i.isdigit() for i in NetRelation.ElementA.Ref)): #ONLY NAVIGABILITY
				#print(f'{NetRelation.ElementA.Ref} -> {NetRelation.ElementB.Ref}')
				#Graph.edge(NetRelation.ElementA.Ref,NetRelation.ElementB.Ref)
				G_Topology.add_edge(NetRelation.ElementA.Ref,NetRelation.ElementB.Ref)

		i = 1
		for Route in Routes.Route:
			entry_signal = Route.RouteEntry.RefersTo.Ref.split('_')[1]
			exit_signal = Route.RouteExit.RefersTo.Ref.split('_')[1]

			entry_net = Signal_net[entry_signal]['net']
			exit_net = Signal_net[exit_signal]['net']
			
			equivalent_entry_signal = Signal_net[entry_signal]['equivalent']
			equivalent_exit_signal = Signal_net[exit_signal]['equivalent']

			path = nx.shortest_path(G_Topology, source=entry_net, target=exit_net) 
			
			if len(path) == 1:
				Graph.edge(entry_net,exit_net,label = f'R_{i:02d}')
			else:
				for p in range(len(path)-1):
					Graph.edge(path[p],path[p+1],label = f'R_{i:02d}')

			#print(f'R_{i:02d} | {entry_net} --> ({equivalent_entry_signal}) --> {path} --> ({equivalent_exit_signal}) --> {exit_net}')

			i = i + 1

		routed = []
		for i in Graph.body:
			if "--" in i:
				x = i[1:-1].split(" ")
				routed.append([x[0],x[2]])

		#print(routed)

		for NetRelation in NetRelations.NetRelation:
			if (NetRelation.Navigability != "None" and any(i.isdigit() for i in NetRelation.ElementA.Ref)): #ONLY NAVIGABILITY
				if not ( [NetRelation.ElementA.Ref,NetRelation.ElementB.Ref] in routed or [NetRelation.ElementB.Ref,NetRelation.ElementA.Ref] in routed):
					Graph.edge(NetRelation.ElementA.Ref,NetRelation.ElementB.Ref)
				
		for element in network:
			data = f'<<table border=\"0\" cellborder=\"0\" cellpadding=\"3\" bgcolor=\"white\"><tr><td bgcolor=\"black\" align=\"center\" colspan=\"2\"><font color=\"white\">{element}</font></td></tr>'

			if 'Switch' in network[element]:
				data += f'<tr><td bgcolor="red" align="right">Switch</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['Switch'])}</td></tr>'

			if 'Switch_X' in network[element]:
				data += f'<tr><td bgcolor="darkred" align="right">Double Switch</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['Switch_X'])}</td></tr>'

			if 'Border' in network[element]:
				data += f'<tr><td bgcolor="lightslateblue" align="right">Border</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['Border'])}</td></tr>'

			if 'BufferStop' in network[element]:
				data += f'<tr><td bgcolor="olive" align="right">BufferStop</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['BufferStop'])}</td></tr>'

			if 'LevelCrossing' in network[element]:
				data += f'<tr><td bgcolor="darkcyan" align="right">LevelCrossing</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['LevelCrossing'])}</td></tr>'

			if 'Platform' in network[element]:
				data += f'<tr><td bgcolor="cornflowerblue" align="right">Platform</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['Platform'])}</td></tr>'

			if 'Crossing' in network[element]:
				data += f'<tr><td bgcolor="pink" align="right">Crossing</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['Crossing'])}</td></tr>'

			if 'Signal' in network[element]:
				data += f'<tr><td bgcolor="yellowgreen" align="right">Signal</td>'
				data += f'<td align="left" port="r2">{' '.join(network[element]['Signal'])}</td></tr>'

			data += '</table>>'

			Graph.node(element,label = data)

		graph_file = "App//Layouts//Example_"+str(example)+"//Graph"

		Graph.render(graph_file,format='svg', view = True)

	def calculate_parameters(self,network,example = 1):

		# TODO FIX COUNTER! SWITCHES ARE UNDERCOUNTED AND DOUBLE ARE OVERCOUNTED!

		singleSwitches = []
		doubleSwitches = []
		scissorCrossings = []
		platforms = []
		levelCrossings = []

		n_netElements = len(network)
		n_switches = 0
		n_doubleSwitch = 0
		n_borders = 0
		n_buffers = 0
		n_levelCrossings = 0
		n_platforms = 0
		n_scissorCrossings = 0
		n_signals_1 = 0
		n_signals_2 = 0
		n_signals_3 = 0
		n_signals_S = 0
		n_signals_C = 0
		n_signals_B = 0
		n_signals_L = 0
		n_signals_T = 0
		n_signals_X = 0
		n_signals_P = 0
		n_signals_J = 0
		n_signals_H = 0

		for element in network:
			if "Switch" in network[element]:
				for singleSwitch in network[element]['Switch']:
					if singleSwitch not in singleSwitches:
						singleSwitches.append(singleSwitch)

			if 'Switch_X' in network[element]:
				for doubleSwitch in network[element]['Switch_X']:
					if doubleSwitch not in doubleSwitches:
						doubleSwitches.append(doubleSwitch)
				
			if 'Border' in network[element]:
				n_borders = n_borders + 1

			if 'BufferStop' in network[element]:
				n_buffers = n_buffers + 1

			if 'LevelCrossing' in network[element]:
				for levelCrossing in network[element]['LevelCrossing']:
					if levelCrossing not in levelCrossings:
						levelCrossings.append(levelCrossing)
	
			if 'Platform' in network[element]:
				for platform in network[element]['Platform']:
					if platform not in platforms:
						platforms.append(platform)

			if 'Crossing' in network[element]:
				for scissorCrossing in network[element]['Crossing']:
					if scissorCrossing not in scissorCrossings:
						scissorCrossings.append(scissorCrossing)

			if 'Signal' in network[element]:
				for signal in network[element]['Signal']:
					if 'S' in signal:
						n_signals_S = n_signals_S + 1
					if 'C' in signal:
						n_signals_C = n_signals_C + 1
					if 'B' in signal:
						n_signals_B = n_signals_B + 1
					if 'L' in signal:
						n_signals_L = n_signals_L + 1
					if 'T' in signal:
						n_signals_T = n_signals_T + 1
					if 'X' in signal:
						n_signals_X = n_signals_X + 1
					if 'P' in signal:
						n_signals_P = n_signals_P + 1
					if 'J' in signal:
						n_signals_J = n_signals_J + 1
					if 'H' in signal:
						n_signals_H = n_signals_H + 1

		n_switches = len(singleSwitches)
		n_doubleSwitch = len(doubleSwitches)
		n_scissorCrossings = len(scissorCrossings)
		n_platforms = len(platforms)
		n_levelCrossings = len(levelCrossings)
			
		n_signals_1 = 0
		n_signals_2 = n_signals_T + n_signals_B + n_signals_P
		n_signals_3 = n_signals_S + n_signals_C + n_signals_L + n_signals_X + n_signals_J + n_signals_H

		N = n_netElements + n_switches + n_doubleSwitch + n_scissorCrossings + n_levelCrossings + n_signals_2 + n_signals_3
		M = N - n_netElements

		print(f'n_netElements:{n_netElements}\nn_switch:{n_switches}\nn_doubleSwitch:{n_doubleSwitch}\nn_borders:{n_borders}\nn_buffers:{n_buffers}\nn_levelCrossings:{n_levelCrossings}\nn_platforms:{n_platforms}\nn_scissorCrossings:{n_scissorCrossings}\nn_signals:{n_signals_1+n_signals_2+n_signals_3}')


		return N,M,n_netElements,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,n_signals_1,n_signals_2,n_signals_3

	def createPacket(self,N,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,n_signals,example = 1):
		node = 'my_package'
				
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
		
		# Include body
		packet = 'my_package'
		f.write(f'\tpackage {packet} is\n')

		f.write(f'\t\ttype hex_char is (\'0\', \'1\', \'2\', \'3\', \'4\', \'5\', \'6\', \'7\', \'8\', \'9\', \'A\', \'B\', \'C\', \'D\', \'E\', \'F\');\r\n')
		f.write(f'\t\ttype hex_array is array (natural range <>) of hex_char;\r\n')

		f.write(f'\t\ttype ascii_array is array (0 to 255) of hex_char;\r\n')
		f.write(f'\t\ttype ascii_packet is array (hex_char range <>) of std_logic_vector(8-1 downto 0);\r\n')

		f.write(f'\t\t--LL|S\r\n')
		f.write(f'\t\ttype nodeStates is (OCCUPIED,FREE);\r\n')

		f.write(f'\t\ttype routeCommands is (RELEASE,RESERVE,LOCK);\r\n')
		f.write(f'\t\ttype objectLock is (RELEASED,RESERVED,LOCKED);\r\n')

		f.write(f'\t\ttype routeStates is (WAITING_COMMAND,ROUTE_REQUEST,RESERVING_TRACKS,LOCKING_TRACKS,RESERVING_INFRASTRUCTURE,LOCKING_INFRASTRUCTURE,DRIVING_SIGNAL,SEQUENTIAL_RELEASE,RELEASING_INFRASTRUCTURE,CANCEL_ROUTE);\r\n')

		f.write(f'\t\tfunction hex_to_slv(h: hex_char) return std_logic_vector;\n')
		f.write(f'\t\tfunction slv_to_hex(s: std_logic_vector) return hex_char;\n')
		
		if n_switches > 0:
			f.write(f'\t\ttype singleSwitchStates is (NORMAL,REVERSE,TRANSITION);\r\n')	

			type = 'sSwitch_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic;\n')
			f.write(f'\t\t\tlsb : std_logic;\n')
			f.write(f'\t\tend record {type};\n')
		
		if n_switches > 1:
			type = 'sSwitches_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic_vector({n_switches}-1 downto 0);\n')
			f.write(f'\t\t\tlsb : std_logic_vector({n_switches}-1 downto 0);\n')
			f.write(f'\t\tend record {type};\n')

		if n_doubleSwitch > 0:	
			f.write(f'\t\ttype doubleSwitchStates is (DOUBLE_NORMAL,DOUBLE_REVERSE,REVERSE_NORMAL,NORMAL_REVERSE,TRANSITION);\r\n')	

			type = 'dSwitch_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic;\n')
			f.write(f'\t\t\tlsb : std_logic;\n')
			f.write(f'\t\tend record {type};\n')
		
		if n_doubleSwitch > 1:
			type = 'dSwitches_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic_vector({n_doubleSwitch}-1 downto 0);\n')
			f.write(f'\t\t\tlsb : std_logic_vector({n_doubleSwitch}-1 downto 0);\n')
			f.write(f'\t\tend record {type};\n')

		if n_scissorCrossings > 0:	
			f.write(f'\t\ttype scissorCrossingStates is (NORMAL,REVERSE,TRANSITION);\r\n')	

			type = 'scissorCrossing_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic;\n')
			f.write(f'\t\t\tlsb : std_logic;\n')
			f.write(f'\t\tend record {type};\n')
		
		if n_scissorCrossings > 1:
			type = 'scissorCrossings_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic_vector({n_scissorCrossings}-1 downto 0);\n')
			f.write(f'\t\t\tlsb : std_logic_vector({n_scissorCrossings}-1 downto 0);\n')
			f.write(f'\t\tend record {type};\n')

		if n_levelCrossings >0:
			f.write(f'\t\ttype levelCrossingStates is (DOWN,UP,TRANSITION);\r\n')

			type = 'levelCrossing_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic;\n')
			f.write(f'\t\t\tlsb : std_logic;\n')
			f.write(f'\t\tend record {type};\n')
				
		if n_levelCrossings > 1:
			type = 'levelCrossings_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic_vector({n_levelCrossings}-1 downto 0);\n')
			f.write(f'\t\t\tlsb : std_logic_vector({n_levelCrossings}-1 downto 0);\n')
			f.write(f'\t\tend record {type};\n')
		
		if n_signals > 0:
			f.write(f'\t\ttype signalStates is (RED,DOUBLE_YELLOW,YELLOW,GREEN);\r\n')

			type = 'signal_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic;\n')
			f.write(f'\t\t\tlsb : std_logic;\n')
			f.write(f'\t\tend record {type};\n')
				
		if n_signals > 1:
			type = 'signals_type'
			f.write(f'\t\ttype {type} is record\n')
			f.write(f'\t\t\tmsb : std_logic_vector({n_signals}-1 downto 0);\n')
			f.write(f'\t\t\tlsb : std_logic_vector({n_signals}-1 downto 0);\n')
			f.write(f'\t\tend record {type};\n')

		#f.write(f'\t\ttype int_array is array(0 to {n_signals}-1) of integer;\r\n')
		
		f.write(f'\tend {packet};')
		f.write(f'\tpackage body my_package is\n')

		f.write(f'\t-- Conversion functions\n')
		f.write(f'\tfunction hex_to_slv(h: hex_char) return std_logic_vector is\n')
		f.write(f'\tbegin\n')
		f.write(f'\tcase h is\n')
		f.write(f'\t\twhen \'0\' => return "0000";\n')
		f.write(f'\t\twhen \'1\' => return "0001";\n')
		f.write(f'\t\twhen \'2\' => return "0010";\n')
		f.write(f'\t\twhen \'3\' => return "0011";\n')
		f.write(f'\t\twhen \'4\' => return "0100";\n')
		f.write(f'\t\twhen \'5\' => return "0101";\n')
		f.write(f'\t\twhen \'6\' => return "0110";\n')
		f.write(f'\t\twhen \'7\' => return "0111";\n')
		f.write(f'\t\twhen \'8\' => return "1000";\n')
		f.write(f'\t\twhen \'9\' => return "1001";\n')
		f.write(f'\t\twhen \'A\' => return "1010";\n')
		f.write(f'\t\twhen \'B\' => return "1011";\n')
		f.write(f'\t\twhen \'C\' => return "1100";\n')
		f.write(f'\t\twhen \'D\' => return "1101";\n')
		f.write(f'\t\twhen \'E\' => return "1110";\n')
		f.write(f'\t\twhen \'F\' => return "1111";\n')
		f.write(f'\t\twhen others => return "0000";  -- Default case\n')
		f.write(f'\tend case;\n')
		f.write(f'\tend function hex_to_slv;\n')

		f.write(f'\tfunction slv_to_hex(s: std_logic_vector) return hex_char is\n')
		f.write(f'\tbegin\n')
		f.write(f'\tcase s is\n')
		f.write(f'\t\twhen "0000" => return \'0\';\n')
		f.write(f'\t\twhen "0001" => return \'1\';\n')
		f.write(f'\t\twhen "0010" => return \'2\';\n')
		f.write(f'\t\twhen "0011" => return \'3\';\n')
		f.write(f'\t\twhen "0100" => return \'4\';\n')
		f.write(f'\t\twhen "0101" => return \'5\';\n')
		f.write(f'\t\twhen "0110" => return \'6\';\n')
		f.write(f'\t\twhen "0111" => return \'7\';\n')
		f.write(f'\t\twhen "1000" => return \'8\';\n')
		f.write(f'\t\twhen "1001" => return \'9\';\n')
		f.write(f'\t\twhen "1010" => return \'A\';\n')
		f.write(f'\t\twhen "1011" => return \'B\';\n')
		f.write(f'\t\twhen "1100" => return \'C\';\n')
		f.write(f'\t\twhen "1101" => return \'D\';\n')
		f.write(f'\t\twhen "1110" => return \'E\';\n')
		f.write(f'\t\twhen "1111" => return \'F\';\n')
		f.write(f'\t\twhen others => return \'0\';  -- Default case\n')
		f.write(f'\tend case;\n')
		f.write(f'\tend function slv_to_hex;\n')
		f.write(f'end package body my_package;\n')

		# Close file
		f.close()
		
	def initialComment(self,node,f):
		f.write(f'--  {node}.vhdl : Automatically generated using ACG\r\n')
		
	def includeLibrary(self,f,packet = False):
		f.write(f'library IEEE;\n')
		f.write(f'use IEEE.std_logic_1164.all;\n')
		f.write(f'use IEEE.numeric_std.all;\r\n')
		f.write(f'library work;\n')
		if (packet):
			f.write(f'--Declare the package\r\n')
			f.write(f'use work.my_package.all;\r\n')
			
	def createGlobal(self,N,M,example = 1):
			
		node = 'global'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# system entity
		wrapper = 'global'
		f.write(f'\tentity {wrapper} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tuart_rxd_i : in std_logic;\n')
		f.write(f'\t\t\tuart_txd_o : out std_logic;\n')
		f.write(f'\t\t\tleds : out std_logic_vector(4-1 downto 0);\n')
		f.write(f'\t\t\trgb_1 : out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\trgb_2 : out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tselector1 : in std_logic;\n')
		f.write(f'\t\t\tselector2 : in std_logic;\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {wrapper};\r\n') 
	
		f.write(f'architecture Behavioral of {wrapper} is\r\n')            

		# uartControl component
		uartControl = 'uartControl'
		f.write(f'\tcomponent {uartControl} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tN : out integer;\n')
		f.write(f'\t\t\twrite : in std_logic;\n')
		f.write(f'\t\t\tempty_in : in std_logic;\n') 
		f.write(f'\t\t\trd_uart : out std_logic;\n')
		f.write(f'\t\t\twr_uart : out std_logic;\n')  
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {uartControl};\r\n')
		
		# system component 
		system = "system"
		f.write(f'\tcomponent {system} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		
		f.write(f'\t\t\treset_uart : out std_logic;\n')
		f.write(f'\t\t\tr_available : in std_logic;\n')
		#f.write(f'\t\t\tread : out std_logic;\n')
		f.write(f'\t\t\twrite : out std_logic;\n')
		f.write(f'\t\t\tr_data : in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tselector1 : in std_logic;\n')
		f.write(f'\t\t\tselector2 : in std_logic;\n')
		f.write(f'\t\t\tN : in integer;\n')
		f.write(f'\t\t\tleds : out std_logic_vector(4-1 downto 0);\n')
		f.write(f'\t\t\tled_rgb_1 : out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tled_rgb_2 : out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tw_data : out std_logic_vector(8-1 downto 0);\n')
	
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {system};\r\n')
		
		f.write(f'\tsignal w_data_signal, r_dataSignal: std_logic_vector(7 downto 0);\n')
		f.write(f'\tsignal rd_uart_signal, wr_uart_signal: std_logic;\n')
		f.write(f'\tsignal emptySignal,empty_s,tx_empty_s,switch_s,reset_s,reset_uart: std_logic;\n')
		f.write(f'\tsignal led_s : std_logic_vector(4-1 downto 0);\n')
		f.write(f'\tsignal led_rgb_1,led_rgb_2 : std_logic_vector(3-1 downto 0);\n\r')
		f.write(f'\tsignal N_s : integer;\n')
		f.write(f'\tsignal read_s,write_s : std_logic;\n')
		
		f.write(f'begin\r\n')
		
		f.write(f'\tuart_inst : entity work.uart\n')
		
		f.write(f'\t\tgeneric map(\n')
		#f.write(f'\t\t\tDVSR      => 407,	-- baud rate divisor DVSR = 125M / (16 * baud rate) baud rate = 19200\n')
		f.write(f'\t\t\tDVSR      => 325,	-- baud rate divisor DVSR = 100M / (16 * baud rate) baud rate = 19200\n')
		f.write(f'\t\t\tDVSR_BIT  => 9,   --  bits of DVSR\n')
		f.write(f'\t\t\tFIFO_W_RX	=> {str(int(round(np.log2(N)))+1)}, 	--  addr bits of FIFO words in FIFO=2^FIFO_W\n')
		f.write(f'\t\t\tFIFO_W_TX	=> {str(int(round(np.log2(M)))+1)} 	--  addr bits of FIFO words in FIFO=2^FIFO_W\n')			
		f.write(f'\t\t)\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclk 		=> clock,\n')
		f.write(f'\t\t\treset 		=> reset,\n')
		f.write(f'\t\t\trd_uart 	=> rd_uart_signal,\n')
		f.write(f'\t\t\twr_uart 	=> wr_uart_signal,\n')
		f.write(f'\t\t\trx 			=> uart_rxd_i,\n')
		f.write(f'\t\t\tw_data 		=> w_data_signal,\n')
		f.write(f'\t\t\trx_empty	=> emptySignal,\n')
		f.write(f'\t\t\tr_data  	=> r_dataSignal,\n')
		f.write(f'\t\t\ttx  		=> uart_txd_o\n')	   
		f.write(f'\t\t);\n')
		
		f.write(f'\t{uartControl}_i : {uartControl}\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclock => clock,\n')
		f.write(f'\t\t\treset => reset_uart,\n')
		f.write(f'\t\t\tN => N_s,\n')
		f.write(f'\t\t\twrite => write_s,\n')
		f.write(f'\t\t\tempty_in => emptySignal,\n')
		f.write(f'\t\t\trd_uart => rd_uart_signal,\n')
		f.write(f'\t\t\twr_uart => wr_uart_signal\n')
		f.write(f'\t\t);\r\n')
		
		f.write(f'\t{system}_i : {system}\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclock => clock,\n')
		f.write(f'\t\t\treset => reset,\n')
		f.write(f'\t\t\treset_uart => reset_s,\n')
		f.write(f'\t\t\tr_available => rd_uart_signal,\n')
		#f.write(f'\t\t\tread => read_s,\n')
		f.write(f'\t\t\twrite => write_s,\n')
		f.write(f'\t\t\tr_data => r_dataSignal,\n')
		f.write(f'\t\t\tselector1 => selector1,\n')
		f.write(f'\t\t\tselector2 => selector2,\n')
		f.write(f'\t\t\tN => N_s,\n')
		f.write(f'\t\t\tleds => led_s,\n')
		f.write(f'\t\t\tled_rgb_1 => led_rgb_1,\n')
		f.write(f'\t\t\tled_rgb_2 => led_rgb_2,\n')
		f.write(f'\t\t\tw_data => w_data_signal\n')
		f.write(f'\t\t);\r\n')  
		
		f.write(f'\trgb_1 <= led_rgb_1;\n')
		f.write(f'\trgb_2 <= led_rgb_2;\n')
		f.write(f'\tleds <= led_s;\n')
		f.write(f'\treset_uart <= Reset or reset_s;\r\n') 
			
		f.write(f'end Behavioral;')
		
		f.close()  # Close header file 
	  
	def createUARTs(self,N,M,example = 1):
		self.createUartControl(example)
		self.createUART(example)
		self.createUartBaudGenerator(example)
		self.createUartTx(example)
		self.createUartRx(example)
		self.createUartFIFO(example)
	
	def createUartControl(self,example = 1):
		node = 'uartControl'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# uartControl entity
		uartControl = "uartControl"
		f.write(f'\tentity {uartControl} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tN : out integer;\n')
		f.write(f'\t\t\twrite : in std_logic;\n')
		f.write(f'\t\t\tempty_in : in std_logic;\n')
		f.write(f'\t\t\trd_uart : out std_logic;\n')
		f.write(f'\t\t\twr_uart : out std_logic;\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {uartControl};\r\n')

		f.write(f'architecture Behavioral of {uartControl} is\r\n')            
		
		f.write(f'begin\r\n')
		
		f.write(f'\treading : process(clock)\n')
		f.write(f'\t\tvariable count_i: integer := 0;\n')
		f.write(f'\t\tvariable L : integer := 0;\n')
		f.write(f'\tbegin\n')   
		f.write(f'\t\tif (clock = \'1\' and clock\'event) then\n')
		f.write(f'\t\t\tif reset = \'1\' then\n')          
		f.write(f'\t\t\t\tL := 0;\n') 
		f.write(f'\t\t\t\trd_uart <= \'0\';\n')
		f.write(f'\t\t\telsif empty_in = \'0\' then   -- Data available\n')
		f.write(f'\t\t\t\tcount_i := count_i + 1;\n')                          
		f.write(f'\t\t\t\tif count_i = 100E3 then    -- Count 100 msecs\n')
		f.write(f'\t\t\t\t\tcount_i := 0;\n')
		f.write(f'\t\t\t\t\trd_uart <= \'1\';     -- Request new data"+"\n')
		f.write(f'\t\t\t\t\tL := L + 1;\n')
		f.write(f'\t\t\t\telse\n')                    
		f.write(f'\t\t\t\t\trd_uart <= \'0\';\n');
		f.write(f'\t\t\t\tend if;\n')                     
		f.write(f'\t\t\telse                    -- No data\n')
		f.write(f'\t\t\t\tN <= L;\n')
		f.write(f'\t\t\t\trd_uart <= \'0\';\n')
		f.write(f'\t\t\tend if;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')
		
		f.write(f'\twriting : process(clock)\n')
		f.write(f'\t\tvariable count_j: integer := 0;\n')
		f.write(f'\tbegin\n')   
		f.write(f'\t\tif (clock = \'1\' and clock\'event) then\n')
		f.write(f'\t\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\t\twr_uart <= \'0\';\n')
		f.write(f'\t\t\telse\n')                    
		f.write(f'\t\t\t\twr_uart <= write;\n')
		f.write(f'\t\t\tend if;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n') 
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file 

	def createUART(self,example = 1):
		node = 'uart'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# uart entity
		uart = "uart"
		f.write(f'\tentity {uart} is\n')
		f.write(f'\t\tgeneric(\n')
		f.write(f'\t\t\t-- 19200 baud, 8 data bits, 1 stop bit, 2^2 FIFO\n')
		f.write(f'\t\t\tDBIT: integer := 8; -- # data bits\n')
		f.write(f'\t\t\tSB_TICK: integer := 16;	-- # ticks for stop bits, 16/24/32 -- for 1/1.5/2 stop bits\n')
		#f.write(f'\t\t\tDVSR: integer := 407; 	-- baud rate divisor -- DVSR = 125M / (16 * baud rate)\n')
		f.write(f'\t\t\tDVSR: integer := 325; 	-- baud rate divisor -- DVSR = 100M / (16 * baud rate)\n')
		f.write(f'\t\t\tDVSR_BIT: integer := 9; 	-- # bits of DVSR\n')
		f.write(f'\t\t\tFIFO_W_TX: integer := 4; 	-- # addr bits of FIFO_TX # words in FIFO=2^FIFO_W\n')
		f.write(f'\t\t\tFIFO_W_RX: integer := 4 	-- # addr bits of FIFO_TX # words in FIFO=2^FIFO_W\n')
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclk, reset : in std_logic;\n')
		f.write(f'\t\t\trd_uart, wr_uart : in std_logic;\n')
		f.write(f'\t\t\trx : in std_logic;\n')
		f.write(f'\t\t\tw_data : in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\ttx_full, rx_empty : out std_logic;\n')
		f.write(f'\t\t\tr_data : out std_logic_vector(8-1 downto 0) ;\n')
		f.write(f'\t\t\ttx : out std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {uart};\r\n') 
	
		f.write(f'architecture Behavioral of {uart} is\r\n')            
		
		f.write(f'\tsignal rx_done_tick : std_logic;\n')
		f.write(f'\tsignal tick : std_logic;\n')
		f.write(f'\tsignal tx_fifo_out : std_logic_vector(8-1 downto 0);\n')
		f.write(f'\tsignal rx_data_out : std_logic_vector(8-1 downto 0);\n')
		f.write(f'\tsignal tx_empty, tx_fifo_not_empty : std_logic;\n')
		f.write(f'\tsignal tx_done_tick : std_logic;\r\n')
		
		f.write(f'begin\r\n')
		
		f.write(f'\tbaud_gen_unit: entity work.uart_baud_gen(Behavioral)\n')
		f.write(f'\t\tgeneric map(M => DVSR, N => DVSR_BIT)\n')
		f.write(f'\t\tport map(clk => clk, reset => reset,\n')
		f.write(f'\t\t\t\tq => open, max_tick => tick);\r\n')
		
		f.write(f'\tuart_rx_unit: entity work.uart_rx(Behavioral)\n')
		f.write(f'\t\tgeneric map(DBIT => DBIT, SB_TICK => SB_TICK)\n')
		f.write(f'\t\tport map(clk => clk, reset => reset, rx => rx,\n')
		f.write(f'\t\t\t\ts_tick => tick, rx_done_tick => rx_done_tick,\n')
		f.write(f'\t\t\t\td_out => rx_data_out);\r\n')
					
		f.write(f'\tfifo_rx_unit: entity work.fifo(Behavioral)\n')
		f.write(f'\t\tgeneric map(B => DBIT, W => FIFO_W_RX)\n')
		f.write(f'\t\tport map(clk => clk, reset => reset, rd => rd_uart,\n')
		f.write(f'\t\t\t\twr => rx_done_tick, w_data => rx_data_out,\n')
		f.write(f'\t\t\t\tempty => rx_empty, full => open, r_data => r_data);\r\n')
					
		f.write(f'\tfifo_tx_unit: entity work.fifo(Behavioral)\n')
		f.write(f'\t\tgeneric map(B => DBIT, W => FIFO_W_TX)\n')
		f.write(f'\t\tport map(clk => clk, reset => reset, rd => tx_done_tick,\n')
		f.write(f'\t\t\t\twr => wr_uart, w_data => w_data, empty => tx_empty,\n')
		f.write(f'\t\t\t\tfull => tx_full, r_data => tx_fifo_out);\r\n')
					
		f.write(f'\tuart_tx_unit: entity work.uart_tx(Behavioral)\n')
		f.write(f'\t\tgeneric map(DBIT => DBIT, SB_TICK => SB_TICK)\n')
		f.write(f'\t\tport map(clk => clk, reset => reset,\n')
		f.write(f'\t\t\t\ttx_start => tx_fifo_not_empty,\n')
		f.write(f'\t\t\t\ts_tick => tick, d_in => tx_fifo_out,\n')
		f.write(f'\t\t\t\ttx_done_tick => tx_done_tick, tx => tx);\r\n')
					
		f.write(f'\ttx_fifo_not_empty <= not tx_empty;\r\n')
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file

	def createUartBaudGenerator(self,example = 1):
		node = 'uart_baud_gen'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# uart_baud_gen entity
		uart_baud_gen = "uart_baud_gen"
		f.write(f'\tentity {uart_baud_gen} is\n')
		f.write(f'\t\tgeneric(\n')
		f.write(f'\t\t\tN : integer := 4; -- number of bits;\n')
		f.write(f'\t\t\tM : integer := 10 -- mod-M;\n')
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclk, reset : in std_logic;\n')
		f.write(f'\t\t\tmax_tick : out std_logic;\n')
		f.write(f'\t\t\tq : out std_logic_vector(N-1 downto 0)\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {uart_baud_gen};\r\n') 

		f.write(f'architecture Behavioral of {uart_baud_gen} is\r\n')            
		
		f.write(f'\tsignal r_reg : unsigned(N-1 downto 0);\n')
		f.write(f'\tsignal r_next : unsigned(N-1 downto 0);\r\n')
		
		f.write(f'begin\r\n')
		
		f.write(f'\t-- printer\n')
		f.write(f'\tprocess(clk, reset)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (reset = \'1\') then\n')
		f.write(f'\t\t\tr_reg <= (others => \'0\');\n')
		f.write(f'\t\telsif rising_edge(clk) then\n')
		f.write(f'\t\t\tr_reg <= r_next;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')

		f.write(f'\t-- next-state logic\n')
		f.write(f'\tr_next <= (others => \'0\') when r_reg=(M-1) else r_reg + 1;\r\n')

		f.write(f'\t-- output logic\n')
		f.write(f'\tq <= std_logic_vector(r_reg);\n')
		f.write(f'\tmax_tick <= \'1\' when r_reg=(M-1) else \'0\';\r\n')
			
		f.write(f'end Behavioral;') 

		f.close()  # Close header file    

	def createUartTx(self,example = 1):
		node = 'uart_tx'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# uart_tx entity
		uart_tx = "uart_tx"
		f.write(f'\tentity {uart_tx} is\n')
		f.write(f'\t\tgeneric(\n')
		f.write(f'\t\t\tDBIT : integer := 8; -- # data bits;\n')
		f.write(f'\t\t\tSB_TICK : integer := 16 -- # ticks for stop bits;\n')
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclk, reset : in std_logic;\n')
		f.write(f'\t\t\ttx_start : in std_logic;\n')
		f.write(f'\t\t\ts_tick : in std_logic;\n')
		f.write(f'\t\t\td_in : in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\ttx_done_tick : out std_logic;\n')
		f.write(f'\t\t\ttx : out std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {uart_tx};\r\n') 
	
		f.write(f'architecture Behavioral of {uart_tx} is\r\n')            
		
		f.write(f'\ttype state_type is (idle, start, data, stop);\n')
		f.write(f'\tsignal state_reg, state_next: state_type;\n')
		f.write(f'\tsignal s_reg, s_next: unsigned(3 downto 0);\n')
		f.write(f'\tsignal n_reg, n_next: unsigned(2 downto 0);\n')
		f.write(f'\tsignal b_reg, b_next: std_logic_vector(7 downto 0);\n')
		f.write(f'\tsignal tx_reg, tx_next: std_logic;\r\n')
		
		f.write(f'begin\r\n')
		
		f.write(f'\t-- FSMD state & data registers\n')
		f.write(f'\tprocess(clk, reset)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\tstate_reg <= idle;\n')
		f.write(f'\t\t\ts_reg <= (others => \'0\');\n')
		f.write(f'\t\t\tn_reg <= (others => \'0\');\n')
		f.write(f'\t\t\tb_reg <= (others => \'0\');\n')
		f.write(f'\t\t\ttx_reg <= \'1\';\n')
		f.write(f'\t\telsif rising_edge(clk) then\n')
		f.write(f'\t\t\tstate_reg <= state_next;\n')
		f.write(f'\t\t\ts_reg <= s_next;\n')
		f.write(f'\t\t\tn_reg <= n_next;\n')
		f.write(f'\t\t\tb_reg <= b_next;\n')
		f.write(f'\t\t\ttx_reg <= tx_next;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')
		
		f.write(f'\t-- next-state logic & datapath functional units/routing\n')
		f.write(f'\tprocess(state_reg, s_reg, n_reg, b_reg, s_tick, tx_reg, tx_start, d_in)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tstate_next <= state_reg;\n')
		f.write(f'\t\ts_next <= s_reg;\n')
		f.write(f'\t\tn_next <= n_reg;\n')
		f.write(f'\t\tb_next <= b_reg;\n')
		f.write(f'\t\ttx_next <= tx_reg;\n')
		f.write(f'\t\ttx_done_tick <= \'0\';\n')
		f.write(f'\t\tcase state_reg is\n')
		f.write(f'\t\t\twhen idle =>\n')
		f.write(f'\t\t\t\ttx_next <= \'1\';\n')
		f.write(f'\t\t\t\tif tx_start = \'1\' then\n')
		f.write(f'\t\t\t\t\tstate_next <= start;\n')
		f.write(f'\t\t\t\t\ts_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\tb_next <= d_in;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen start =>\n')
		f.write(f'\t\t\t\ttx_next <= \'0\';\n')
		f.write(f'\t\t\t\tif (s_tick = \'1\') then\n')
		f.write(f'\t\t\t\t\tif s_reg = 15 then\n')
		f.write(f'\t\t\t\t\t\tstate_next <= data;\n')
		f.write(f'\t\t\t\t\t\ts_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\t\tn_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\ts_next <= s_reg + 1;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen data =>\n')
		f.write(f'\t\t\t\ttx_next <= b_reg(0);\n')
		f.write(f'\t\t\t\tif (s_tick = \'1\') then\n')
		f.write(f'\t\t\t\t\tif s_reg = 15 then\n')
		f.write(f'\t\t\t\t\t\ts_next <= (others => \'0\') ;\n')
		f.write(f'\t\t\t\t\t\tb_next <= \'0\' & b_reg(8-1 downto 1);\n')
		f.write(f'\t\t\t\t\t\tif n_reg = (DBIT - 1) then\n')
		f.write(f'\t\t\t\t\t\t\tstate_next <= stop;\n')
		f.write(f'\t\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\t\tn_next <= n_reg + 1 ;\n')
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\ts_next <= s_reg + 1;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen stop =>\n')
		f.write(f'\t\t\t\ttx_next <= \'1\';\n')
		f.write(f'\t\t\t\tif (s_tick = \'1\') then\n')
		f.write(f'\t\t\t\t\tif s_reg = (SB_TICK - 1) then\n')
		f.write(f'\t\t\t\t\t\tstate_next <= idle;\n')
		f.write(f'\t\t\t\t\t\ttx_done_tick <= \'1\';\n')
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\ts_next <= s_reg + 1;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\tend case;\n')
		f.write(f'\tend process;\r\n')
		
		f.write(f'\ttx <= tx_reg;\r\n')
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file   

	def createUartRx(self,example = 1):
		node = 'uart_rx'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# uart_rx entity
		uart_rx = "uart_rx"
		f.write(f'\tentity {uart_rx} is\n')
		f.write(f'\t\tgeneric(\n')
		f.write(f'\t\t\tDBIT : integer := 8; -- # data bits;\n')
		f.write(f'\t\t\tSB_TICK : integer := 16 -- # ticks for stop bits;\n')
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclk, reset : in std_logic;\n')
		f.write(f'\t\t\trx : in std_logic;\n')
		f.write(f'\t\t\ts_tick : in std_logic;\n')
		f.write(f'\t\t\trx_done_tick : out std_logic;\n')
		f.write(f'\t\t\td_out : out std_logic_vector(8-1 downto 0)\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {uart_rx};\r\n') 
	
		f.write(f'architecture Behavioral of {uart_rx} is\r\n')            
		
		f.write(f'\ttype state_type is (idle, start, data, stop);\n')
		f.write(f'\tsignal state_reg, state_next: state_type;\n')
		f.write(f'\tsignal s_reg, s_next: unsigned(3 downto 0);\n')
		f.write(f'\tsignal n_reg, n_next: unsigned(2 downto 0);\n')
		f.write(f'\tsignal b_reg, b_next: std_logic_vector(8-1 downto 0);\r\n')
		
		f.write(f'begin\r\n')
		
		f.write(f'\t-- FSMD state & data registers\n')
		f.write(f'\tprocess(clk, reset)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\tstate_reg <= idle;\n')
		f.write(f'\t\t\ts_reg <= (others => \'0\');\n')
		f.write(f'\t\t\tn_reg <= (others => \'0\');\n')
		f.write(f'\t\t\tb_reg <= (others => \'0\');\n')
		f.write(f'\t\telsif (clk\'event and clk = \'1\') then\n')
		f.write(f'\t\t\tstate_reg <= state_next;\n')
		f.write(f'\t\t\ts_reg <= s_next;\n')
		f.write(f'\t\t\tn_reg <= n_next;\n')
		f.write(f'\t\t\tb_reg <= b_next;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')
		
		f.write(f'\t-- next_state logic & data path functional units/routing\n')
		f.write(f'\tprocess(state_reg, s_reg, n_reg, b_reg, s_tick, rx)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tstate_next <= state_reg;\n')
		f.write(f'\t\ts_next <= s_reg;\n')
		f.write(f'\t\tn_next <= n_reg;\n')
		f.write(f'\t\tb_next <= b_reg;\n')
		f.write(f'\t\trx_done_tick <= \'0\';\n')
		f.write(f'\t\tcase state_reg is\n')
		f.write(f'\t\t\twhen idle =>\n')
		f.write(f'\t\t\t\tif rx = \'0\' then\n')
		f.write(f'\t\t\t\t\tstate_next <= start;\n')
		f.write(f'\t\t\t\t\ts_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen start =>\n')
		f.write(f'\t\t\t\tif (s_tick = \'1\') then\n')
		f.write(f'\t\t\t\t\tif s_reg = 8-1 then\n')
		f.write(f'\t\t\t\t\t\tstate_next <= data;\n')
		f.write(f'\t\t\t\t\t\ts_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\t\tn_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\ts_next <= s_reg + 1;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen data =>\n')
		f.write(f'\t\t\t\tif (s_tick = \'1\') then\n')
		f.write(f'\t\t\t\t\tif s_reg = 15 then\n')
		f.write(f'\t\t\t\t\t\ts_next <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\t\tb_next <= rx & b_reg(8-1 downto 1);\n')
		f.write(f'\t\t\t\t\t\tif n_reg = (DBIT-1) then\n')
		f.write(f'\t\t\t\t\t\t\tstate_next <= stop;\n')
		f.write(f'\t\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\t\tn_next <= n_reg + 1;\n')
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\ts_next <= s_reg + 1;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen stop =>\n')
		f.write(f'\t\t\t\tif (s_tick = \'1\') then\n')
		f.write(f'\t\t\t\t\tif s_reg = (SB_TICK-1) then\n')
		f.write(f'\t\t\t\t\t\tstate_next <= idle;\n')
		f.write(f'\t\t\t\t\t\trx_done_tick <= \'1\';\n')
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\ts_next <= s_reg + 1;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\tend case;\n')
		f.write(f'\tend process;\r\n')
		
		f.write(f'\td_out <= b_reg;\r\n')
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file

	def createUartFIFO(self,example = 1):
		node = 'fifo'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# FIFO entity
		fifo = "fifo"
		f.write(f'\tentity {fifo} is\n')
		f.write(f'\t\tgeneric(\n')
		f.write(f'\t\t\tB : natural := 8; -- number of bits;\n')
		f.write(f'\t\t\tW : natural := 4  -- number of address bits;\n')
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclk, reset : in std_logic;\n')
		f.write(f'\t\t\trd, wr : in std_logic;\n')
		f.write(f'\t\t\tw_data : in std_logic_vector(B-1 downto 0);\n')
		f.write(f'\t\t\tempty, full : out std_logic;\n')
		f.write(f'\t\t\tr_data : out std_logic_vector(B-1 downto 0)\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {fifo};\r\n') 
	
		f.write(f'architecture Behavioral of {fifo} is\r\n')            
		
		f.write(f'\ttype reg_file_type is array (2**W-1 downto 0) of std_logic_vector(B-1 downto 0);\n') 
		f.write(f'\tsignal array_reg: reg_file_type;\n')
		f.write(f'\tsignal w_ptr_reg, w_ptr_next, w_ptr_succ: std_logic_vector(W-1 downto 0);\n')
		f.write(f'\tsignal r_ptr_reg, r_ptr_next, r_ptr_succ: std_logic_vector(W-1 downto 0);\n')
		f.write(f'\tsignal full_reg, empty_reg, full_next, empty_next: std_logic;\n')
		f.write(f'\tsignal wr_op: std_logic_vector (1 downto 0);\n')
		f.write(f'\tsignal wr_en: std_logic;\r\n')
		
		f.write(f'begin\r\n')
		
		f.write(f'\t----------------\n')
		f.write(f'\t-- register file\n')
		f.write(f'\t----------------\n')
		f.write(f'\tprocess(clk, reset)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (reset = \'1\') then\n')
		f.write(f'\t\t\tarray_reg <= (others => (others => \'0\'));\n')
		f.write(f'\t\telsif (clk\'event and clk = \'1\') then\n')
		f.write(f'\t\t\tif wr_en = \'1\' then\n')
		f.write(f'\t\t\t\tarray_reg(to_integer(unsigned(w_ptr_reg))) <= w_data;\n')
		f.write(f'\t\t\tend if;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\t\tend process;\r\n')
		
		f.write(f'\t-- read port\n')
		f.write(f'\tr_data <= array_reg(to_integer(unsigned(r_ptr_reg)));\r\n')
		
		f.write(f'\t-- write enabled only when FIFO is not full\n')
		f.write(f'\twr_en <= wr and (not full_reg);\r\n')
			
		f.write(f'\t--\n')
		f.write(f'\t-- fifo control logic\n')
		f.write(f'\t--\n')
		f.write(f'\t-- register for read and write pointers\n')
		f.write(f'\tprocess(clk, reset)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (reset = \'1\') then\n')
		f.write(f'\t\t\tw_ptr_reg <= ( others => \'0\');\n')
		f.write(f'\t\t\tr_ptr_reg <= ( others => \'0\');\n')
		f.write(f'\t\t\tfull_reg <= \'0\';\n')
		f.write(f'\t\t\tempty_reg <= \'1\';\n')
		f.write(f'\t\telsif (clk\'event and clk = \'1\') then	\n')
		f.write(f'\t\t\tw_ptr_reg <= w_ptr_next;\n')
		f.write(f'\t\t\tr_ptr_reg <= r_ptr_next;\n')
		f.write(f'\t\t\tfull_reg <= full_next;\n')
		f.write(f'\t\t\tempty_reg <= empty_next;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')

		f.write(f'\t-- successive pointer values\n')
		f.write(f'\tw_ptr_succ <= std_logic_vector(unsigned(w_ptr_reg) + 1);\n')
		f.write(f'\tr_ptr_succ <= std_logic_vector(unsigned(r_ptr_reg) + 1);\r\n')

		f.write(f'\t-- next-state logic for read and write pointers\n')
		f.write(f'\twr_op <= wr & rd;\r\n')
		
		f.write(f'\tprocess(w_ptr_reg, w_ptr_succ, r_ptr_reg, r_ptr_succ ,wr_op, empty_reg, full_reg)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tw_ptr_next <= w_ptr_reg;\n')
		f.write(f'\t\tr_ptr_next <= r_ptr_reg;\n')
		f.write(f'\t\tfull_next <= full_reg;\n')
		f.write(f'\t\tempty_next <= empty_reg;\n')	
		f.write(f'\t\tcase wr_op is\n')
		f.write(f'\t\t\twhen "00" => -- no op\n')
		f.write(f'\t\t\twhen "01" => -- read\n')
		f.write(f'\t\t\t\tif (empty_reg /= \'1\') then -- not empty\n')
		f.write(f'\t\t\t\t\tr_ptr_next <= r_ptr_succ;\n')
		f.write(f'\t\t\t\t\tfull_next <= \'0\';\n')
		f.write(f'\t\t\t\t\tif (r_ptr_succ=w_ptr_reg) then\n')
		f.write(f'\t\t\t\t\t\tempty_next <= \'1\';\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen "10" => -- write\n')
		f.write(f'\t\t\t\tif (full_reg /= \'1\') then -- not full\n')
		f.write(f'\t\t\t\t\tw_ptr_next <= w_ptr_succ;\n')
		f.write(f'\t\t\t\t\tempty_next <= \'0\';\n')
		f.write(f'\t\t\t\t\tif (w_ptr_succ = r_ptr_reg) then\n')
		f.write(f'\t\t\t\t\t\tfull_next <= \'1\';\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\twhen others => -- write / read;\n')
		f.write(f'\t\t\t\tw_ptr_next <= w_ptr_succ;\n')
		f.write(f'\t\t\t\tr_ptr_next <= r_ptr_succ;\n')
		f.write(f'\t\tend case;\n')
		f.write(f'\tend process;\r\n')

		f.write(f'\t-- output\n')
		f.write(f'\tfull <= full_reg;\n')
		f.write(f'\tempty <= empty_reg;\r\n')
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file    

	def createSystem(self,N,M,example = 1):
		node = 'system'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)
			
		# system entity
		system = "system"
		f.write(f'\tentity {system} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock :  in std_logic;\n')
		f.write(f'\t\t\tr_data :  in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tr_available :  in std_logic;\n')
		#f.write(f'\t\t\tread :  out std_logic;\n')
		f.write(f'\t\t\twrite :  out std_logic;\n')
		f.write(f'\t\t\tselector1 :  in std_logic;\n')
		f.write(f'\t\t\tselector2 :  in std_logic;\n')
		f.write(f'\t\t\treset_uart :  out std_logic;\n')
		f.write(f'\t\t\tN :  in integer;\n')
		f.write(f'\t\t\tleds :  out std_logic_vector(4-1 downto 0);\n')
		f.write(f'\t\t\tled_rgb_1 :  out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tled_rgb_2 :  out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tw_data :  out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\treset :  in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {system};\r\n') 

		f.write(f'architecture Behavioral of {system} is\r\n')

		# detector component
		detector = 'detector'
		f.write(f'\tcomponent {detector} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock :  in std_logic;\n')
		f.write(f'\t\t\tr_data :  in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tr_available :  in std_logic;\n')
		f.write(f'\t\t\tled_rgb_1 :  out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tled_rgb_2 :  out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tpacket : out hex_array({N}-1 downto 0);\n')
		f.write(f'\t\t\tprocessing :  in std_logic;\n')
		f.write(f'\t\t\tprocessed :  out std_logic;\n')
		f.write(f'\t\t\tN :  in integer;\n')
		f.write(f'\t\t\twr_uart :  out std_logic;\n')
		f.write(f'\t\t\tw_data :  out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\treset :  in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {detector};\r\n')

		# interlocking component
		interlocking = 'interlocking'
		f.write(f'\tcomponent {interlocking} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock :  in std_logic;\n')
		f.write(f'\t\t\tprocessing :  in std_logic;\n')
		f.write(f'\t\t\tprocessed :  out std_logic;\n')
		f.write(f'\t\t\tpacket_i : in hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\tpacket_o : out hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\treset :  in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {interlocking};\r\n')

		# selector component
		selector = 'selector'
		f.write(f'\tcomponent {selector} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock :  in std_logic;\n')
		f.write(f'\t\t\tselector :  in std_logic;\n')
		f.write(f'\t\t\tleds :  out std_logic_vector(4-1 downto 0);\n')
		f.write(f'\t\t\twr_uart_1 :  in std_logic;\n')
		f.write(f'\t\t\twr_uart_2 :  in std_logic;\n')
		f.write(f'\t\t\twr_uart_3 :  out std_logic;\n')
		f.write(f'\t\t\tw_data_1 :  in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tw_data_2 :  in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tw_data_3 :  out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\treset :  in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {selector};\r\n')
		
		# printer component
		printer = 'printer'
		f.write(f'\tcomponent {printer} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock :  in std_logic;\n')
		f.write(f'\t\t\tprocessing :  in std_logic;\n')
		f.write(f'\t\t\tprocessed :  out std_logic;\n')
		f.write(f'\t\t\tpacket_i : in hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\tw_data :  out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\twr_uart :  out std_logic;\n')
		f.write(f'\t\t\treset :  in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {printer};\r\n')
		
		f.write(f'\tSignal packet_i_s : hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\tSignal packet_o_s : hex_array({str(N)}-1 downto 0);\n')
		
		f.write(f'\tSignal w_data_1,w_data_2,w_data_3 : std_logic_vector(8-1 downto 0);\n')
		f.write(f'\tSignal wr_uart_1_s,wr_uart_2_s : std_logic;\n')
		f.write(f'\tSignal pro_int_reg,pro_det_enc,pro_reg_det : std_logic;\n\r')
		
		f.write(f'begin\r\n')
		
		f.write(f'\t{detector}_i : {detector}\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclock => clock,\n')
		f.write(f'\t\t\treset => reset,\n')
		f.write(f'\t\t\tr_data => r_data,\n')
		f.write(f'\t\t\tr_available => r_available,\n')
		f.write(f'\t\t\tled_rgb_1 => led_rgb_1,\n')
		f.write(f'\t\t\tled_rgb_2 => led_rgb_2,\n')
		f.write(f'\t\t\tN => N,\n')
		f.write(f'\t\t\twr_uart => wr_uart_1_s,\n')
		f.write(f'\t\t\tprocessing => pro_reg_det,\n')
		f.write(f'\t\t\tprocessed => pro_det_enc,\n')
		f.write(f'\t\t\tpacket => packet_i_s,\n')
		f.write(f'\t\t\tw_data => w_data_1\n')
		f.write(f'\t\t);\r\n')
		
		f.write(f'\t{interlocking}_i : {interlocking}\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclock => clock,\n')
		f.write(f'\t\t\treset => reset,\n')
		f.write(f'\t\t\tprocessing => pro_det_enc,\n')
		f.write(f'\t\t\tprocessed => pro_int_reg,\n')
		f.write(f'\t\t\tpacket_i => packet_i_s,\n')
		f.write(f'\t\t\tpacket_o => packet_o_s\n')
		f.write(f'\t\t);\r\n')
		
		f.write(f'\t{printer}_i : {printer}\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclock => clock,\n')
		f.write(f'\t\t\treset => reset,\n')
		f.write(f'\t\t\tprocessing => pro_int_reg,\n')
		f.write(f'\t\t\tprocessed => pro_reg_det,\n')
		f.write(f'\t\t\tpacket_i => packet_o_s,\n')
		f.write(f'\t\t\tw_data => w_data_2,\n')
		f.write(f'\t\t\twr_uart => wr_uart_2_s\n')
		f.write(f'\t\t);\r\n')
		
		f.write(f'\t{selector}_i : {selector}\n')
		f.write(f'\t\tport map(\n')
		f.write(f'\t\t\tclock => clock,\n')
		f.write(f'\t\t\treset => reset,\n')
		f.write(f'\t\t\tleds => leds,\n')
		f.write(f'\t\t\tselector => selector1,\n')
		f.write(f'\t\t\twr_uart_1 => wr_uart_1_s,\n')
		f.write(f'\t\t\twr_uart_2 => wr_uart_2_s,\n')
		f.write(f'\t\t\twr_uart_3 => write,\n')
		f.write(f'\t\t\tw_data_1 => w_data_1,\n')
		f.write(f'\t\t\tw_data_2 => w_data_2,\n')
		f.write(f'\t\t\tw_data_3 => w_data_3\n')
		f.write(f'\t\t);\r\n')
		
		f.write(f'\t\tw_data <= w_data_3;\r\n')

		f.write(f'\t\tprocess(clock)\n')
		f.write(f'\t\tvariable counter: integer := 0;\n')
		f.write(f'\t\tbegin\n')
		f.write(f'\t\t\tif (clock = \'1\' and clock\'event) then\n')
		f.write(f'\t\t\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\t\t\treset_uart <= \'0\';\n')
		f.write(f'\t\t\t\telse\n')
		f.write(f'\t\t\t\t\tcounter := counter + 1;\n')
		f.write(f'\t\t\t\t\tif counter = 10*100E6 then\n')
		f.write(f'\t\t\t\t\t\tcounter := 0;\n') 
		f.write(f'\t\t\t\t\t\treset_uart <= \'1\';\n')  
		f.write(f'\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\treset_uart <= \'0\';\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\tend if;\n')
		f.write(f'\t\tend process;\r\n') 
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file

	def createDetector(self,N,example = 1):
    	
		node = 'detector'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)
			
		# detector entity
		detector = "detector"
		f.write(f'\tentity {detector} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tClock : in std_logic;\n')
		f.write(f'\t\t\tr_data : in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tr_available : in std_logic;\n')
		f.write(f'\t\t\tled_rgb_1 : out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tled_rgb_2 : out std_logic_vector(3-1 downto 0);\n')
		f.write(f'\t\t\tpacket : out hex_array({N}-1 downto 0);\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		f.write(f'\t\t\tN : in integer;\n')
		f.write(f'\t\t\twr_uart : out std_logic;\n')
		f.write(f'\t\t\tw_data : out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {detector};\r\n') 
	
		f.write(f'architecture Behavioral of {detector} is\r\n')

		f.write(f'\ttype states_t is (idle,reading,final,error);\n') 
		f.write(f'\tsignal state : states_t := idle;\n') 
	
		f.write(f'\tconstant tag_start : std_logic_vector(8-1 downto 0) := "00111100"; -- r_data = \'<\'\n')
		f.write(f'\tconstant tag_end : std_logic_vector(8-1 downto 0) := "00111110"; -- r_data = \'>\'\n')

		f.write(f'\t-- Lookup table for ASCII to hex_char conversion\r\n')
		f.write(f'\tconstant ascii_to_hex : ascii_array := (\r\n')
		
		f.write(f'\t\t48 => \'0\', 49 => \'1\', 50 => \'2\', 51 => \'3\', 52 => \'4\', 53 => \'5\', 54 => \'6\', 55 => \'7\',\r\n')
		f.write(f'\t\t56 => \'8\', 57 => \'9\', 65 => \'A\', 66 => \'B\', 67 => \'C\', 68 => \'D\', 69 => \'E\', 70 => \'F\',\r\n')
		f.write(f'\t\tothers => \'0\' -- default value\r\n')
		f.write(f'\t);\r\n')

		f.write(f'begin\r\n')

		f.write(f'\tdetection : process(clock,reset)\n')
		f.write(f'\t\t variable counter : integer range 0 to {str(round(N*1.5))} := 0;\n')
		f.write(f'\tbegin\n')   
		f.write(f'\t\tif (reset = \'1\') then\n')
		f.write(f'\t\t\tpacket <= (others => \'0\');\n') 
		f.write(f'\t\t\tprocessed <= \'0\';\n') 
		f.write(f'\t\t\tled_rgb_1 <= "000";\n') 
		f.write(f'\t\t\tled_rgb_2 <= "000";\n') 
		f.write(f'\t\telsif(rising_edge(clock)) then\n')
		f.write(f'\t\t\tcase(state) is\n')

		f.write(f'\t\t\t\twhen idle =>\n')

		f.write(f'\t\t\t\t\tpacket <= (others => \'0\');\n')
		f.write(f'\t\t\t\t\tprocessed <= \'0\';\n')
		f.write(f'\t\t\t\t\tled_rgb_1 <= "000";\n')
		f.write(f'\t\t\t\t\tled_rgb_2 <= "000";\n')      
		f.write(f'\t\t\t\t\tif (r_available = \'1\') then\n')           
		f.write(f'\t\t\t\t\t\tif (r_data = tag_start) then\n')
		f.write(f'\t\t\t\t\t\t\tcounter := 1;\n')
		f.write(f'\t\t\t\t\t\t\tstate <= reading;\n')
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\tend if;\n')
					   
		f.write(f'\t\t\t\twhen reading =>\n')

		f.write(f'\t\t\t\t\tled_rgb_1 <= "100";\n')
		f.write(f'\t\t\t\t\tled_rgb_2 <= "100";\n')
		f.write(f'\t\t\t\t\tprocessed <= \'0\';\n')
		f.write(f'\t\t\t\t\tif (r_available = \'1\') then\n')
		f.write(f'\t\t\t\t\t\tif (r_data = tag_end) then\n')
		f.write(f'\t\t\t\t\t\t\tif (counter = {str(N+1)}) then\n')
		f.write(f'\t\t\t\t\t\t\t\tstate <= final;\n')
		f.write(f'\t\t\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\t\t\tstate <= error;\n')
		f.write(f'\t\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\t\tif counter < {str(N+2)} then\n')	
		
		f.write(f'\t\t\t\t\t\t\tpacket(counter-1) <= ascii_to_hex(to_integer(unsigned(r_data)));\n')
	
		f.write(f'\t\t\t\t\t\t\tcounter := counter + 1;\n')
		f.write(f'\t\t\t\t\t\telse\n')
		f.write(f'\t\t\t\t\t\t\tcounter := 0;\n')
		f.write(f'\t\t\t\t\t\t\tstate <= error;\n')
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		
		f.write(f'\t\t\t\twhen final =>\n')

		f.write(f'\t\t\t\t\tled_rgb_1 <= "010";\n')
		f.write(f'\t\t\t\t\tled_rgb_2 <= "010";\n')
		f.write(f'\t\t\t\t\tprocessed <= \'1\';\n')
		f.write(f'\t\t\t\t\tif (r_available = \'1\') then\n')       
		f.write(f'\t\t\t\t\t\tif (r_data = tag_start) then\n')
		f.write(f'\t\t\t\t\t\t\tcounter := 1;\n')
		f.write(f'\t\t\t\t\t\t\tstate <= reading;\n')
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\tend if;\n')
					   
		f.write(f'\t\t\t\twhen error =>\n')

		f.write(f'\t\t\t\t\tled_rgb_1 <= "001";\n')
		f.write(f'\t\t\t\t\tled_rgb_2 <= "001";\n')
		f.write(f'\t\t\t\t\tif (r_available = \'1\') then\n')           
		f.write(f'\t\t\t\t\t\tif (r_data = tag_start) then\n') 
		f.write(f'\t\t\t\t\t\t\tcounter := 1;\n') 
		f.write(f'\t\t\t\t\t\t\tstate <= reading;\n')
		f.write(f'\t\t\t\t\t\tend if;\n') 
		f.write(f'\t\t\t\t\tend if;\n')

		f.write(f'\t\t\t\twhen others =>\n')

		f.write(f'\t\t\t\t\tled_rgb_1 <= "001";\n')
		f.write(f'\t\t\t\t\tled_rgb_2 <= "001";\n')
		f.write(f'\t\t\t\t\tif (r_available = \'1\') then\n')           
		f.write(f'\t\t\t\t\t\tif (r_data = tag_start) then\n') 
		f.write(f'\t\t\t\t\t\t\tcounter := 1;\n') 
		f.write(f'\t\t\t\t\t\t\tstate <= reading;\n')
		f.write(f'\t\t\t\t\t\tend if;\n') 
		f.write(f'\t\t\t\t\tend if;\n')

		f.write(f'\t\t\tend case;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')

		f.write(f'\tw_data <= r_data;\n')
		f.write(f'\twr_uart <= r_available;\r\n')
		f.write(f'end Behavioral;') 

		f.close()  # Close header file

	def createInterlocking(self,N,M,n_netElements,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,n_signals,example = 1):
		node = 'interlocking'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)
			
		# interlocking wrapper
		interlocking = "interlocking"
		f.write(f'\tentity {interlocking} is\n')
		f.write(f'\t\tgeneric(\n')
		f.write(f'\t\t\tN : natural := {str(N)};\n')  
		f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)}\n')
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		f.write(f'\t\t\tpacket_i : in hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\tpacket_o : out hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {interlocking};\n')
	
		f.write(f'architecture Behavioral of {interlocking} is\r\n') 
		
		# splitter component
		splitter = 'splitter'
		f.write(f'\tcomponent {splitter} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  

		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing :  in std_logic;\n')
		f.write(f'\t\t\tprocessed :  out std_logic;\n')

		f.write(f'\t\t\tpacket :  in hex_array(N-1 downto 0);\n')
		
		f.write(f'\t\t\ttracks :  out hex_array(N_TRACKCIRCUITS-1 downto 0);\n')
		if n_routes >= 1:
			f.write(f"\t\t\troutes : out {'hex_array(N_ROUTES-1 downto 0)' if n_routes > 1 else 'hex_char'};\n")
		if n_signals >= 1:
			f.write(f"\t\t\tsignals : out {'hex_array(N_SIGNALS-1 downto 0)' if n_signals > 1 else 'hex_char'};\n")
		if n_levelCrossings >= 1:
			f.write(f"\t\t\tlevelCrossings : out {'hex_array(N_LEVELCROSSINGS-1 downto 0)' if n_levelCrossings > 1 else 'hex_char'};\n")
		if n_switches >= 1:
			f.write(f"\t\t\tsingleSwitches : out {'hex_array(N_SINGLESWITCHES-1 downto 0)' if n_switches > 1 else 'hex_char'};\n")
		if n_scissorCrossings >= 1:
			f.write(f"\t\t\tscissorCrossings : out {'hex_array(N_SCRISSORCROSSINGS-1 downto 0)' if n_scissorCrossings > 1 else 'hex_char'};\n")
		if n_doubleSwitch >= 1:
			f.write(f"\t\t\tdoubleSwitches : out {'hex_array(N_DOUBLESWITCHES-1 downto 0)' if n_doubleSwitch > 1 else 'hex_char'};\n")
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {splitter};\r\n')
		
		candidates = ['A','B','C']

		# network component
		network = 'network'
		f.write(f'\tcomponent {network} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		f.write(f'\t\t\ttracks_i: in hex_array(N_TRACKCIRCUITS-1 downto 0);\n') 
		f.write(f'\t\t\ttracks_o: out hex_array(N_TRACKCIRCUITS-1 downto 0);\n') 
		f.write(f'\t\t\tsignals_i : in hex_array(N_SIGNALS-1 downto 0);\n')
		f.write(f'\t\t\tsignals_o : out hex_array(N_SIGNALS-1 downto 0);\n')
		if n_routes > 1:
			f.write(f'\t\t\troutes_i : in hex_array(N_ROUTES-1 downto 0);\n')
			f.write(f'\t\t\troutes_o : out hex_array(N_ROUTES-1 downto 0);\n')
		if n_routes == 1:
			f.write(f'\t\t\troutes_i : in hex_char;\n')
			f.write(f'\t\t\troutes_o : out hex_char;\n')
		if n_levelCrossings > 1:
			f.write(f'\t\t\tlevelCrossings_i : in hex_array(N_LEVELCROSSINGS-1 downto 0);\n')
			f.write(f'\t\t\tlevelCrossings_o : out hex_array(N_LEVELCROSSINGS-1 downto 0);\n')
		if n_levelCrossings == 1:
			f.write(f'\t\t\tlevelCrossings_i : in hex_char;\n')
			f.write(f'\t\t\tlevelCrossings_o : out hex_char;\n')
		if n_switches > 1:
			f.write(f'\t\t\tsingleSwitches_i : in hex_array(N_SINGLESWITCHES-1 downto 0);\n')  
			f.write(f'\t\t\tsingleSwitches_o : out hex_array(N_SINGLESWITCHES-1 downto 0);\n')
		if n_switches == 1:
			f.write(f'\t\t\tsingleSwitches_i : in hex_char;\n')  
			f.write(f'\t\t\tsingleSwitches_o : out hex_char;\n')

		if n_doubleSwitch > 1:
			f.write(f'\t\t\tdoubleSwitches_i : in hex_array(N_DOUBLESWITCHES-1 downto 0);\n')  
			f.write(f'\t\t\tdoubleSwitches_o : out hex_array(N_DOUBLESWITCHES-1 downto 0);\n')
		if n_doubleSwitch == 1:
			f.write(f'\t\t\tdoubleSwitches_i : in hex_char;\n')  
			f.write(f'\t\t\tdoubleSwitches_o : out hex_char;\n')
				
		if n_scissorCrossings > 1:
			f.write(f'\t\t\tscissorCrossings_i : in hex_array(N_SCISSORCROSSINGS-1 downto 0);\n')  
			f.write(f'\t\t\tscissorCrossings_o : out hex_array(N_SCISSORCROSSINGS-1 downto 0);\n')
		if n_scissorCrossings == 1:
			f.write(f'\t\t\tscissorCrossings_i : in hex_char;\n')  
			f.write(f'\t\t\tscissorCrossings_o : out hex_char;\n')
	
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {network};\r\n')
		
		# mediator component
		mediator = 'mediator'
		f.write(f'\tcomponent {mediator} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  

		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		f.write(f'\t\t\ttracks :  in hex_array(N_TRACKCIRCUITS-1 downto 0);\n')
		if n_routes >= 1:
			f.write(f"\t\t\troutes : in {'hex_array(N_ROUTES-1 downto 0)' if n_routes > 1 else 'hex_char'};\n")
		if n_signals >= 1:
			f.write(f"\t\t\tsignals : in {'hex_array(N_SIGNALS-1 downto 0)' if n_signals > 1 else 'hex_char'};\n")
		if n_levelCrossings >= 1:
			f.write(f"\t\t\tlevelCrossings : in {'hex_array(N_LEVELCROSSINGS-1 downto 0)' if n_levelCrossings > 1 else 'hex_char'};\n")
		if n_switches >= 1:
			f.write(f"\t\t\tsingleSwitches : in {'hex_array(N_SINGLESWITCHES-1 downto 0)' if n_switches > 1 else 'hex_char'};\n")
		if n_scissorCrossings >= 1:
			f.write(f"\t\t\tscissorCrossings : in {'hex_array(N_SCRISSORCROSSINGS-1 downto 0)' if n_scissorCrossings > 1 else 'hex_char'};\n")
		if n_doubleSwitch >= 1:
			f.write(f"\t\t\tdoubleSwitches : in {'hex_array(N_DOUBLESWITCHES-1 downto 0)' if n_doubleSwitch > 1 else 'hex_char'};\n")

		f.write(f'\t\t\toutput : out hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {mediator};\r\n')
		
		# voter component
		voter = 'voter'
		f.write(f'\tcomponent {voter} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')

		for i,candidate in enumerate(candidates):
			f.write(f'\t\t\tprocessing_{candidate} : in std_logic;\n')
		f.write(f'\t\t\tprocessed_V : out std_logic;\n')

		for i,candidate in enumerate(candidates):
			f.write(f'\t\t\ttracks_{candidate}: in hex_array(N_TRACKCIRCUITS-1 downto 0);\n') 
		f.write(f'\t\t\ttracks_V: out hex_array(N_TRACKCIRCUITS-1 downto 0);\n') 

		for i,candidate in enumerate(candidates):
			f.write(f'\t\t\tsignals_{candidate} : in hex_array(N_SIGNALS-1 downto 0);\n')
		f.write(f'\t\t\tsignals_V : out hex_array(N_SIGNALS-1 downto 0);\n')

		if n_routes > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\troutes_{candidate} : in hex_array(N_ROUTES-1 downto 0);\n')
			f.write(f'\t\t\troutes_V : out hex_array(N_ROUTES-1 downto 0);\n')

		if n_routes == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\troutes_{candidate} : in hex_char;\n')
			f.write(f'\t\t\troutes_V : out hex_char;\n')

		if n_levelCrossings > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tlevelCrossings_{candidate} : in hex_array(N_LEVELCROSSINGS-1 downto 0);\n')
			f.write(f'\t\t\tlevelCrossings_V : out hex_array(N_LEVELCROSSINGS-1 downto 0);\n')

		if n_levelCrossings == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tlevelCrossings_{candidate} : in hex_char;\n')
			f.write(f'\t\t\tlevelCrossings_V : out hex_char;\n')

		if n_switches > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tsingleSwitches_{candidate} : in hex_array(N_SINGLESWITCHES-1 downto 0);\n')  
			f.write(f'\t\t\tsingleSwitches_V : out hex_array(N_SINGLESWITCHES-1 downto 0);\n')

		if n_switches == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tsingleSwitches_{candidate} : in hex_char;\n')  
			f.write(f'\t\t\tsingleSwitches_V : out hex_char;\n')

		if n_doubleSwitch > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tdoubleSwitches_{candidate} : in hex_array(N_DOUBLESWITCHES-1 downto 0);\n')  
			f.write(f'\t\t\tdoubleSwitches_V : out hex_array(N_DOUBLESWITCHES-1 downto 0);\n')

		if n_doubleSwitch == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tdoubleSwitches_{candidate} : in hex_char;\n')  
			f.write(f'\t\t\tdoubleSwitches_V : out hex_char;\n')
				
		if n_scissorCrossings > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tscissorCrossings_{candidate} : in hex_array(N_SCISSORCROSSINGS-1 downto 0);\n')  
			f.write(f'\t\t\tscissorCrossings_V : out hex_array(N_SCISSORCROSSINGS-1 downto 0);\n')

		if n_scissorCrossings == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tscissorCrossings_{candidate} : in hex_char;\n')  
			f.write(f'\t\t\tscissorCrossings_V : out hex_char;\n')
	
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend component {voter};\r\n')

		f.write(f"\tSignal tc_s_i,tc_s_o,{','.join(f'tc_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_netElements)}-1 downto 0);\n")    
		f.write(f"\tSignal sig_s_i,sig_s_o,{','.join(f'sig_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_signals)}-1 downto 0);\n")
		if n_routes > 1:
			f.write(f"\tSignal rt_s_i,rt_s_o,{','.join(f'rt_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_routes)}-1 downto 0);\n")
		if n_routes == 1:
			f.write(f"\tSignal rt_s_i,rt_s_o,{','.join(f'rt_s_o_{candidate}' for candidate in candidates)} : hex_char;\n")
		if n_levelCrossings > 1:
			f.write(f"\tSignal lc_s_i,lc_s_o,{','.join(f'lc_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_levelCrossings)}-1 downto 0);\n")
		if n_levelCrossings == 1:
			f.write(f"\tSignal lc_s_i,lc_s_o,{','.join(f'lc_s_o_{candidate}' for candidate in candidates)} : hex_char;\n")
		if n_switches > 1:
			f.write(f"\tSignal ssw_s_i,ssw_s_o,{','.join(f'ssw_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_switches)}-1 downto 0);\n")
		if n_switches == 1:
			f.write(f"\tSignal ssw_s_i,ssw_s_o,{','.join(f'ssw_s_o_{candidate}' for candidate in candidates)} : hex_char;\n")
		if n_scissorCrossings > 1:
			f.write(f"\tSignal sc_s_i,sc_s_o,{','.join(f'sc_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_scissorCrossings)}-1 downto 0);\n")
		if n_scissorCrossings == 1:
			f.write(f"\tSignal sc_s_i,sc_s_o,{','.join(f'sc_s_o_{candidate}' for candidate in candidates)} : hex_char;\n")
		if n_doubleSwitch > 1:
			f.write(f"\tSignal dsw_s_i,dsw_s_o,{','.join(f'dsw_s_o_{candidate}' for candidate in candidates)} : hex_array({str(n_doubleSwitch)}-1 downto 0);\n")
		if n_doubleSwitch == 1:
			f.write(f"\tSignal dsw_s_i,dsw_s_o,{','.join(f'dsw_s_o_{candidate}' for candidate in candidates)} : hex_char;\n")
		f.write(f"\tSignal process_spt_int,process_int_med,{','.join(f'process_{candidate}' for candidate in candidates)} : std_logic;\n")
		
		f.write(f'\nbegin\r\n')  
		
		self.instantiateSplitter(f,splitter,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings)
		
		self.instantiateMediator(f,mediator,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings)
		
		for i,candidate in enumerate(candidates):
			self.instantiateNetwork(f,candidate,network,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings)
		
		self.instantiateVoter(f,candidates,voter,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings)

		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file

	def instantiateSplitter(self,f,name,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings):
    		
		# instantiate splitter
		f.write(f'\t{name}_i : {name} port map(\n')
		
		f.write(f'\t\tclock => clock,\n')
		
		f.write(f'\t\tpacket => packet_i,\n')
		f.write(f'\t\tprocessing => processing,\n')
		f.write(f'\t\tprocessed => process_spt_int,\n')
		f.write(f'\t\ttracks => tc_s_i,\n')

		f.write(f'\t\tsignals => sig_s_i,\n')
		if n_routes > 0:
			f.write(f'\t\troutes => rt_s_i,\n')
		if n_levelCrossings > 0:
			f.write(f'\t\tlevelCrossings => lc_s_i,\n')
		if n_switches > 0:    
			f.write(f'\t\tsingleSwitches => ssw_s_i,\n')
		if n_doubleSwitch > 0:    
			f.write(f'\t\tdoubleSwitches => dsw_s_i,\n')
		if n_scissorCrossings > 0:    
			f.write(f'\t\tscissorCrossings => sc_s_i,\n')
		f.write(f'\t\treset => reset\n')    
		f.write(f'\t\t);\r\n')

	def instantiateMediator(self,f,name,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings):
    		
    	# instantiate mediator
		f.write(f'\t{name}_i : {name} port map(\n')
		
		f.write(f'\t\tclock => clock,\n')
		f.write(f'\t\tprocessing => process_int_med,\n')
		f.write(f'\t\tprocessed => processed,\n')
		
		f.write(f'\t\tsignals => sig_s_o,\n')
		if n_routes > 0:
			f.write(f'\t\troutes => rt_s_o,\n')
		if n_levelCrossings > 0:
			f.write(f'\t\tlevelCrossings => lc_s_o,\n')
		if n_switches > 0:    
			f.write(f'\t\tsingleSwitches => ssw_s_o,\n')
		if n_doubleSwitch > 0:    
			f.write(f'\t\tdoubleSwitches => dsw_s_o,\n')
		if n_scissorCrossings > 0:    
			f.write(f'\t\tscissorCrossings => sc_s_o,\n')

		f.write(f'\t\ttracks => tc_s_o,\n')

		f.write(f'\t\toutput => packet_o,\n')
		f.write(f'\t\treset => reset\n')    
		f.write(f'\t\t);\r\n')

	def instantiateNetwork(self,f,candidate,name,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings):
    		
    	# instantiate network
		f.write(f'\t{name}_{candidate} : {name} port map(\n')
		
		f.write(f'\t\tclock => clock,\n')
		f.write(f'\t\ttracks_i => tc_s_i,\n')
		f.write(f'\t\ttracks_o => tc_s_o_{candidate},\n')
		f.write(f'\t\tprocessing => process_spt_int,\n')
		f.write(f'\t\tprocessed => process_{candidate},\n')
		f.write(f'\t\tsignals_i => sig_s_i,\n')
		f.write(f'\t\tsignals_o => sig_s_o_{candidate},\n')

		if n_routes > 0:
			f.write(f'\t\troutes_i => rt_s_i,\n')
			f.write(f'\t\troutes_o => rt_s_o_{candidate},\n')	
		if n_levelCrossings > 0:
			f.write(f'\t\tlevelCrossings_i => lc_s_i,\n')
			f.write(f'\t\tlevelCrossings_o => lc_s_o_{candidate},\n')
		if n_switches > 0:    
			f.write(f'\t\tsingleSwitches_i => ssw_s_i,\n')
			f.write(f'\t\tsingleSwitches_o => ssw_s_o_{candidate},\n') 
		if n_doubleSwitch > 0:    
			f.write(f'\t\tdoubleSwitches_i => dsw_s_i,\n')
			f.write(f'\t\tdoubleSwitches_o => dsw_s_o_{candidate},\n') 
		if n_scissorCrossings > 0:    
			f.write(f'\t\tscissorCrossings_i => sc_s_i,\n')
			f.write(f'\t\tscissorCrossings_o => sc_s_o_{candidate},\n')

		f.write(f'\t\treset => reset\n')
		
		f.write(f'\t\t);\r\n')

	def instantiateVoter(self,f,candidates,name,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings):
				
		# instantiate Voter
		f.write(f'\t{name}_i : {name} port map(\n')
		
		f.write(f'\t\tclock => clock,\n')
		for i,candidate in enumerate(candidates):
			f.write(f'\t\ttracks_{candidate} => tc_s_o_{candidate},\n')
		f.write(f'\t\ttracks_V => tc_s_o,\n')
		for i,candidate in enumerate(candidates):
			f.write(f'\t\tprocessing_{candidate} => process_{candidate},\n')
		f.write(f'\t\tprocessed_V => process_int_med,\n')
		for i,candidate in enumerate(candidates):
			f.write(f'\t\tsignals_{candidate} => sig_s_o_{candidate},\n')
		f.write(f'\t\tsignals_V => sig_s_o,\n')

		if n_routes > 0:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\troutes_{candidate} => rt_s_o_{candidate},\n')
			f.write(f'\t\troutes_V => rt_s_o,\n')	

		if n_levelCrossings > 0:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\tlevelCrossings_{candidate} => lc_s_o_{candidate},\n')
			f.write(f'\t\tlevelCrossings_V => lc_s_o,\n')

		if n_switches > 0:   
			for i,candidate in enumerate(candidates):
				f.write(f'\t\tsingleSwitches_{candidate} => ssw_s_o_{candidate},\n')
			f.write(f'\t\tsingleSwitches_V => ssw_s_o,\n') 

		if n_doubleSwitch > 0:    
			for i,candidate in enumerate(candidates):
				f.write(f'\t\tdoubleSwitches_{candidate} => dsw_s_o_{candidate},\n')
			f.write(f'\t\tdoubleSwitches_V => dsw_s_o,\n') 

		if n_scissorCrossings > 0:    
			for i,candidate in enumerate(candidates):
				f.write(f'\t\tscissorCrossings_{candidate} => sc_s_o_{candidate},\n')
			f.write(f'\t\tscissorCrossings_V => sc_s_o,\n')

		f.write(f'\t\treset => reset\n')
		
		f.write(f'\t\t);\r\n')

	def createSplitter(self,N,n_netElements,n_routes,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example = 1):
		node = 'splitter'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)
			
		# splitter entity
		splitter = "splitter"
		f.write(f'\tentity {splitter} is\n')
		f.write(f'\t\tgeneric(\n')
		 
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  

		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
		f.write(f'\t\t\tprocessing :  in std_logic := \'0\';\n')
		f.write(f'\t\t\tprocessed :  out std_logic := \'0\';\n')

		f.write(f'\t\t\tpacket :  in hex_array(N-1 downto 0) := (others => \'0\');\n')
		
		f.write(f'\t\t\ttracks :  out hex_array(N_TRACKCIRCUITS-1 downto 0) := (others => \'0\');\n')
		if n_routes >= 1:
			f.write(f"\t\t\troutes : out {'hex_array(N_ROUTES-1 downto 0)' if n_routes > 1 else 'hex_char'};\n")
		if n_signals >= 1:
			f.write(f"\t\t\tsignals : out {'hex_array(N_SIGNALS-1 downto 0)' if n_signals > 1 else 'hex_char'};\n")
		if n_levelCrossings >= 1:
			f.write(f"\t\t\tlevelCrossings : out {'hex_array(N_LEVELCROSSINGS-1 downto 0)' if n_levelCrossings > 1 else 'hex_char'};\n")
		if n_switches >= 1:
			f.write(f"\t\t\tsingleSwitches : out {'hex_array(N_SINGLESWITCHES-1 downto 0)' if n_switches > 1 else 'hex_char'};\n")
		if n_scissorCrossings >= 1:
			f.write(f"\t\t\tscissorCrossings : out {'hex_array(N_SCRISSORCROSSINGS-1 downto 0)' if n_scissorCrossings > 1 else 'hex_char'};\n")
		if n_doubleSwitch >= 1:
			f.write(f"\t\t\tdoubleSwitches : out {'hex_array(N_DOUBLESWITCHES-1 downto 0)' if n_doubleSwitch > 1 else 'hex_char'};\n")
		f.write(f'\t\t\treset : in std_logic := \'0\'\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {splitter};\r\n')
	
		f.write(f'architecture Behavioral of {splitter} is\r\n') 
			
		f.write(f'begin\r\n')  
		
		# Ocupation | Routes | signals | levelCrossings | singleSwitches | doubleSwitches | scissorCrossinges

		f.write(f'\tprocess(processing)\n')
		f.write(f'\tbegin\n')
		
		f.write(f'\t\tif processing = \'1\' then\n')

		f.write(f'\t\t\ttracks <= packet({n_netElements-1} downto 0);\n')
		
		if n_routes > 1:
			f.write(f'\t\t\troutes <= packet({n_netElements+n_routes-1} downto {n_netElements});\n')
		if n_routes == 1:
			f.write(f'\t\t\troutes <= packet({n_netElements+n_routes-1});\n')
		if n_signals > 1:
			f.write(f'\t\t\tsignals <= packet({n_signals+n_netElements+n_routes-1} downto {n_netElements+n_routes});\n')
		if n_signals == 1:
			f.write(f'\t\t\tsignals <= packet({n_signals+n_netElements+n_routes-1});\n')	
		if n_levelCrossings > 1:
			f.write(f'\t\t\tlevelCrossings <= packet({n_levelCrossings+n_signals+n_netElements+n_routes-1} downto {n_signals+n_netElements+n_routes});\n')
		if n_levelCrossings == 1:
			f.write(f'\t\t\tlevelCrossings <= packet({n_levelCrossings+n_signals+n_netElements+n_routes-1});\n')	
		if n_switches > 1:
			f.write(f'\t\t\tsingleSwitches <= packet({n_switches+n_levelCrossings+n_signals+n_netElements+n_routes-1} downto {n_levelCrossings+n_signals+n_netElements+n_routes});\n')
		if n_switches == 1:
			f.write(f'\t\t\tsingleSwitches <= packet({n_switches+n_levelCrossings+n_signals+n_netElements+n_routes-1});\n')	
		if n_doubleSwitch > 1:
			f.write(f'\t\t\tdoubleSwitches <= packet({n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_netElements+n_routes-1} downto {n_switches+n_levelCrossings+n_signals+n_netElements+n_routes});\n')
		if n_doubleSwitch == 1:
			f.write(f'\t\t\t\tdoubleSwitches <= packet({n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_netElements+n_routes-1});\n')
		if n_scissorCrossings > 1:
			f.write(f'\t\t\tscissorCrossings <= packet({n_scissorCrossings+n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_netElements+n_routes-1} downto {n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_netElements+n_routes});\n')
		if n_scissorCrossings == 1:
			f.write(f'\t\t\tscissorCrossings <= packet({n_scissorCrossings+n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_netElements+n_routes-1});\n')	

		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')    
		f.write(f'\tprocessed <= processing;\n') 
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file 

	def createMediator(self,N,M,n_netElements,n_routes,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example = 1):
		node = 'mediator'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)
			
		# mediator entity
		mediator = "mediator"
		f.write(f'\tentity {mediator} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  

		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		f.write(f'\t\t\ttracks :  in hex_array(N_TRACKCIRCUITS-1 downto 0);\n')
		if n_routes >= 1:
			f.write(f"\t\t\troutes : in {'hex_array(N_ROUTES-1 downto 0)' if n_routes > 1 else 'hex_char'};\n")
		if n_signals >= 1:
			f.write(f"\t\t\tsignals : in {'hex_array(N_SIGNALS-1 downto 0)' if n_signals > 1 else 'hex_char'};\n")
		if n_levelCrossings >= 1:
			f.write(f"\t\t\tlevelCrossings : in {'hex_array(N_LEVELCROSSINGS-1 downto 0)' if n_levelCrossings > 1 else 'hex_char'};\n")
		if n_switches >= 1:
			f.write(f"\t\t\tsingleSwitches : in {'hex_array(N_SINGLESWITCHES-1 downto 0)' if n_switches > 1 else 'hex_char'};\n")
		if n_scissorCrossings >= 1:
			f.write(f"\t\t\tscissorCrossings : in {'hex_array(N_SCRISSORCROSSINGS-1 downto 0)' if n_scissorCrossings > 1 else 'hex_char'};\n")
		if n_doubleSwitch >= 1:
			f.write(f"\t\t\tdoubleSwitches : in {'hex_array(N_DOUBLESWITCHES-1 downto 0)' if n_doubleSwitch > 1 else 'hex_char'};\n")

		f.write(f'\t\t\toutput : out hex_array(N-1 downto 0);\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {mediator};\r\n') 
	
		f.write(f'architecture Behavioral of {mediator} is\r\n')      
		
		f.write(f'begin\r\n')  
		
	# Ocupation | Routes | signals | levelCrossings | singleSwitches | doubleSwitches | scissorCrossings
		
		f.write(f'\tprocess(processing)\n')
		f.write(f'\tbegin\n')
		
		f.write(f'\t\tif (processing = \'1\') then\n')

		f.write(f'\t\t\toutput({n_netElements-1} downto 0) <= tracks;\n')
		
		if n_routes > 1:
			f.write(f'\t\t\toutput({n_routes+n_netElements-1} downto {n_netElements}) <= routes;\n')
		if n_routes == 1:
			f.write(f'\t\t\toutput({n_routes+n_netElements-1}) <= routes ;\n')
		if n_signals > 1:
			f.write(f'\t\t\toutput({n_signals+n_netElements+n_routes-1} downto {n_netElements+n_routes}) <= signals;\n')
		if n_signals == 1:
			f.write(f'\t\t\toutput({n_signals+n_netElements+n_routes-1}) <= signals;\n')	
		if n_levelCrossings > 1:
			f.write(f'\t\t\toutput({n_levelCrossings+n_signals+n_routes+n_netElements-1} downto {n_signals+n_routes+n_netElements}) <= levelCrossings;\n')
		if n_levelCrossings == 1:
			f.write(f'\t\t\toutput({n_levelCrossings+n_signals+n_routes+n_netElements-1}) <= levelCrossings;\n')	
		if n_switches > 1:
			f.write(f'\t\t\toutput({n_switches+n_levelCrossings+n_signals+n_routes+n_netElements-1} downto {n_levelCrossings+n_signals+n_routes+n_netElements}) <= singleSwitches;\n')
		if n_switches == 1:
			f.write(f'\t\t\toutput({n_switches+n_levelCrossings+n_signals+n_routes+n_netElements-1}) <= singleSwitches;\n')	
		if n_doubleSwitch > 1:
			f.write(f'\t\t\toutput({n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_routes+n_netElements-1} downto {n_switches+n_levelCrossings+n_signals+n_routes+n_netElements}) <= doubleSwitches;\n')
		if n_doubleSwitch == 1:
			f.write(f'\t\t\toutput({n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_routes+n_netElements-1}) <= doubleSwitches;\n')
		if n_scissorCrossings > 1:
			f.write(f'\t\t\toutput({n_scissorCrossings+n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_routes+n_netElements-1} downto {n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_routes+n_netElements}) <= scissorCrossings;\n')
		if n_scissorCrossings == 1:
			f.write(f'\t\t\toutput({n_scissorCrossings+n_doubleSwitch+n_switches+n_levelCrossings+n_signals+n_routes+n_netElements-1}) <= scissorCrossings;\n')

		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')   
		f.write(f'\tprocessed <= processing;\n')
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file  

	def createNetwork(self,graph,routes,N,n_netElements,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example = 1):
		print('')
		n_routes = len(routes)
		
		node = 'network'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)

		# network entity
		network = "network"
		f.write(f'\tentity {network} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		if n_netElements >= 1:
			f.write(f"\t\t\ttracks_i : in {'hex_array(N_TRACKCIRCUITS-1 downto 0)' if n_netElements > 1 else 'hex_char'};\n")
			f.write(f"\t\t\ttracks_o : out {'hex_array(N_TRACKCIRCUITS-1 downto 0)' if n_netElements > 1 else 'hex_char'};\n")
		if n_signals >= 1:
			f.write(f"\t\t\tsignals_i : in {'hex_array(N_SIGNALS-1 downto 0)' if n_signals > 1 else 'hex_char'};\n")
			f.write(f"\t\t\tsignals_o : out {'hex_array(N_SIGNALS-1 downto 0)' if n_signals > 1 else 'hex_char'};\n")
		if n_routes >= 1:
			f.write(f"\t\t\troutes_i : in {'hex_array(N_ROUTES-1 downto 0)' if n_routes > 1 else 'hex_char'};\n")
			f.write(f"\t\t\troutes_o : out {'hex_array(N_ROUTES-1 downto 0)' if n_routes > 1 else 'hex_char'};\n")
		if n_levelCrossings >= 1:
			f.write(f"\t\t\tlevelCrossings_i : in {'hex_array(N_LEVELCROSSINGS-1 downto 0)' if n_levelCrossings > 1 else 'hex_char'};\n")
			f.write(f"\t\t\tlevelCrossings_o : out {'hex_array(N_LEVELCROSSINGS-1 downto 0)' if n_levelCrossings > 1 else 'hex_char'};\n")
		if n_switches >= 1:
			f.write(f"\t\t\tsingleSwitches_i : in {'hex_array(N_SINGLESWITCHES-1 downto 0)' if n_switches > 1 else 'hex_char'};\n")
			f.write(f"\t\t\tsingleSwitches_o : out {'hex_array(N_SINGLESWITCHES-1 downto 0)' if n_switches > 1 else 'hex_char'};\n")
		if n_scissorCrossings >= 1:	
			f.write(f"\t\t\tscissorCrossings_i : in {'hex_array(N_SCISSORCROSSINGS-1 downto 0)' if n_scissorCrossings > 1 else 'hex_char'};\n")
			f.write(f"\t\t\tscissorCrossings_o : out {'hex_array(N_SCISSORCROSSINGS-1 downto 0)' if n_scissorCrossings > 1 else 'hex_char'};\n")
		if n_doubleSwitch >= 1:
			f.write(f"\t\t\tdoubleSwitches_i : in {'hex_array(N_DOUBLESWITCHES-1 downto 0)' if n_doubleSwitch > 1 else 'hex_char'};\n")  
			f.write(f"\t\t\tdoubleSwitches_o : out {'hex_array(N_DOUBLESWITCHES-1 downto 0)' if n_doubleSwitch > 1 else 'hex_char'};\n")
		
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {network};\r\n')

		f.write(f'architecture Behavioral of {network} is\r\n')

		levelCrossingData = self.getLevelCrossings(graph,routes)
		#print(levelCrossingData)
		singleSwitchData = self.getSingleSwitch(graph,routes)
		#print(singleSwitchData)
		scissorCrossingData = self.getScissorCrossing(graph,routes)
		#print(scissorCrossingData)
		doubleSwitchData = self.getDoubleSwitch(graph,routes)
		#print(doubleSwitchData)
		signalData = self.getSignal(graph,routes)
		#print(signalData)
	
		for i in signalData:
			ocupationLevel_0,ocupationLevel_1,ocupationLevel_2,signal_0,signal_1,signal_2,switches_1,switches_2,paths = self.getSignalGraph(i,signalData)
			for path in paths:
				if paths[path]['LevelCrossings'] != []:
					new_route = signalData[i]['Routes'][signalData[i]['Next'].index(paths[path]['Signals'][1])]
					lcs = paths[path]['LevelCrossings']
					#print(f'Z {i} {paths[path]['Signals'][1]} {lcs} {new_route}')
					for lc in lcs:
						if new_route not in levelCrossingData[lc]['Routes']:
							levelCrossingData[lc]['Routes'].append(f'{new_route}')
		#print(levelCrossingData)	
		for i in signalData:
			signal = ""
			ocupationLevel_0,ocupationLevel_1,ocupationLevel_2,signal_0,signal_1,signal_2,switches_1,switches_2,paths = self.getSignalGraph(i,signalData)
			for path in paths:
				#sws = []
				if paths[path]['Switches'] != []:
					new_route = signalData[i]['Routes'][signalData[i]['Next'].index(paths[path]['Signals'][1])]
					#if sws == []:
					sws = paths[path]['Switches']
					if signal != paths[path]['Signals'][1]:
						signal = paths[path]['Signals'][1]
						print(f'Z {i} {signal} {sws} {new_route}')

						for sw in sws:
							switch,position = sw.split('_')
							#print(switch,position)
							if len(position) == 1 and new_route not in singleSwitchData[switch]['Routes']:
								singleSwitchData[switch]['Routes'].append(f'{new_route}')
								singleSwitchData[switch]['Position'].append(f'{position}')

		# component levelCrossing  
		if n_levelCrossings > 0:
			for levelCrossingId in levelCrossingData:
				index = list(levelCrossingData.keys()).index(levelCrossingId)
				self.createLevelCrossing(index,levelCrossingId,levelCrossingData[levelCrossingId],signalData,mode = 'component',f = f)
				self.createLevelCrossing(index,levelCrossingId,levelCrossingData[levelCrossingId],signalData,mode = 'entity',f = None, example = example)	
		# component singleSwitch  
		if n_switches > 0:  	
			for singleSwitchId in singleSwitchData:
				index = list(singleSwitchData.keys()).index(singleSwitchId)
				self.createSingleSwitch(index,singleSwitchId,singleSwitchData[singleSwitchId],mode = 'component',f = f)
				self.createSingleSwitch(index,singleSwitchId,singleSwitchData[singleSwitchId],mode = 'entity',f = None, example = example)
		# component scissorCrossing  
		if n_scissorCrossings > 0:  	
			for scissorCrossingId in scissorCrossingData:
				index = list(scissorCrossingData.keys()).index(scissorCrossingId)
				self.createScissorCrossing(index,scissorCrossingId,scissorCrossingData[scissorCrossingId],mode = 'component',f = f)
				self.createScissorCrossing(index,scissorCrossingId,scissorCrossingData[scissorCrossingId],mode = 'entity',f = None, example = example)
		# component doubleSwitch  
		if n_doubleSwitch > 0:  
			for doubleSwitchId in doubleSwitchData:
				index = list(doubleSwitchData.keys()).index(doubleSwitchId)
				self.createDoubleSwitch(index,doubleSwitchId,doubleSwitchData[doubleSwitchId],mode = 'component',f = f)
				self.createDoubleSwitch(index,doubleSwitchId,doubleSwitchData[doubleSwitchId],mode = 'entity',f = None, example = example)
		# component signals  
		if n_signals > 0:

			futureRoute = {}

			for route in routes:
				end = routes[route]['End']

				if end not in futureRoute:
					futureRoute[end] = []
				futureRoute[end].append(f'R{route}')

			for signalId in signalData:
				#if signalId in futureRoute:
				#	print(f'XZY {signalId} {futureRoute[signalId]}')
				index = list(signalData.keys()).index(signalId)
				self.createSignal(index,signalId,signalData,futureRoute,mode = 'component',f = f)
				self.createSignal(index,signalId,signalData,futureRoute,mode = 'entity',f = None, example = example)
		# component node
		if n_netElements > 0:
			for netElementId in list(graph.keys()):
				index = list(graph.keys()).index(netElementId)
				self.createNode(index,netElementId,routes,mode = 'component',f = f)
				self.createNode(index,netElementId,routes,mode = 'entity',f = None, example = example)
		# component route
		if n_routes > 0:
			for routeId in list(routes.keys()):
				print(f'R_{routeId} | {routes[routeId]}')
				index = list(routes.keys()).index(routeId)
				self.createRoute(index,routes[routeId],levelCrossingData,singleSwitchData,doubleSwitchData,scissorCrossingData,mode = 'component',f = f)
				self.createRoute(index,routes[routeId],levelCrossingData,singleSwitchData,doubleSwitchData,scissorCrossingData,mode = 'entity',f = None, example = example)

		# intersignals
		if n_levelCrossings > 0:
			levelCrossings = " , ".join([f'state_{i}' for i in list(levelCrossingData.keys())])
			f.write(f'\tsignal {levelCrossings} : hex_char;\n')
		if n_switches > 0: 
			singleSwitches = " , ".join([f'state_{i}' for i in list(singleSwitchData.keys())])
			f.write(f'\tsignal {singleSwitches} : hex_char;\n')
		if n_scissorCrossings > 0:
			scissorCrossings = " , ".join([f'state_{i}' for i in list(scissorCrossingData.keys())])
			f.write(f'\tsignal {scissorCrossings} : hex_char;\n')
		if n_doubleSwitch > 0: 
			doubleSwitches = " , ".join([f'state_{i}' for i in list(doubleSwitchData.keys())])
			f.write(f'\tsignal {doubleSwitches} : hex_char;\n')
		if n_signals > 0: 
			signals = " , ".join([f'state_{i}' for i in list(signalData.keys())])
			f.write(f'\tsignal {signals} : hex_char;\n')	
		if n_netElements > 0:
			commands = " , ".join([f'cmd_R{i}_{j}' for i in routes for j in routes[i]['Path']])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\n')

			commands = " , ".join([f'state_{i}' for i in list(graph.keys())])
			f.write(f'\tsignal {commands} : hex_char;\n')
		if n_levelCrossings > 0:
			commands = " , ".join([f'cmd_{rt}_{lc}' for lc in levelCrossingData for rt in levelCrossingData[lc]['Routes']])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\n')
		if n_switches > 0: 
			commands = " , ".join([f'cmd_{rt}_{sw}' for sw in singleSwitchData for rt in singleSwitchData[sw]['Routes']])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\n')
		if n_doubleSwitch > 0: 
			commands = " , ".join([f'cmd_{rt}_{dw}' for dw in doubleSwitchData for rt in doubleSwitchData[dw]['Routes']])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\n')
		if n_scissorCrossings > 0:
			commands = " , ".join([f'cmd_R{i}_{j.split('_')[0]}' for i in routes for j in routes[i]['ScissorCrossings']])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\n')
		if n_signals > 0: 
			commands = " , ".join([f'cmd_R{i}_{routes[i]['Start']}' for i in routes])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\r\n')
			commands = " , ".join([f'cmd_R{i}_{routes[i]['End']}' for i in routes])
			f.write(f'\tsignal {commands} : routeCommands := RELEASE;\r\n')
	
		f.write(f'begin\r\n') 
		
		#print(list(graph.keys()))

		# instantiate levelCrossings
		for levelCrossingId in levelCrossingData:
			index = list(levelCrossingData.keys()).index(levelCrossingId)
			f.write(f'\tlevelCrossing_{levelCrossingId} : levelCrossing_{index} port map(')

			for element in levelCrossingData[levelCrossingId]['Neighbour']:
				netElement = list(graph.keys()).index(element)
				f.write(f'track_{element} => tracks_i({netElement}), ')
							
			for element in levelCrossingData[levelCrossingId]['Routes']:
				f.write(f'{element}_command => cmd_{element}_{levelCrossingId}, ')

			if n_levelCrossings > 1:
				f.write(f'indication => levelCrossings_i({index}), command  => levelCrossings_o({index}), ')
			if n_levelCrossings == 1:
				f.write(f'indication => levelCrossings_i, command  => levelCrossings_o, ')
			f.write(f'correspondence => state_{levelCrossingId}, ')		
			f.write(f'clock => clock, reset => reset);\r\n')

		# instantiate singleSwitches
		for singleSwitchId in singleSwitchData:
			index = list(singleSwitchData.keys()).index(singleSwitchId)
			f.write(f'\tsingleSwitch_{singleSwitchId} : singleSwitch_{index} port map(')
	
			for element in singleSwitchData[singleSwitchId]['Routes']:
				f.write(f'{element}_command => cmd_{element}_{singleSwitchId}, ')

			if n_switches > 1:
				f.write(f'indication => singleSwitches_i({index}), command => singleSwitches_o({index}), ')
			if n_switches == 1:
				f.write(f'indication => singleSwitches_i, command => singleSwitches_o, ')
			f.write(f'correspondence => state_{singleSwitchId}, ')

			f.write(f'clock => clock, reset => reset);\r\n')
		
		# instantiate scissorCrossings
		for scissorCrossingId in scissorCrossingData:
			index = list(scissorCrossingData.keys()).index(scissorCrossingId)
			f.write(f'\tscissorCrossing_{scissorCrossingId} : scissorCrossing_{index} port map(')

			for element in scissorCrossingData[scissorCrossingId]['Routes']:
				f.write(f'{element}_command => cmd_{element}_{scissorCrossingId}, ')

			if n_scissorCrossings > 1:
				f.write(f'indication => scissorCrossings_i({index}), command => scissorCrossings_o({index}), ')
			if n_scissorCrossings == 1:
				f.write(f'indication => scissorCrossings_i, command => scissorCrossings_o, ')
			f.write(f'correspondence => state_{scissorCrossingId}, ')

			f.write(f'clock => clock, reset => reset);\r\n')

		# instantiate doubleSwitches
		for doubleSwitchId in doubleSwitchData:
			index = list(doubleSwitchData.keys()).index(doubleSwitchId)
			f.write(f'\tdoubleSwitch_{doubleSwitchId} : doubleSwitch_{index} port map(')
	
			for element in doubleSwitchData[doubleSwitchId]['Routes']:
				f.write(f'{element}_command => cmd_{element}_{doubleSwitchId}, ')

			if n_doubleSwitch > 1:
				f.write(f'indication => doubleSwitches_i({index}), command => doubleSwitches_o({index}),')
			if n_doubleSwitch == 1:
				f.write(f'indication => doubleSwitches_i, command => doubleSwitches_o, ')
			f.write(f'correspondence=> state_{doubleSwitchId}, ')
		
			f.write(f'clock => clock, reset => reset);\r\n')

		# instantiate signals
		for signalId in signalData:
			index = list(signalData.keys()).index(signalId)
			f.write(f'\trailwaySignal_{signalId} : railwaySignal_{index} port map(')
	
			if 'Routes' in signalData[signalId]:
				for element in signalData[signalId]['Routes']:
					f.write(f'{element}_command => cmd_{element}_{signalId}, ')

			if signalId in futureRoute:
				for element in futureRoute[signalId]:
					f.write(f'{element}_command => cmd_{element}_{signalId}, ')

			ocupationLevel_0,ocupationLevel_1,ocupationLevel_2,signal_0,signal_1,signal_2,switches_1,switches_2,paths = self.getSignalGraph(signalId,signalData)

			netElement = list(graph.keys()).index(ocupationLevel_0)
			f.write(f'track_{ocupationLevel_0} => tracks_i({netElement}), ')
			if ocupationLevel_1 != []:
				for i in ocupationLevel_1:
					if i != ocupationLevel_0:
						netElement = list(graph.keys()).index(i)
						f.write(f'track_{i} => tracks_i({netElement}), ')		
			if ocupationLevel_2 != []:
				for i in ocupationLevel_2:
					if i not in ocupationLevel_1 and i != ocupationLevel_0:
						netElement = list(graph.keys()).index(i)
						f.write(f'track_{i} => tracks_i({netElement}), ')

			if signal_1 != []:
				for i in signal_1:
					f.write(f'correspondence_{i} => state_{i}, ')		
			if signal_2 != []:
				for i in signal_2:
					if i not in signal_1:
						f.write(f'correspondence_{i} => state_{i}, ')

			sw_print = []
			for path in paths:
				if paths[path]['Switches'] != []:
					for i in paths[path]['Switches']:
						if i.split('_')[0] not in sw_print:
							sw_print.append(i.split('_')[0])
			if sw_print != []:
				for i in sw_print:
					f.write(f'{"s" if i[0].isdigit() else ""}{i.split('_')[0]}_state => state_{i.split('_')[0]}, ')	

			lc_print = []
			for path in paths:
				if paths[path]['LevelCrossings'] != []:
					for i in paths[path]['LevelCrossings']:
						if i not in lc_print:
							lc_print.append(i.split('_')[0])
			if lc_print != []:
				for i in lc_print:
					f.write(f'{i}_state => state_{i}, ')	

			if n_signals > 1:
				f.write(f'indication => signals_i({index}), command => signals_o({index}), ')
			if n_signals == 1:
				f.write(f'indication => signals_i, command => signals_o, ')
			f.write(f'correspondence_{signalId} => state_{signalId}, ')
		
			f.write(f'clock => clock, reset => reset);\r\n')

		# instantiate nodes
		for netElementId in list(graph.keys()):
			index = list(graph.keys()).index(netElementId)
			f.write(f'\tnode_{netElementId} : node_{index} port map(')
			
			if n_netElements > 1:
				#f.write(f'track_i => tracks_i({index}), track_o => tracks_o({index}), ')
				f.write(f'track_i => tracks_i({index}), track_o => state_{netElementId}, ')
			if n_netElements == 1:	
				#f.write(f'track_i => tracks_i, track_o => tracks_o, ')	
				f.write(f'track_i => tracks_i, track_o => state_{netElementId}, ')	

			for route in routes:
				if netElementId in routes[route]['Path']:
					f.write(f'R{route}_command => cmd_R{route}_{netElementId}, ')
	
			f.write(f'reset => reset);\r\n')

		# instantiate routes

		for routeId in list(routes.keys()):
			index = list(routes.keys()).index(routeId)

			lc_list = [key for key, value in levelCrossingData.items() if f'R{routeId}' in value['Routes']]
			sw_list = [key for key, value in singleSwitchData.items() if f'R{routeId}' in value['Routes']]
			dw_list = [key for key, value in doubleSwitchData.items() if f'R{routeId}' in value['Routes']]
			sc_list = [key for key, value in scissorCrossingData.items() if f'R{routeId}' in value['Routes']]

			f.write(f'\troute_R{routeId} : route_{index} port map(')

			if n_routes > 1:
				f.write(f'routeRequest => routes_i({index}), ')
			if n_routes == 1:
				f.write(f'routeRequest => routes_i, ')	

			for netElementId in list(graph.keys()):
				track_index = list(graph.keys()).index(netElementId)
				if netElementId in routes[routeId]['Path']:
					f.write(f'{netElementId}_command => cmd_R{routeId}_{netElementId}, ')
					#f.write(f'track_{netElementId} => tracks_i({track_index}), ')
					f.write(f'track_{netElementId} => state_{netElementId}, ')
	
			for levelCrossingId in lc_list:
				if levelCrossingId != None:
					f.write(f'{levelCrossingId}_command => cmd_R{routeId}_{levelCrossingId}, ')	
					f.write(f'{levelCrossingId}_state => state_{levelCrossingId}, ')
			
			for singleSwitchId in sw_list:
				if singleSwitchId != None:
					f.write(f'{"s" if singleSwitchId[0].isdigit() else ""}{singleSwitchId.split('_')[0]}_command => cmd_R{routeId}_{singleSwitchId.split('_')[0]}, ')	
					f.write(f'{"s" if singleSwitchId[0].isdigit() else ""}{singleSwitchId.split('_')[0]}_state => state_{singleSwitchId.split('_')[0]}, ')

			for doubleSwitchId in dw_list:
				if doubleSwitchId != None:
					f.write(f'{"s" if doubleSwitchId[0].isdigit() else ""}{doubleSwitchId.split('_')[0]}_command => cmd_R{routeId}_{doubleSwitchId.split('_')[0]}, ')	
					f.write(f'{"s" if doubleSwitchId[0].isdigit() else ""}{doubleSwitchId.split('_')[0]}_state => state_{doubleSwitchId.split('_')[0]}, ')

			for scissorCrossingId in sc_list:
				f.write(f'{"s" if scissorCrossingId[0].isdigit() else ""}{scissorCrossingId.split('_')[0]}_command => cmd_R{routeId}_{scissorCrossingId.split('_')[0]}, ')	
				f.write(f'{"s" if scissorCrossingId[0].isdigit() else ""}{scissorCrossingId.split('_')[0]}_state => state_{scissorCrossingId.split('_')[0]}, ')

			f.write(f'{routes[routeId]['Start']}_state => state_{routes[routeId]['Start']}, ')
			f.write(f'{routes[routeId]['Start']}_command => cmd_R{routeId}_{routes[routeId]['Start']}, ')	

			f.write(f'{routes[routeId]['End']}_state => state_{routes[routeId]['End']}, ')
			f.write(f'{routes[routeId]['End']}_command =>cmd_R{routeId}_{routes[routeId]['End']}, ')

			f.write(f'routeExecute => routes_o({index}), ')

			f.write(f'clock => clock, reset => reset);\r\n')

		f.write(f'\tprocessed <= processing;\r\n')
		#f.write(f'tracks_o <= tracks_i;\r\n')
		#f.write(f'routes_o <= routes_i;\r\n')
		#f.write(f'signals_o <= signals_i;\r\n')
		#f.write(f'levelCrossings_o <= levelCrossings_i;\r\n')
		#f.write(f'singleSwitches_o <= singleSwitches_i;\r\n')

		for i,j in enumerate(list(graph.keys())):
			f.write(f'\ttracks_o({i}) <= state_{j};\r\n')

		f.write(f'end Behavioral;') 
    
		f.close()  # Close header file	

	def createVoter(self,graph,routes,N,n_netElements,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example = 1):
		print('')
		n_routes = len(routes)
		
		node = 'voter'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)

		candidates = ['A','B','C']

		voter = 'voter'
		f.write(f'\tentity {voter} is\n')
		f.write(f'\t\tgeneric(\n')
		if n_netElements > 0:
			f.write(f'\t\t\tN_TRACKCIRCUITS : natural := {str(n_netElements)};\n')	
		if n_routes > 0:         
			f.write(f'\t\t\tN_ROUTES : natural := {str(n_routes)};\n')
		if n_signals > 0:
			f.write(f'\t\t\tN_SIGNALS : natural := {str(n_signals)};\n')
		if n_levelCrossings > 0:
			f.write(f'\t\t\tN_LEVELCROSSINGS : natural := {str(n_levelCrossings)};\n')
		if n_switches > 0:         
			f.write(f'\t\t\tN_SINGLESWITCHES : natural := {str(n_switches)};\n')
		if n_doubleSwitch > 0:         
			f.write(f'\t\t\tN_DOUBLESWITCHES : natural := {str(n_doubleSwitch)};\n')
		if n_scissorCrossings > 0:         
			f.write(f'\t\t\tN_SCRISSORCROSSINGS : natural := {str(n_scissorCrossings)};\n')
		f.write(f'\t\t\tN : natural := {str(N)}\n')  
		f.write(f'\t\t);\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')

		for i,candidate in enumerate(candidates):
			f.write(f'\t\t\tprocessing_{candidate} : in std_logic;\n')
		f.write(f'\t\t\tprocessed_V : buffer std_logic;\n')

		for i,candidate in enumerate(candidates):
			f.write(f'\t\t\ttracks_{candidate}: in hex_array(N_TRACKCIRCUITS-1 downto 0);\n') 
		f.write(f'\t\t\ttracks_V: buffer hex_array(N_TRACKCIRCUITS-1 downto 0);\n') 

		for i,candidate in enumerate(candidates):
			f.write(f'\t\t\tsignals_{candidate} : in hex_array(N_SIGNALS-1 downto 0);\n')
		f.write(f'\t\t\tsignals_V : buffer hex_array(N_SIGNALS-1 downto 0);\n')

		if n_routes > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\troutes_{candidate} : in hex_array(N_ROUTES-1 downto 0);\n')
			f.write(f'\t\t\troutes_V : buffer hex_array(N_ROUTES-1 downto 0);\n')

		if n_routes == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\troutes_{candidate} : in hex_char;\n')
			f.write(f'\t\t\troutes_V : buffer hex_char;\n')

		if n_levelCrossings > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tlevelCrossings_{candidate} : in hex_array(N_LEVELCROSSINGS-1 downto 0);\n')
			f.write(f'\t\t\tlevelCrossings_V : buffer hex_array(N_LEVELCROSSINGS-1 downto 0);\n')

		if n_levelCrossings == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tlevelCrossings_{candidate} : in hex_char;\n')
			f.write(f'\t\t\tlevelCrossings_V : buffer hex_char;\n')

		if n_switches > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tsingleSwitches_{candidate} : in hex_array(N_SINGLESWITCHES-1 downto 0);\n')  
			f.write(f'\t\t\tsingleSwitches_V : buffer hex_array(N_SINGLESWITCHES-1 downto 0);\n')

		if n_switches == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tsingleSwitches_{candidate} : in hex_char;\n')  
			f.write(f'\t\t\tsingleSwitches_V : buffer hex_char;\n')

		if n_doubleSwitch > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tdoubleSwitches_{candidate} : in hex_array(N_DOUBLESWITCHES-1 downto 0);\n')  
			f.write(f'\t\t\tdoubleSwitches_V : buffer hex_array(N_DOUBLESWITCHES-1 downto 0);\n')

		if n_doubleSwitch == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tdoubleSwitches_{candidate} : in hex_char;\n')  
			f.write(f'\t\t\tdoubleSwitches_V : buffer hex_char;\n')
				
		if n_scissorCrossings > 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tscissorCrossings_{candidate} : in hex_array(N_SCISSORCROSSINGS-1 downto 0);\n')  
			f.write(f'\t\t\tscissorCrossings_V : buffer hex_array(N_SCISSORCROSSINGS-1 downto 0);\n')

		if n_scissorCrossings == 1:
			for i,candidate in enumerate(candidates):
				f.write(f'\t\t\tscissorCrossings_{candidate} : in hex_char;\n')  
			f.write(f'\t\t\tscissorCrossings_V : buffer hex_char;\n')

		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {voter};\r\n')
			
		f.write(f'architecture Behavioral of {voter} is\r\n')

		f.write(f'\tfunction two_out_of_three_hex(input1, input2, input3: hex_char) return hex_char is\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (input1 = input2) then\n')
		f.write(f'\t\t\treturn input1;\n')
		f.write(f'\t\telsif (input1 = input3) then\n')
		f.write(f'\t\t\treturn input1;\n')
		f.write(f'\t\telsif (input2 = input3) then\n')
		f.write(f'\t\t\treturn input2;\n')
		f.write(f'\t\telse\n')
		f.write(f'\t\t\treturn \'F\';  -- Return \'F\' to indicate the default case;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend function;\n')

		f.write(f'\tfunction two_out_of_three(input1, input2, input3: std_logic) return std_logic is\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (input1 = input2) then\n')
		f.write(f'\t\t\treturn input1;\n')
		f.write(f'\t\telsif (input1 = input3) then\n')
		f.write(f'\t\t\treturn input1;\n')
		f.write(f'\t\telsif (input2 = input3) then\n')
		f.write(f'\t\t\treturn input2;\n')
		f.write(f'\t\telse\n')
		f.write(f'\t\t\treturn \'0\';  -- Return \'0\' to indicate the default case;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend function;\n')

		f.write(f'\tsignal default_case_flag : std_logic;\n') 

		f.write(f'begin\r\n') 

		f.write(f'\tprocess(clock, reset)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\tprocessed_V <= \'0\';\n')
		f.write(f'\t\t\tdefault_case_flag <= \'0\';\n')
		f.write(f'\t\telsif rising_edge(clock) then\n')
		f.write(f'\t\t\tdefault_case_flag <= \'0\';  -- Reset the flag\n')

		if n_netElements > 1:
			f.write(f'\t\t\tfor i in 0 to N_TRACKCIRCUITS-1 loop\n')
			f.write(f'\t\t\t\ttracks_V(i) <= two_out_of_three_hex(tracks_A(i), tracks_B(i), tracks_C(i));\n')
			f.write(f'\t\t\t\tif tracks_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_netElements == 1:
			f.write(f'\t\t\t\ttracks_V <= two_out_of_three_hex(tracks_A, tracks_B, tracks_C);\n')
			f.write(f'\t\t\t\tif tracks_V = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')

		if n_signals > 1:
			f.write(f'\t\t\tfor i in 0 to N_SIGNALS-1 loop\n')
			f.write(f'\t\t\t\tsignals_V(i) <= two_out_of_three_hex(signals_A(i), signals_B(i), signals_C(i));\n')
			f.write(f'\t\t\t\tif signals_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_signals == 1:
			f.write(f'\t\t\t\tsignals_V <= two_out_of_three_hex(signals_A, signals_B, signals_C);\n')
			f.write(f'\t\t\t\tif signals_V = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')

		if n_routes > 1:
			f.write(f'\t\t\tfor i in 0 to N_ROUTES-1 loop\n')
			f.write(f'\t\t\t\troutes_V(i) <= two_out_of_three_hex(routes_A(i), routes_B(i), routes_C(i));\n')
			f.write(f'\t\t\t\tif routes_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_routes == 1:
			f.write(f'\t\t\t\troutes_V <= two_out_of_three_hex(routes_A, routes_B, routes_C);\n')
			f.write(f'\t\t\t\tif routes_V = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')

		if n_levelCrossings > 1:
			f.write(f'\t\t\tfor i in 0 to N_LEVELCROSSINGS-1 loop\n')
			f.write(f'\t\t\t\tlevelCrossings_V(i) <= two_out_of_three_hex(levelCrossings_A(i), levelCrossings_B(i), levelCrossings_C(i));\n')
			f.write(f'\t\t\t\tif levelCrossings_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_levelCrossings == 1:
			f.write(f'\t\t\tlevelCrossings_V <= two_out_of_three_hex(levelCrossings_A, levelCrossings_B, levelCrossings_C);\n')
			f.write(f'\t\t\tif levelCrossings_V = \'F\' then\n')
			f.write(f'\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\tend if;\n')

		if n_switches > 1:
			f.write(f'\t\t\tfor i in 0 to N_SINGLESWITCHES-1 loop\n')
			f.write(f'\t\t\t\tsingleSwitches_V(i) <= two_out_of_three_hex(singleSwitches_A(i), singleSwitches_B(i), singleSwitches_C(i));\n')
			f.write(f'\t\t\t\tif singleSwitches_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_switches == 1:
			f.write(f'\t\t\t\tsingleSwitches_V <= two_out_of_three_hex(singleSwitches_A, singleSwitches_B, singleSwitches_C);\n')
			f.write(f'\t\t\t\tif singleSwitches_V = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')

		if n_doubleSwitch > 1:
			f.write(f'\t\t\tfor i in 0 to N_DOUBLESWITCHES-1 loop\n')
			f.write(f'\t\t\t\tdoubleSwitches_V(i) <= two_out_of_three_hex(doubleSwitches_A(i), doubleSwitches_B(i), doubleSwitches_C(i));\n')
			f.write(f'\t\t\t\tif doubleSwitches_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_doubleSwitch == 1:
			f.write(f'\t\t\t\tdoubleSwitches_V <= two_out_of_three_hex(doubleSwitches_A, doubleSwitches_B, doubleSwitches_C);\n')
			f.write(f'\t\t\t\tif doubleSwitches_V = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
		
		if n_scissorCrossings > 1:
			f.write(f'\t\t\tfor i in 0 to N_SCISSORCROSSINGS-1 loop\n')
			f.write(f'\t\t\t\tscissorCrossings_V(i) <= two_out_of_three_hex(scissorCrossings_A(i), scissorCrossings_B(i), scissorCrossings_C(i));\n')
			f.write(f'\t\t\t\tif scissorCrossings_V(i) = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend loop;\n')
		if n_scissorCrossings == 1:
			f.write(f'\t\t\t\tscissorCrossings_V <= two_out_of_three_hex(scissorCrossings_A, scissorCrossings_B, scissorCrossings_C);\n')
			f.write(f'\t\t\t\tif scissorCrossings_V = \'F\' then\n')
			f.write(f'\t\t\t\t\tdefault_case_flag <= \'1\';\n')
			f.write(f'\t\t\t\tend if;\n')

		f.write(f'\t\t\tif default_case_flag = \'1\' then\n')
		f.write(f'\t\t\t\tprocessed_V <= \'0\';\n')
		f.write(f'\t\t\telse\n')
		f.write(f'\t\t\t\tprocessed_V <= two_out_of_three(processing_A, processing_B, processing_C);\n')
		f.write(f'\t\t\tend if;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\n')
		
		f.write(f'end Behavioral;') 

		f.close()  # Close header file	

	def getLevelCrossings(self,network,routes):
		levelCrossingId = {}

		for element in network:
			if 'LevelCrossing' in network[element]:
				for levelCrossing in network[element]['LevelCrossing']:
					if levelCrossing not in levelCrossingId:
						levelCrossingId[levelCrossing] = {'Neighbour':[]}
					
					if element not in levelCrossingId[levelCrossing]['Neighbour']:
						levelCrossingId[levelCrossing]['Neighbour'].append(element)

					if network[element]['Neighbour'] not in levelCrossingId[levelCrossing]['Neighbour']:
						for i in network[element]['Neighbour']:
							levelCrossingId[levelCrossing]['Neighbour'].append(i)

		for levelCrossing in levelCrossingId:
			for route in routes:
				if levelCrossing in routes[route]['LevelCrossings']:
					if 'Routes' not in levelCrossingId[levelCrossing]:
						levelCrossingId[levelCrossing] |= {'Routes':[]}
					if route not in levelCrossingId[levelCrossing]['Routes']:
						levelCrossingId[levelCrossing]['Routes'].append(f'R{route}')

		return levelCrossingId

	def getSingleSwitch(self,network,routes):
		singleSwitchId = {}

		for element in network:
			if 'Switch' in network[element]:
				for switch in network[element]['Switch']:
					if switch not in singleSwitchId:
						singleSwitchId[switch] = {'Neighbour':3*[None]} 

					if element not in singleSwitchId[switch]['Neighbour']:
						singleSwitchId[switch]['Neighbour'][0] = element

			if 'Switch_B' in network[element]:
				for switch in network[element]['Switch_B']:
					if switch not in singleSwitchId:
						singleSwitchId[switch] = {'Neighbour':3*[None]} 

					if element not in singleSwitchId[switch]['Neighbour']:
						singleSwitchId[switch]['Neighbour'][1] = element
			if 'Switch_C' in network[element]:
				for switch in network[element]['Switch_C']:
					if switch not in singleSwitchId:
						singleSwitchId[switch] = {'Neighbour':3*[None]} 

					if element not in singleSwitchId[switch]['Neighbour']:
						singleSwitchId[switch]['Neighbour'][2] = element

		for singleSwitch in singleSwitchId:
			for route in routes:
				if singleSwitch+'_N' in routes[route]['Switches']:
					if 'Routes' not in singleSwitchId[singleSwitch]:
						singleSwitchId[singleSwitch] |= {'Routes':[]}
						singleSwitchId[singleSwitch] |= {'Position':[]}
					if route not in singleSwitchId[singleSwitch]['Routes']:
						singleSwitchId[singleSwitch]['Routes'].append(f'R{route}')
						singleSwitchId[singleSwitch]['Position'].append(f'N')
				if singleSwitch+'_R' in routes[route]['Switches']:
					if 'Routes' not in singleSwitchId[singleSwitch]:
						singleSwitchId[singleSwitch] |= {'Routes':[]}
						singleSwitchId[singleSwitch] |= {'Position':[]}
					if route not in singleSwitchId[singleSwitch]['Routes']:
						singleSwitchId[singleSwitch]['Routes'].append(f'R{route}')
						singleSwitchId[singleSwitch]['Position'].append(f'R')
		return singleSwitchId

	def getScissorCrossing(self,network,routes):
		scissorCrossingId = {}

		for element in network:
			if 'Crossing' in network[element]:
				for scissorCrossing in network[element]['Crossing']:
					if scissorCrossing not in scissorCrossingId:
						scissorCrossingId[scissorCrossing] = {'Neighbour':[]} 
					
					if element not in scissorCrossingId[scissorCrossing]['Neighbour']:
						scissorCrossingId[scissorCrossing]['Neighbour'].append(element)

		for scissorCrossing in scissorCrossingId:
			for route in routes:
				if scissorCrossing+'_XN' in routes[route]['ScissorCrossings']:
					if 'Routes' not in scissorCrossingId[scissorCrossing]:
						scissorCrossingId[scissorCrossing] |= {'Routes':[]}
						scissorCrossingId[scissorCrossing] |= {'Position':[]}
					if route not in scissorCrossingId[scissorCrossing]['Routes']:
						scissorCrossingId[scissorCrossing]['Routes'].append(f'R{route}')
						scissorCrossingId[scissorCrossing]['Position'].append(f'N')
				if scissorCrossing+'_XR' in routes[route]['ScissorCrossings']:
					if 'Routes' not in scissorCrossingId[scissorCrossing]:
						scissorCrossingId[scissorCrossing] |= {'Routes':[]}
						scissorCrossingId[scissorCrossing] |= {'Position':[]}
					if route not in scissorCrossingId[scissorCrossing]['Routes']:
						scissorCrossingId[scissorCrossing]['Routes'].append(f'R{route}')
						scissorCrossingId[scissorCrossing]['Position'].append(f'R')
		return scissorCrossingId

	def getDoubleSwitch(self,network,routes):
		doubleSwitchId = {}

		for element in network:
			if 'Switch_X' in network[element]:
				for doubleSwitch in network[element]['Switch_X']:
					if doubleSwitch not in doubleSwitchId:
						doubleSwitchId[doubleSwitch] = {'Neighbour':[]} 
					
					if element not in doubleSwitchId[doubleSwitch]['Neighbour']:
						doubleSwitchId[doubleSwitch]['Neighbour'].append(element)

		for doubleSwitch in doubleSwitchId:
			for route in routes:
				if doubleSwitch+'_NN' in routes[route]['Switches']:
					if 'Routes' not in doubleSwitchId[doubleSwitch]:
						doubleSwitchId[doubleSwitch] |= {'Routes':[]}
						doubleSwitchId[doubleSwitch] |= {'Position':[]}
					if route not in doubleSwitchId[doubleSwitch]['Routes']:
						doubleSwitchId[doubleSwitch]['Routes'].append(f'R{route}')
						doubleSwitchId[doubleSwitch]['Position'].append(f'NN')
				if doubleSwitch+'_NR' in routes[route]['Switches']:
					if 'Routes' not in doubleSwitchId[doubleSwitch]:
						doubleSwitchId[doubleSwitch] |= {'Routes':[]}
						doubleSwitchId[doubleSwitch] |= {'Position':[]}
					if route not in doubleSwitchId[doubleSwitch]['Routes']:
						doubleSwitchId[doubleSwitch]['Routes'].append(f'R{route}')
						doubleSwitchId[doubleSwitch]['Position'].append(f'NR')
				if doubleSwitch+'_RN' in routes[route]['Switches']:
					if 'Routes' not in doubleSwitchId[doubleSwitch]:
						doubleSwitchId[doubleSwitch] |= {'Routes':[]}
						doubleSwitchId[doubleSwitch] |= {'Position':[]}
					if route not in doubleSwitchId[doubleSwitch]['Routes']:
						doubleSwitchId[doubleSwitch]['Routes'].append(f'R{route}')
						doubleSwitchId[doubleSwitch]['Position'].append(f'RN')
				if doubleSwitch+'_RR' in routes[route]['Switches']:
					if 'Routes' not in doubleSwitchId[doubleSwitch]:
						doubleSwitchId[doubleSwitch] |= {'Routes':[]}
						doubleSwitchId[doubleSwitch] |= {'Position':[]}
					if route not in doubleSwitchId[doubleSwitch]['Routes']:
						doubleSwitchId[doubleSwitch]['Routes'].append(f'R{route}')
						doubleSwitchId[doubleSwitch]['Position'].append(f'RR')
		return doubleSwitchId

	def getSignal(self,network,routes):
		signalId = {}

		for element in network:
			if 'Signal' in network[element]:
				for signal in network[element]['Signal']:
					if signal not in signalId:
						signalId[signal] = {}
						signalId[signal] |= {'Start':element}

		for signal in signalId:
			switch_aux = []
			lc_aux = []
			for route in routes:
				if signal == routes[route]['Start']:
					if 'Routes' not in signalId[signal]:
						signalId[signal] |= {'Routes':[]}
					if f'R{route}' not in signalId[signal]['Routes']:
						signalId[signal]['Routes'].append(f'R{route}')

					if 'Next' not in signalId[signal]:
						signalId[signal] |= {'Next':[]}
					if routes[route]['Path'][1:] not in signalId[signal]['Next']:
						signalId[signal]['Next'].append(routes[route]['End'])

					if 'Switches' not in signalId[signal]:
						signalId[signal] |= {'Switches':[]}

					if routes[route]['Switches'] != [] or routes[route]['ScissorCrossings'] != []:

						if routes[route]['Switches'] != [] and routes[route]['Switches'] not in switch_aux:
							switch_aux.append(routes[route]['Switches'])
						if routes[route]['ScissorCrossings'] != [] and routes[route]['ScissorCrossings'] not in switch_aux:
							switch_aux.append(routes[route]['ScissorCrossings'])

					signalId[signal]['Switches'] = switch_aux

					if 'LevelCrossings' not in signalId[signal]:
						signalId[signal] |= {'LevelCrossings':[]}
					#if routes[route]['LevelCrossings'] not in signalId[signal]['LevelCrossings']:
					signalId[signal]['LevelCrossings'].append(routes[route]['LevelCrossings'])	

					if 'Path' not in signalId[signal]:
						signalId[signal] |= {'Path':[]}
					if routes[route]['Path'][1:] not in signalId[signal]['Path']:
						signalId[signal]['Path'].append(routes[route]['Path'][1:])						

		print('')
		for signal in signalId:
			print(f'{signal} > {signalId[signal]}')	
		print('')
		return signalId

	def createLevelCrossing(self,index,name,data,signalData,mode, f = None,example = 1):	
		if mode == 'entity':
			node = f'levelCrossing_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)

		levelCrossing = f'levelCrossing_{index}'
		f.write(f'\t{mode} {levelCrossing} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\treset : in std_logic;\n')

		for neighbour in data['Neighbour']:
			f.write(f'\t\t\ttrack_{neighbour} : in hex_char;\n')

		ocupation = " or ".join([f'{i}_state = OCCUPIED' for i in data['Neighbour']])
		
		track_status = ",".join([f'{i}_state' for i in data['Neighbour']])

		commands = []
		for routes in data['Routes']:
			f.write(f'\t\t\t{routes}_command : in routeCommands;\r\n')
			commands.append(routes)

		f.write(f'\t\t\tindication : in hex_char;\n')
		f.write(f'\t\t\tcommand : out hex_char;\n')
		f.write(f'\t\t\tcorrespondence : out hex_char\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {levelCrossing};\n')

		if mode == 'entity':
			freeState = " and ".join([f'{i}_command = RELEASE' for i in commands])
			reserveState = " or ".join([f'{i}_command = RESERVE' for i in commands])
			lockState = " or ".join([f'{i}_command = LOCK' for i in commands])

			freq = 100e6
			timeout = 7

			FF = math.ceil(math.log2(timeout*freq))

			t = [(2**(i+1))/freq for i in range(FF)]
			sequence = [0]*FF
			total = 0
			for i in range(FF-1,-1,-1):
				if total + t[i] <= timeout:
					total += t[i]
					sequence[i] = 1
			timeout_stop = " and ".join([f'Q({i}) = \'{sequence[i]}\'' for i in range(FF)])
			timeout = '0'+"".join([f'{sequence[i]}' for i in range(FF)])[::-1]

			f.write(f'architecture Behavioral of {node} is\r\n')

			f.write(f'\tcomponent flipFlop is\r\n')
			f.write(f'\t\tport(\r\n')
			f.write(f'\t\t\tclock : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\treset : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\tQ : out std_logic := \'0\'\r\n')
			f.write(f'\t\t);\r\n')
			f.write(f'\tend component flipFlop;\r\n')

			f.write(f'\tsignal restart : std_logic := \'1\';\n')
			f.write(f'\tsignal Q : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal clock_in : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal timeout : std_logic := \'0\';\n')

			f.write(f'\tsignal commandState : routeCommands := RELEASE;\n')

			f.write(f'\tsignal lockStateIn : objectLock := RELEASED;\n')
			f.write(f'\tsignal lockStateOut : objectLock := RELEASED;\n')
			f.write(f'\tsignal positionStateIn : levelCrossingStates := UP;\n')
			f.write(f'\tsignal positionStateOut : levelCrossingStates := UP;\n')
			f.write(f'\tsignal correspondenceState : levelCrossingStates := UP;\n')
			for neighbour in data['Neighbour']:
				f.write(f'\tsignal {neighbour}_state : nodeStates := FREE;\n')
			
			f.write(f'begin\n')
			f.write(f'\tclock_in(0) <= clock;\r\n')
			f.write(f'\t-- Assign the last 2 bits of indication to lockState\n')
			f.write(f"\tlockStateIn <= objectLock'val(to_integer(unsigned(hex_to_slv(indication)(0 to 1))));\n")

			f.write(f'\t-- Assign the first 2 bits of indication to positionState\n')
			f.write(f"\tpositionStateIn <= levelCrossingStates'val(to_integer(unsigned(hex_to_slv(indication)(2 to 3))));\n")

			f.write(f'\t-- Assign the last 2 bits of track_x to x_state\n')
			for neighbour in data['Neighbour']:
				f.write(f"\t{neighbour}_state <= nodeStates'val(to_integer(unsigned(hex_to_slv(track_{neighbour})(2 to 3))));\n")

			f.write(f'\t-- Update command based on the values of positionStateOut and lockStateOut\n')
			f.write(f"\tcommand <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(levelCrossingStates'pos(positionStateOut), 2)));\n")
			f.write(f'\t-- Update correspondence based on the values of correspondenceState and lockStateOut\n')
			f.write(f"\tcorrespondence <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(levelCrossingStates'pos(correspondenceState), 2)));\n")

			f.write(f'\tgen : for i in 0 to {FF-1} generate\r\n')
			f.write(f'\t\t inst: flipFlop port map(clock_in(i), restart, Q(i));\r\n')
			f.write(f'\t\tclock_in(i+1) <= Q(i);\r\n')
			f.write(f'\tend generate;\r\n')

			route_cmd = ",".join([f'{i}_command' for i in commands])

			f.write(f'\n\tprocess(timeout,{route_cmd})\n')
			f.write(f'\tbegin\n')
			
			f.write(f'\t\tif (timeout = \'1\') then\n')
			f.write(f'\t\t\tcommandState <= RELEASE;\n')
			f.write(f'\t\telse\n')

			f.write(f'\t\t\tif ({freeState}) then\n')
			f.write(f'\t\t\t\tcommandState <= RELEASE;\n')
			f.write(f'\t\t\tend if;\n')

			f.write(f'\t\t\tif ({reserveState}) then\n')
			f.write(f'\t\t\t\tcommandState <= RESERVE;\n')
			f.write(f'\t\t\tend if;\n')

			f.write(f'\t\t\tif ({lockState}) then\n')
			f.write(f'\t\t\t\tcommandState <= LOCK;\n')
			f.write(f'\t\t\tend if;\n')

			f.write(f'\t\tend if;\n')

			f.write(f'\tend process;\n') 

			f.write(f'\n\tprocess(timeout,commandState,positionStateIn,{track_status})\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tcase commandState is\n')
			f.write(f'\t\t\twhen RELEASE => -- AUTOMATIC\n')
			f.write(f'\t\t\t\tif (({ocupation}) and timeout = \'0\') then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= DOWN;\n')
			f.write(f'\t\t\t\telse\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= RELEASED;\n')
			f.write(f'\t\t\twhen RESERVE => -- DONT CHANGE\n')
			f.write(f'\t\t\t\tpositionStateOut <= DOWN;\n')
			f.write(f'\t\t\t\tlockStateOut <= RESERVED;\n')
			f.write(f'\t\t\twhen LOCK => -- DONT CHANGE\n')
			f.write(f'\t\t\t\tpositionStateOut <= DOWN;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\t\twhen others =>\n')
			f.write(f'\t\t\t\tpositionStateOut <= DOWN;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\tend case;\n')
			f.write(f'\tend process;\n') 

			f.write(f'\n\tprocess(clock,reset,Q,restart)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tif (reset = \'1\' or Q = "{timeout}") then\n')
			f.write(f'\t\t\ttimeout <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\t\tif (restart = \'1\') then\n')
			f.write(f'\t\t\ttimeout <= \'0\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(timeout,positionStateOut,positionStateIn)\n')
			f.write(f'\tbegin\n')
					
			f.write(f'\t\tif (positionStateOut = DOWN and positionStateIn = DOWN) then\n')
			f.write(f'\t\t\tcorrespondenceState <= DOWN;\n')
			f.write(f'\t\t\trestart <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			
			f.write(f'\t\tif (positionStateOut = UP and positionStateIn = UP) then\n')
			f.write(f'\t\t\tcorrespondenceState <= UP;\n')
			f.write(f'\t\t\trestart <= \'1\';\n')
			f.write(f'\t\tend if;\n')

			f.write(f'\t\tif (positionStateOut /= positionStateIn) then\n')
			f.write(f'\t\t\tcorrespondenceState <= TRANSITION;\n')
			f.write(f'\t\t\trestart <= \'0\';\n')
			f.write(f'\t\tend if;\n')
		
			f.write(f'\tend process;\r\n') 

			f.write(f'end Behavioral;') 
			f.close()  # Close header file

	def createSingleSwitch(self,index,name,data,mode, f = None,example = 1):
		if mode == 'entity':
			node = f'singleSwitch_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)
		
		singleSwitch = f'singleSwitch_{index}'
		f.write(f'\t{mode} {singleSwitch} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
		f.write(f'\t\t\treset : in std_logic := \'0\';\n')

		commands = []
		commands_N = []
		commands_R = []
		for element in range(len(data['Routes'])):
			f.write(f'\t\t\t{data['Routes'][element]}_command : in routeCommands := RELEASE;\n')
			commands.append(data['Routes'][element])
			if data['Position'][element] == 'N':
				commands_N.append(data['Routes'][element])
			else:
				commands_R.append(data['Routes'][element])	

		f.write(f'\t\t\tindication : in hex_char;\n')
		f.write(f'\t\t\tcommand : out hex_char;\n')
		f.write(f'\t\t\tcorrespondence : out hex_char\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {singleSwitch};\n')

		if mode == 'entity':
			freeState = " and ".join([f'{i}_command = RELEASE' for i in commands])
			freeState_N = " and ".join([f'{i}_command = RELEASE' for i in commands_N])
			freeState_R = " and ".join([f'{i}_command = RELEASE' for i in commands_R])
			reserveState = " or ".join([f'{i}_command = RESERVE' for i in commands])
			reserveState_N = " or ".join([f'{i}_command = RESERVE' for i in commands_N])
			reserveState_R = " or ".join([f'{i}_command = RESERVE' for i in commands_R])
			lockState = " or ".join([f'{i}_command = LOCK' for i in commands])
			lockState_N = " or ".join([f'{i}_command = LOCK' for i in commands_N])
			lockState_R = " or ".join([f'{i}_command = LOCK' for i in commands_R])

			freq = 100e6
			timeout = 7

			FF = math.ceil(math.log2(timeout*freq))

			t = [(2**(i+1))/freq for i in range(FF)]
			sequence = [0]*FF
			total = 0
			for i in range(FF-1,-1,-1):
				if total + t[i] <= timeout:
					total += t[i]
					sequence[i] = 1
			timeout_stop = " and ".join([f'Q({i}) = \'{sequence[i]}\'' for i in range(FF)])
			timeout = '0'+"".join([f'{sequence[i]}' for i in range(FF)])[::-1]

			route_cmd = ",".join([f'{i}_command' for i in commands])

			f.write(f'architecture Behavioral of {node} is\n')

			f.write(f'\tcomponent flipFlop is\r\n')
			f.write(f'\t\tport(\r\n')
			f.write(f'\t\t\tclock : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\treset : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\tQ : out std_logic := \'0\'\r\n')
			f.write(f'\t\t);\r\n')
			f.write(f'\tend component flipFlop;\r\n')

			f.write(f'\tsignal restart : std_logic := \'1\';\n')
			f.write(f'\tsignal Q : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal clock_in : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal timeout : std_logic := \'0\';\n')

			f.write(f'\tsignal commandState : routeCommands := RELEASE;\r\n')
			
			f.write(f'\tsignal lockStateIn : objectLock := RELEASED;\n')
			f.write(f'\tsignal lockStateOut : objectLock := RELEASED;\n')
			f.write(f'\tsignal positionStateIn : singleSwitchStates := NORMAL;\n')
			f.write(f'\tsignal positionStateOut : singleSwitchStates := NORMAL;\n')
			f.write(f'\tsignal correspondenceState : singleSwitchStates := NORMAL;\n')

			f.write(f'begin\n')

			f.write(f'\tclock_in(0) <= clock;\r\n')
			f.write(f'\t-- Assign the last 2 bits of indication to lockState\n')
			f.write(f"\tlockStateIn <= objectLock'val(to_integer(unsigned(hex_to_slv(indication)(0 to 1))));\n")

			f.write(f'\t-- Assign the first 2 bits of indication to positionState\n')
			f.write(f"\tpositionStateIn <= singleSwitchStates'val(to_integer(unsigned(hex_to_slv(indication)(2 to 3))));\n")

			f.write(f'\t-- Update command based on the values of positionStateOut and lockStateOut\n')
			f.write(f"\tcommand <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(singleSwitchStates'pos(positionStateOut), 2)));\n")
			f.write(f'\t-- Update correspondence based on the values of correspondenceState and lockStateOut\n')
			f.write(f"\tcorrespondence <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(singleSwitchStates'pos(correspondenceState), 2)));\n")

			f.write(f'\tgen : for i in 0 to {FF-1} generate\r\n')
			f.write(f'\t\t inst: flipFlop port map(clock_in(i), restart, Q(i));\r\n')
			f.write(f'\t\tclock_in(i+1) <= Q(i);\r\n')
			f.write(f'\tend generate;\r\n')

			f.write(f'\n\tprocess(timeout,{route_cmd})\r\n')
			f.write(f'\tbegin\r\n')
			f.write(f'\t\tif (timeout = \'1\') then\r\n')
			f.write(f'\t\t\tcommandState <= RELEASE;\r\n')
			f.write(f'\t\telse\r\n')
			f.write(f'\t\t\tif ({freeState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= RELEASE;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\t\tif ({reserveState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= RESERVE;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\t\tif ({lockState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= LOCK;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\tend if;\r\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(timeout,commandState,positionStateIn,{route_cmd})\r\n')
			f.write(f'\tbegin\r\n')
			f.write(f'\t\tcase commandState is\r\n')
			f.write(f'\t\t\twhen RELEASE => -- AUTOMATIC\r\n')
			f.write(f'\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tlockStateOut <= RELEASED;\n')
			f.write(f'\t\t\twhen RESERVE =>\r\n')
			f.write(f'\t\t\t\tif (({reserveState_N}) and ({freeState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_N}) and ({reserveState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= RESERVED;\n')
			f.write(f'\t\t\twhen LOCK =>\r\n')
			f.write(f'\t\t\t\tif (({lockState_N}) and ({freeState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_N}) and ({lockState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\t\twhen others =>\r\n')
			f.write(f'\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\tend case;\r\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(clock,reset,Q,restart)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tif (reset = \'1\' or Q = "{timeout}") then\n')
			f.write(f'\t\t\ttimeout <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\t\tif (restart = \'1\') then\n')
			f.write(f'\t\t\ttimeout <= \'0\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\r\n') 
			
			f.write(f'\n\tprocess(timeout,positionStateOut,positionStateIn)\r\n')
			f.write(f'\tbegin\r\n')
			
			f.write(f'\t\tif (positionStateOut = NORMAL and positionStateIn = NORMAL) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= NORMAL;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')
			
			f.write(f'\t\tif (positionStateOut = REVERSE and positionStateIn = REVERSE) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= REVERSE;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\t\tif (positionStateOut /= positionStateIn) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= TRANSITION;\r\n')
			f.write(f'\t\t\trestart <= \'0\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\tend process;\r\n') 

			f.write(f'end Behavioral;') 
			f.close()  # Close header file

	def createDoubleSwitch(self,index,name,data,mode, f = None,example = 1):
		if mode == 'entity':
			node = f'doubleSwitch_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)
		
		doubleSwitch = f'doubleSwitch_{index}'
		f.write(f'\t{mode} {doubleSwitch} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
		f.write(f'\t\t\treset : in std_logic := \'0\';\n')

		commands = []
		commands_NN = []
		commands_RR = []
		commands_RN = []
		commands_NR = []
		for element in range(len(data['Routes'])):
			f.write(f'\t\t\t{data['Routes'][element]}_command : in routeCommands := RELEASE;\n')
			commands.append(data['Routes'][element])
			if data['Position'][element] == 'NN':
				commands_NN.append(data['Routes'][element])
			if data['Position'][element] == 'RR':
				commands_RR.append(data['Routes'][element])
			if data['Position'][element] == 'RN':
				commands_RN.append(data['Routes'][element])
			if data['Position'][element] == 'NR':
				commands_NR.append(data['Routes'][element])

		f.write(f'\t\t\tindication : in hex_char;\n')
		f.write(f'\t\t\tcommand : out hex_char;\n')
		f.write(f'\t\t\tcorrespondence : out hex_char\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {doubleSwitch};\n')

		if mode == 'entity':
			freeState = " and ".join([f'{i}_command = RELEASE' for i in commands])
			freeState_NN = " and ".join([f'{i}_command = RELEASE' for i in commands_NN])
			freeState_RR = " and ".join([f'{i}_command = RELEASE' for i in commands_RR])
			freeState_RN = " and ".join([f'{i}_command = RELEASE' for i in commands_RN])
			freeState_NR = " and ".join([f'{i}_command = RELEASE' for i in commands_NR])

			reserveState = " or ".join([f'{i}_command = RESERVE' for i in commands])
			reserveState_NN = " or ".join([f'{i}_command = RESERVE' for i in commands_NN])
			reserveState_RR = " or ".join([f'{i}_command = RESERVE' for i in commands_RR])
			reserveState_RN = " or ".join([f'{i}_command = RESERVE' for i in commands_RN])
			reserveState_NR = " or ".join([f'{i}_command = RESERVE' for i in commands_NR])

			lockState = " or ".join([f'{i}_command = LOCK' for i in commands])
			lockState_NN = " or ".join([f'{i}_command = LOCK' for i in commands_NN])
			lockState_RR = " or ".join([f'{i}_command = LOCK' for i in commands_RR])
			lockState_RN = " or ".join([f'{i}_command = LOCK' for i in commands_RN])
			lockState_NR = " or ".join([f'{i}_command = LOCK' for i in commands_NR])

			freq = 100e6
			timeout = 7

			FF = math.ceil(math.log2(timeout*freq))

			t = [(2**(i+1))/freq for i in range(FF)]
			sequence = [0]*FF
			total = 0
			for i in range(FF-1,-1,-1):
				if total + t[i] <= timeout:
					total += t[i]
					sequence[i] = 1
			timeout_stop = " and ".join([f'Q({i}) = \'{sequence[i]}\'' for i in range(FF)])
			timeout = '0'+"".join([f'{sequence[i]}' for i in range(FF)])[::-1]

			route_cmd = ",".join([f'{i}_command' for i in commands])

			f.write(f'architecture Behavioral of {node} is\n')

			f.write(f'\tcomponent flipFlop is\r\n')
			f.write(f'\t\tport(\r\n')
			f.write(f'\t\t\tclock : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\treset : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\tQ : out std_logic := \'0\'\r\n')
			f.write(f'\t\t);\r\n')
			f.write(f'\tend component flipFlop;\r\n')

			f.write(f'\tsignal restart : std_logic := \'1\';\n')
			f.write(f'\tsignal Q : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal clock_in : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal timeout : std_logic := \'0\';\n')

			f.write(f'\tsignal commandState : routeCommands := RELEASE;\r\n')
			
			f.write(f'\tsignal lockStateIn : objectLock := RELEASED;\n')
			f.write(f'\tsignal lockStateOut : objectLock := RELEASED;\n')

			f.write(f'\tsignal positionStateIn : doubleSwitchStates := DOUBLE_NORMAL;\n')
			f.write(f'\tsignal positionStateOut : doubleSwitchStates := DOUBLE_NORMAL;\n')
			f.write(f'\tsignal correspondenceState : doubleSwitchStates := DOUBLE_NORMAL;\n')

			f.write(f'begin\n')

			f.write(f'\tclock_in(0) <= clock;\r\n')
			f.write(f'\t-- Assign the last 2 bits of indication to lockState\n')
			f.write(f"\tlockStateIn <= objectLock'val(to_integer(unsigned(hex_to_slv(indication)(0 to 1))));\n")

			f.write(f'\t-- Assign the first 2 bits of indication to positionState\n')
			f.write(f"\tpositionStateIn <= doubleSwitchStates'val(to_integer(unsigned(hex_to_slv(indication)(2 to 3))));\n")

			f.write(f'\t-- Update command based on the values of positionStateOut and lockStateOut\n')
			f.write(f"\tcommand <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(doubleSwitchStates'pos(positionStateOut), 2)));\n")
			f.write(f'\t-- Update correspondence based on the values of correspondenceState and lockStateOut\n')
			f.write(f"\tcorrespondence <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(doubleSwitchStates'pos(correspondenceState), 2)));\n")

			f.write(f'\tgen : for i in 0 to {FF-1} generate\r\n')
			f.write(f'\t\t inst: flipFlop port map(clock_in(i), restart, Q(i));\r\n')
			f.write(f'\t\tclock_in(i+1) <= Q(i);\r\n')
			f.write(f'\tend generate;\r\n')

			f.write(f'\n\tprocess(timeout,{route_cmd})\r\n')
			f.write(f'\tbegin\r\n')
			f.write(f'\t\tif (timeout = \'1\') then\r\n')
			f.write(f'\t\t\tcommandState <= RELEASE;\r\n')
			f.write(f'\t\telse\r\n')
			f.write(f'\t\t\tif ({freeState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= RELEASE;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\t\tif ({reserveState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= RESERVE;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\t\tif ({lockState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= LOCK;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\tend if;\r\n')
			f.write(f'\tend process;\r\n')

			f.write(f'\n\tprocess(timeout,commandState,positionStateIn,{route_cmd})\r\n')
			f.write(f'\tbegin\r\n')
			f.write(f'\t\tcase commandState is\r\n')
			f.write(f'\t\t\twhen RELEASE => -- AUTOMATIC\r\n')
			f.write(f'\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tlockStateOut <= RELEASED;\n')
			f.write(f'\t\t\twhen RESERVE =>\r\n')
			f.write(f'\t\t\t\tif (({reserveState_NN}) and ({freeState_RR} and {freeState_RN} and {freeState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= DOUBLE_NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_NN}) and ({reserveState_RR}) and ({freeState_RN}) and ({freeState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= DOUBLE_REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_NN}) and ({freeState_RR}) and ({reserveState_RN}) and ({freeState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= REVERSE_NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_NN}) and ({freeState_RR}) and ({freeState_RN}) and ({reserveState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= NORMAL_REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= RESERVED;\n')

			f.write(f'\t\t\twhen LOCK =>\r\n')

			f.write(f'\t\t\t\tif (({lockState_NN}) and ({freeState_RR} and {freeState_RN} and {freeState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= DOUBLE_NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_NN}) and ({lockState_RR}) and ({freeState_RN}) and ({freeState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= DOUBLE_REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_NN}) and ({freeState_RR}) and ({lockState_RN}) and ({freeState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= REVERSE_NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_NN}) and ({freeState_RR}) and ({freeState_RN}) and ({lockState_NR})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= NORMAL_REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')

			f.write(f'\t\t\twhen others =>\r\n')
			f.write(f'\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\tend case;\r\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(clock,reset,Q,restart)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tif (reset = \'1\' or Q = "{timeout}") then\n')
			f.write(f'\t\t\ttimeout <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\t\tif (restart = \'1\') then\n')
			f.write(f'\t\t\ttimeout <= \'0\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(timeout,positionStateOut,positionStateIn)\r\n')
			f.write(f'\tbegin\r\n')
			
			f.write(f'\t\tif (positionStateOut = DOUBLE_NORMAL and positionStateIn = DOUBLE_NORMAL) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= DOUBLE_NORMAL;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')
			
			f.write(f'\t\tif (positionStateOut = DOUBLE_REVERSE and positionStateIn = DOUBLE_REVERSE) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= DOUBLE_REVERSE;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')
			
			f.write(f'\t\tif (positionStateOut = REVERSE_NORMAL and positionStateIn = REVERSE_NORMAL) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= REVERSE_NORMAL;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\t\tif (positionStateOut = NORMAL_REVERSE and positionStateIn = NORMAL_REVERSE) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= NORMAL_REVERSE;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\t\tif (positionStateOut /= positionStateIn) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= TRANSITION;\r\n')
			f.write(f'\t\t\trestart <= \'0\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\tend process;\r\n') 

			f.write(f'end Behavioral;') 
			f.close()  # Close header file			

	def createScissorCrossing(self,index,name,data,mode, f = None,example = 1):	
		if mode == 'entity':
			node = f'scissorCrossing_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)
		
		scissorCrossing = f'scissorCrossing_{index}'
		f.write(f'\t{mode} {scissorCrossing} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
		f.write(f'\t\t\treset : in std_logic := \'0\';\n')

		commands = []
		commands_N = []
		commands_R = []
		for element in range(len(data['Routes'])):
			f.write(f'\t\t\t{data['Routes'][element]}_command : in routeCommands := RELEASE;\n')
			commands.append(data['Routes'][element])
			if data['Position'][element] == 'N':
				commands_N.append(data['Routes'][element])
			else:
				commands_R.append(data['Routes'][element])	

		f.write(f'\t\t\tindication : in hex_char;\n')
		f.write(f'\t\t\tcommand : out hex_char;\n')
		f.write(f'\t\t\tcorrespondence : out hex_char\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {scissorCrossing};\n')

		if mode == 'entity':
			freeState = " and ".join([f'{i}_command = RELEASE' for i in commands])
			freeState_N = " and ".join([f'{i}_command = RELEASE' for i in commands_N])
			freeState_R = " and ".join([f'{i}_command = RELEASE' for i in commands_R])
			reserveState = " or ".join([f'{i}_command = RESERVE' for i in commands])
			reserveState_N = " or ".join([f'{i}_command = RESERVE' for i in commands_N])
			reserveState_R = " or ".join([f'{i}_command = RESERVE' for i in commands_R])
			lockState = " or ".join([f'{i}_command = LOCK' for i in commands])
			lockState_N = " or ".join([f'{i}_command = LOCK' for i in commands_N])
			lockState_R = " or ".join([f'{i}_command = LOCK' for i in commands_R])

			freq = 100e6
			timeout = 7

			FF = math.ceil(math.log2(timeout*freq))

			t = [(2**(i+1))/freq for i in range(FF)]
			sequence = [0]*FF
			total = 0
			for i in range(FF-1,-1,-1):
				if total + t[i] <= timeout:
					total += t[i]
					sequence[i] = 1
			timeout_stop = " and ".join([f'Q({i}) = \'{sequence[i]}\'' for i in range(FF)])
			timeout = '0'+"".join([f'{sequence[i]}' for i in range(FF)])[::-1]

			route_cmd = ",".join([f'{i}_command' for i in commands])

			f.write(f'architecture Behavioral of {node} is\n')

			f.write(f'\tcomponent flipFlop is\r\n')
			f.write(f'\t\tport(\r\n')
			f.write(f'\t\t\tclock : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\treset : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\tQ : out std_logic := \'0\'\r\n')
			f.write(f'\t\t);\r\n')
			f.write(f'\tend component flipFlop;\r\n')

			f.write(f'\tsignal restart : std_logic := \'1\';\n')
			f.write(f'\tsignal Q : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal clock_in : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal timeout : std_logic := \'0\';\n')

			f.write(f'\tsignal commandState : routeCommands := RELEASE;\r\n')
			
			f.write(f'\tsignal lockStateIn : objectLock := RELEASED;\n')
			f.write(f'\tsignal lockStateOut : objectLock := RELEASED;\n')
			f.write(f'\tsignal positionStateIn : scissorCrossingStates := NORMAL;\n')
			f.write(f'\tsignal positionStateOut : scissorCrossingStates := NORMAL;\n')
			f.write(f'\tsignal correspondenceState : scissorCrossingStates := NORMAL;\n')

			f.write(f'begin\n')

			f.write(f'\tclock_in(0) <= clock;\r\n')
			f.write(f'\t-- Assign the last 2 bits of indication to lockState\n')
			f.write(f"\tlockStateIn <= objectLock'val(to_integer(unsigned(hex_to_slv(indication)(0 to 1))));\n")

			f.write(f'\t-- Assign the first 2 bits of indication to positionState\n')
			f.write(f"\tpositionStateIn <= scissorCrossingStates'val(to_integer(unsigned(hex_to_slv(indication)(2 to 3))));\n")

			f.write(f'\t-- Update command based on the values of positionStateOut and lockStateOut\n')
			f.write(f"\tcommand <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(scissorCrossingStates'pos(positionStateOut), 2)));\n")
			f.write(f'\t-- Update correspondence based on the values of correspondenceState and lockStateOut\n')
			f.write(f"\tcorrespondence <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(scissorCrossingStates'pos(correspondenceState), 2)));\n")

			f.write(f'\tgen : for i in 0 to {FF-1} generate\r\n')
			f.write(f'\t\t inst: flipFlop port map(clock_in(i), restart, Q(i));\r\n')
			f.write(f'\t\tclock_in(i+1) <= Q(i);\r\n')
			f.write(f'\tend generate;\r\n')

			f.write(f'\n\tprocess(timeout,{route_cmd})\r\n')
			f.write(f'\tbegin\r\n')
			f.write(f'\t\tif (timeout = \'1\') then\r\n')
			f.write(f'\t\t\tcommandState <= RELEASE;\r\n')
			f.write(f'\t\telse\r\n')
			f.write(f'\t\t\tif ({freeState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= RELEASE;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\t\tif ({reserveState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= RESERVE;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\t\tif ({lockState}) then\r\n')
			f.write(f'\t\t\t\tcommandState <= LOCK;\r\n')
			f.write(f'\t\t\tend if;\r\n')
			f.write(f'\t\tend if;\r\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(timeout,commandState,positionStateIn,{route_cmd})\r\n')
			f.write(f'\tbegin\r\n')
			f.write(f'\t\tcase commandState is\r\n')
			f.write(f'\t\t\twhen RELEASE => -- AUTOMATIC\r\n')
			f.write(f'\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tlockStateOut <= RELEASED;\n')
			f.write(f'\t\t\twhen RESERVE =>\r\n')
			f.write(f'\t\t\t\tif (({reserveState_N}) and ({freeState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_N}) and ({reserveState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= RESERVED;\n')
			f.write(f'\t\t\twhen LOCK =>\r\n')
			f.write(f'\t\t\t\tif (({lockState_N}) and ({freeState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= NORMAL;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif (({freeState_N}) and ({lockState_R})) then\n')
			f.write(f'\t\t\t\t\tpositionStateOut <= REVERSE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\t\twhen others =>\r\n')
			f.write(f'\t\t\t\tpositionStateOut <= positionStateIn;\n')
			f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
			f.write(f'\t\tend case;\r\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(clock,reset,Q,restart)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tif (reset = \'1\' or Q = "{timeout}") then\n')
			f.write(f'\t\t\ttimeout <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\t\tif (restart = \'1\') then\n')
			f.write(f'\t\t\ttimeout <= \'0\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(timeout,positionStateOut,positionStateIn)\r\n')
			f.write(f'\tbegin\r\n')
			
			f.write(f'\t\tif (positionStateOut = NORMAL and positionStateIn = NORMAL) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= NORMAL;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')
			
			f.write(f'\t\tif (positionStateOut = REVERSE and positionStateIn = REVERSE) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= REVERSE;\r\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\t\tif (positionStateOut /= positionStateIn) then\r\n')
			f.write(f'\t\t\tcorrespondenceState <= TRANSITION;\r\n')
			f.write(f'\t\t\trestart <= \'0\';\r\n')
			f.write(f'\t\tend if;\r\n')

			f.write(f'\tend process;\r\n') 

			f.write(f'end Behavioral;') 
			f.close()  # Close header file

	def createSignal(self,index,name,data,futureRoute,mode, f = None,example = 1):
		if mode == 'entity':
			node = f'railwaySignal_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)
		
		railwaySignal = f'railwaySignal_{index}'
		f.write(f'\t{mode} {railwaySignal} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\treset : in std_logic;\n')

		commands = []
		if 'Routes' in data[name]:
			for element in range(len(data[name]['Routes'])):
				f.write(f'\t\t\t{data[name]['Routes'][element]}_command : in routeCommands;\n')
				commands.append(data[name]['Routes'][element])

		if name in futureRoute:
			for r in futureRoute[name]:
				f.write(f'\t\t\t{r}_command : in routeCommands;\n')
				commands.append(r)

		ocupationLevel_0,ocupationLevel_1,ocupationLevel_2,signal_0,signal_1,signal_2,switches_1,switches_2,paths = self.getSignalGraph(name,data)
		
		lc_string = []
		for path in paths:
			if 'LevelCrossings' in paths[path]:
				for i in paths[path]['LevelCrossings']:
					if i != [] and i not in lc_string:
						lc_string.append(i) 
		for i in lc_string:
			f.write(f'\t\t\t{i}_state : in hex_char;\r\n')

		f.write(f'\t\t\t--Ocupation level 0\n')	
		f.write(f'\t\t\ttrack_{ocupationLevel_0} : in hex_char;\n')	
		f.write(f'\t\t\tcorrespondence_{signal_0} : out hex_char;\n')

		sw_string_1 = []
		if len(ocupationLevel_1) > 0:
			f.write(f'\t\t\t--Ocupation level 1\n')	
			for i in ocupationLevel_1:
				if i != ocupationLevel_0:
					f.write(f'\t\t\ttrack_{i} : in hex_char;\n')	
		if len(signal_1) > 0:
			for j in signal_1:
				if j != signal_0:
					f.write(f'\t\t\tcorrespondence_{j} : in hex_char;\n')
		if len(switches_1) > 0:
			for k in switches_1:
				#switc_type = 'singleSwitchStates' if len(k.split('_')[1]) == 1 else ('doubleSwitchStates' if 'X' not in k.split('_')[1] else 'scissorCrossingStates')
				if f'\t\t\t{"s" if k[0].isdigit() else ""}{k.split('_')[0]}_state : in hex_char;\n' not in sw_string_1:
					sw_string_1.append(f'\t\t\t{"s" if k[0].isdigit() else ""}{k.split('_')[0]}_state : in hex_char;\n')
			for aux in sw_string_1:
				f.write(aux)

		sw_string_2 = []
		if len(ocupationLevel_2) > 0:
			f.write(f'\t\t\t--Ocupation level 2\n')	
			for i in ocupationLevel_2:
				if i != ocupationLevel_0 and i not in ocupationLevel_1:
					f.write(f'\t\t\ttrack_{i} : in hex_char;\n')	
		if len(signal_2) > 0:
			for j in signal_2:
				if j != signal_0 and j not in signal_1:
					f.write(f'\t\t\tcorrespondence_{j} : in hex_char;\n')
		if len(switches_2) > 0:
			for k in switches_2:
				#switc_type = 'singleSwitchStates' if len(k.split('_')[1]) == 1 else ('doubleSwitchStates' if 'X' not in k.split('_')[1] else 'scissorCrossingStates')
				if f'\t\t\t{"s" if k[0].isdigit() else ""}{k.split('_')[0]}_state : in hex_char;\n' not in sw_string_2:
					sw_string_2.append(f'\t\t\t{"s" if k[0].isdigit() else ""}{k.split('_')[0]}_state : in hex_char;\n')
			for aux in sw_string_2:
				if sw_string_1 == []:
					f.write(aux)
				else:	
					if aux not in sw_string_1:
						f.write(aux)

		f.write(f'\t\t\tindication : in hex_char;\n')
		f.write(f'\t\t\tcommand : out hex_char\n')
		
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {railwaySignal};\n')

		if mode == 'entity':
			print(f'{name}')
			for path in paths:
				print(f'\t{paths[path]}')	

			freeState = " and ".join([f'{i}_command = RELEASE' for i in commands])
			reserveState = " or ".join([f'{i}_command = RESERVE' for i in commands])
			lockState = " or ".join([f'{i}_command = LOCK' for i in commands])

			route_cmds = ",".join([f'{i}_command' for i in commands])

			freq = 100e6
			timeout = 7

			FF = math.ceil(math.log2(timeout*freq))

			t = [(2**(i+1))/freq for i in range(FF)]
			sequence = [0]*FF
			total = 0
			for i in range(FF-1,-1,-1):
				if total + t[i] <= timeout:
					total += t[i]
					sequence[i] = 1
			timeout_stop = " and ".join([f'Q({i}) = \'{sequence[i]}\'' for i in range(FF)])
			timeout = "".join([f'{sequence[i]}' for i in range(FF)])[::-1]

			f.write(f'architecture Behavioral of {node} is\n')

			f.write(f'\tcomponent flipFlop is\r\n')
			f.write(f'\t\tport(\r\n')
			f.write(f'\t\t\tclock : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\treset : in std_logic := \'0\';\r\n')
			f.write(f'\t\t\tQ : out std_logic := \'0\'\r\n')
			f.write(f'\t\t);\r\n')
			f.write(f'\tend component flipFlop;\r\n')

			f.write(f'\tsignal restart : std_logic := \'1\';\n')
			f.write(f'\tsignal Q : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal clock_in : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal timeout : std_logic := \'0\';\n')

			f.write(f'\tsignal commandState : routeCommands := RELEASE;\n')
			f.write(f'\tsignal lockStateIn : objectLock := RELEASED;\n')
			f.write(f'\tsignal lockStateOut : objectLock := RELEASED;\n')
			f.write(f'\tsignal aspectStateIn : signalStates := RED;\n')
			f.write(f'\tsignal aspectStateOut : signalStates := RED;\n')
			f.write(f'\tsignal correspondenceState : signalStates := RED;\n')

			f.write(f'\tsignal path : integer := 0;\n')
			
			lc_string = []
			for path in paths:
				if 'LevelCrossings' in paths[path]:
					for i in paths[path]['LevelCrossings']:
						if i != [] and i not in lc_string:
							lc_string.append(i) 
			for i in lc_string:
				f.write(f'\tsignal {i}_position : levelCrossingStates := UP;\n')	
				f.write(f'\tsignal {i}_lock : objectLock := RELEASED;\n')	

			sw_string_1A = []
			sw_string_1B = []
			if len(ocupationLevel_1) > 0:
				f.write(f'\t--Ocupation level 1\n')	
				for i in ocupationLevel_1:
					if i != ocupationLevel_0:
						f.write(f'\tsignal {i}_state : nodeStates := FREE;\n')	
						f.write(f'\tsignal {i}_lock : objectLock := RELEASED;\n')	
			if len(signal_1) > 0:
				for j in signal_1:
					if j != signal_0:
						f.write(f'\tsignal {j}_aspect : signalStates;\n')
						f.write(f'\tsignal {j}_lock : objectLock := RELEASED;\n')	
			if len(switches_1) > 0:
				for k in switches_1:
    					
					if len(k.split('_')[1]) == 1:
						type = 'singleSwitchStates'
						default = 'NORMAL'
					if len(k.split('_')[1]) == 2:
						if k.split('_')[1][0] == 'X':
							type = 'scissorCrossingStates'
							default = 'NORMAL'
						else:
							type = 'doubleSwitchStates'	
							default = 'DOUBLE_NORMAL'

					if f"\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_position : {type} := {default};\n" not in sw_string_1A:
						sw_string_1A.append(f"\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_position : {type} := {default};\n")
					if f'\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_lock : objectLock := RELEASED;\n' not in sw_string_1B:
						sw_string_1B.append(f'\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_lock : objectLock := RELEASED;\n')
				for aux in sw_string_1A:
					f.write(aux)
				for aux in sw_string_1B:
					f.write(aux)

			sw_string_2A = []
			sw_string_2B = []
			if len(ocupationLevel_2) > 0:
				f.write(f'\t--Ocupation level 2\n')	
				for i in ocupationLevel_2:
					if i != ocupationLevel_0 and i not in ocupationLevel_1:
						f.write(f'\tsignal {i}_state : nodeStates := FREE;\n')	
						f.write(f'\tsignal {i}_lock : objectLock := RELEASED;\n')	
			if len(signal_2) > 0:
				for j in signal_2:
					if j != signal_0 and j not in signal_1:
						f.write(f'\tsignal {j}_aspect : signalStates;\n')
						f.write(f'\tsignal {j}_lock : objectLock := RELEASED;\n')	
			if len(switches_2) > 0:
				for k in switches_2:
					if len(k.split('_')[1]) == 1:
						type = 'singleSwitchStates'
						default = 'NORMAL'
					if len(k.split('_')[1]) == 2:
						if k.split('_')[1][0] == 'X':
							type = 'scissorCrossingStates'
							default = 'NORMAL'
						else:
							type = 'doubleSwitchStates'	
							default = 'DOUBLE_NORMAL'
					if f"\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_position : {type} := {default};\n" not in sw_string_2A:
						sw_string_2A.append(f"\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_position : {type} := {default};\n")
					if f'\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_lock : objectLock := RELEASED;\n' not in sw_string_2B:
						sw_string_2B.append(f'\tsignal {"s" if k[0].isdigit() else ""}{k.split('_')[0]}_lock : objectLock := RELEASED;\n')
				for aux in sw_string_2A:
					if sw_string_1A == []:
						f.write(aux)
					else:	
						if aux not in sw_string_1A:
							f.write(aux)
				
				for aux in sw_string_2B:
					if sw_string_1B == []:
						f.write(aux)
					else:	
						if aux not in sw_string_1B:
							f.write(aux)

			f.write(f'begin\n')
			f.write(f'\tclock_in(0) <= clock;\r\n')

			f.write(f"\tlockStateIn <= objectLock'val(to_integer(unsigned(hex_to_slv(indication)(0 to 1))));\n")
			f.write(f"\taspectStateIn <= signalStates'val(to_integer(unsigned(hex_to_slv(indication)(2 to 3))));\n")

			f.write(f"\tcommand <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(signalStates'pos(aspectStateOut), 2)));\n")
			f.write(f"\tcorrespondence_{name} <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lockStateOut), 2) & to_unsigned(signalStates'pos(correspondenceState), 2)));\n")

			lc_string = []
			for path in paths:
				if 'LevelCrossings' in paths[path]:
					for i in paths[path]['LevelCrossings']:
						if i != [] and i not in lc_string:
							lc_string.append(i) 
			for i in lc_string:
				f.write(f"\t{i}_position <= levelCrossingStates'val(to_integer(unsigned(hex_to_slv({i}_state)(2 to 3))));\n")
				f.write(f"\t{i}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({i}_state)(0 to 1))));\n")
			sw_string_1A = []
			sw_string_1B = []
			if len(ocupationLevel_1) > 0:
				f.write(f'\t--Ocupation level 1\n')	
				for i in ocupationLevel_1:
					if i != ocupationLevel_0:
						f.write(f"\t{i}_state <= nodeStates'val(to_integer(unsigned(hex_to_slv(track_{i})(2 to 3))));\n")
						f.write(f"\t{i}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv(track_{i})(0 to 1))));\n")
			if len(signal_1) > 0:
				for j in signal_1:
					if j != signal_0:
						f.write(f"\t{j}_aspect <= signalStates'val(to_integer(unsigned(hex_to_slv(correspondence_{j})(2 to 3))));\n")
						f.write(f"\t{j}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv(correspondence_{j})(0 to 1))));\n")
			if len(switches_1) > 0:
				for k in switches_1:
					sw = f'{"s" if k[0].isdigit() else ""}{k.split('_')[0]}'
					if len(k.split('_')[1]) == 1:
						type = 'singleSwitchStates'
						default = 'NORMAL'
					if len(k.split('_')[1]) == 2:
						if k.split('_')[1][0] == 'X':
							type = 'scissorCrossingStates'
							default = 'NORMAL'
						else:
							type = 'doubleSwitchStates'	
							default = 'DOUBLE_NORMAL'
					condition1 = f"\t{sw}_position <= {type}'val(to_integer(unsigned(hex_to_slv({sw}_state)(2 to 3))));\n"
					condition2 = f"\t{sw}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({sw}_state)(0 to 1))));\n"
					if condition1 not in sw_string_1A:
						sw_string_1A.append(condition1)
					if condition2 not in sw_string_1B:
						sw_string_1B.append(condition2)
				for aux in sw_string_1A:
					f.write(aux)
				for aux in sw_string_1B:
					f.write(aux)

			sw_string_2A = []
			sw_string_2B = []
			if len(ocupationLevel_2) > 0:
				f.write(f'\t--Ocupation level 2\n')	
				for i in ocupationLevel_2:
					if i != ocupationLevel_0 and i not in ocupationLevel_1:
						f.write(f"\t{i}_state <= nodeStates'val(to_integer(unsigned(hex_to_slv(track_{i})(2 to 3))));\n")
						f.write(f"\t{i}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv(track_{i})(0 to 1))));\n")
			if len(signal_2) > 0:
				for j in signal_2:
					if j != signal_0 and j not in signal_1:
						f.write(f"\t{j}_aspect <= signalStates'val(to_integer(unsigned(hex_to_slv(correspondence_{j})(2 to 3))));\n")
						f.write(f"\t{j}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv(correspondence_{j})(0 to 1))));\n")
			if len(switches_2) > 0:
				for k in switches_2:
					sw = f'{"s" if k[0].isdigit() else ""}{k.split('_')[0]}'
					if len(k.split('_')[1]) == 1:
						type = 'singleSwitchStates'
						default = 'NORMAL'
					if len(k.split('_')[1]) == 2:
						if k.split('_')[1][0] == 'X':
							type = 'scissorCrossingStates'
							default = 'NORMAL'
						else:
							type = 'doubleSwitchStates'	
							default = 'DOUBLE_NORMAL'
					condition1 = f"\t{sw}_position <= {type}'val(to_integer(unsigned(hex_to_slv({sw}_state)(2 to 3))));\n"
					condition2 = f"\t{sw}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({sw}_state)(0 to 1))));\n"
					if condition1 not in sw_string_2A:
						sw_string_2A.append(condition1)
					if condition2 not in sw_string_2B:
						sw_string_2B.append(condition2)

				for aux in sw_string_2A:
					if sw_string_1A == []:
						f.write(aux)
					else:	
						if aux not in sw_string_1A:
							f.write(aux)
				
				for aux in sw_string_2B:
					if sw_string_1B == []:
						f.write(aux)
					else:	
						if aux not in sw_string_1B:
							f.write(aux)

			f.write(f'\tgen : for i in 0 to {FF-1} generate\n')
			f.write(f'\t\tinst: flipFlop port map(Q(i),restart,Q(i+1));\n')
			f.write(f'\tend generate;\n')

			if commands != []:
				f.write(f'\n\tprocess(timeout,{route_cmds})\n')
				f.write(f'\tbegin\n')

				f.write(f'\t\tif (timeout = \'1\') then\n')
				f.write(f'\t\t\tcommandState <= RELEASE;\n')
				f.write(f'\t\telse\n')
				f.write(f'\t\t\tif ({freeState}) then\n')
				f.write(f'\t\t\t\tcommandState <= RELEASE;\n')
				f.write(f'\t\t\tend if;\n')
				f.write(f'\t\t\tif ({reserveState}) then\n')
				f.write(f'\t\t\t\tcommandState <= RESERVE;\n')
				f.write(f'\t\t\tend if;\n')
				f.write(f'\t\t\tif ({lockState}) then\n')
				f.write(f'\t\t\t\tcommandState <= LOCK;\n')
				f.write(f'\t\t\tend if;\n')
				f.write(f'\t\tend if;\n')

				f.write(f'\tend process;\n') 

				f.write(f'\n\tprocess(commandState)\n')
				f.write(f'\tbegin\r\n')
				f.write(f'\t\tcase commandState is\n')
				f.write(f'\t\t\twhen RELEASE => -- AUTOMATIC\n')
				f.write(f'\t\t\t\tlockStateOut <= RELEASED;\n')
				f.write(f'\t\t\twhen RESERVE => -- DONT CHANGE\n')
				f.write(f'\t\t\t\tlockStateOut <= RESERVED;\n')
				f.write(f'\t\t\twhen LOCK => -- DONT CHANGE\n')
				f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
				f.write(f'\t\t\twhen others =>\n')
				f.write(f'\t\t\t\tlockStateOut <= LOCKED;\n')
				f.write(f'\t\tend case;\n')
				f.write(f'\tend process;\n') 
			else:
				f.write(f'\tlockStateOut <= RELEASED;\n')

			for path in paths:
				if 'Switches' in paths[path]:
					switches = ",".join(f'{"s" if x[0].isdigit() else ""}{x.split('_')[0]}_position' for x in paths[path]['Switches'])

			if paths != {}:
				f.write(f"\n\tprocess(commandState{',' if len(switches) > 0 else ''}{switches})\n")
				f.write(f'\tbegin\n')
				f.write(f'\t\tcase commandState is\n')
				f.write(f'\r\t\t\twhen RELEASE =>\n')

				sw_conditions = []
				lc_conditions = []
				sw_dict = {'N':'NORMAL','R':'REVERSE','NN':'DOUBLE_NORMAL','RR':'DOUBLE_REVERSE','RN':'REVERSE_NORMAL','NR':'NORMAL_REVERSE','XN':'NORMAL','XR':'REVERSE'}
				for path in paths:
					if 'Switches' in paths[path]:
						sw_conditions.append(" and ".join(f'{"s" if x[0].isdigit() else ""}{x.split('_')[0]}_position = {sw_dict[x.split('_')[1]]}' for x in paths[path]['Switches']))
				for path in paths:
					if 'LevelCrossings' in paths[path] and paths[path]['LevelCrossings'] != []:
						lc_conditions.append(" and ".join(f'{"s" if x[0].isdigit() else ""}{x}_position = DOWN' for x in paths[path]['LevelCrossings'] if x != None))
					else:
						lc_conditions.append(None)

				#f.write(f'{sw_conditions} {lc_conditions}\r\n')			

				main_conditions = [f"{x} and {y}" if x is not '' and y is not None else x or y for x, y in zip(sw_conditions, lc_conditions)]

				#f.write(f'{main_conditions}\r\n')

				if main_conditions != [None]:
					f.write(f'\t\t\t\tif ({" or ".join([f"({main_condition})" for main_condition in main_conditions])}) then\n')

					for condition in range(len(main_conditions)):	
						conditions = main_conditions[condition]
						#if 'LevelCrossings' in paths[sw_condition+1] and paths[sw_condition+1]['LevelCrossings'] != []:
						#	lc_condition = " and ".join(f'{x}_state = DOWN' for x in paths[sw_condition+1]['LevelCrossings'] if x != [])
						#	conditions = conditions + f' and ({lc_condition})'	
							
						f.write(f'\t\t\t\t\tif ({conditions}) then\n')
						f.write(f'\t\t\t\t\t\tpath <= {condition+1};\n')
						f.write(f'\t\t\t\t\tend if;\n')		
				else:
					f.write(f'\t\t\t\tpath <= 1;\n')

				if main_conditions != [None]:
					f.write(f'\t\t\t\telse\n')
					f.write(f'\t\t\t\t\tpath <= 0;\n')
					f.write(f'\t\t\t\tend if;\n')

				f.write(f'\r\t\t\twhen RESERVE =>\n')
				f.write(f'\t\t\t\tpath <= {len(main_conditions)+1};\n')		
				f.write(f'\r\t\t\twhen LOCK =>\n')
				f.write(f'\t\t\t\tpath <= 0;\n')		
				f.write(f'\r\t\t\twhen others =>\n')
				f.write(f'\t\t\t\tpath <= 0;\n')
				f.write(f'\t\tend case;\n')
				f.write(f'\tend process;\n') 
			else:
				if name[0] == 'T':
					f.write(f'\taspectStateOut <= RED;\n')
				if name[0] == 'L':
					f.write(f'\taspectStateOut <= DOUBLE_YELLOW;\n')
			
			if paths != {}:
    				
				occupation = ",".join([f"{occ}_state" for occ in ocupationLevel_1])
				signals = ",".join([f"{sig}_aspect" for sig in signal_1])

				extra = [occupation,signals]
				extra_connected = ",".join([f"{ext}" for ext in extra if ext])

				#f.write(f'-- {ocupationLevel_1} {signal_1} {extra} {extra_connected}\n')
				f.write(f'\n\tprocess(path,{extra_connected})\n')
				f.write(f'\tbegin\n')

				f.write(f'\t\tcase path is\n')
				f.write(f'\t\t\twhen 0 =>\n')
				f.write(f'\t\t\t\taspectStateOut <= RED;\r\n')
				for i in range(len(paths)):
					f.write(f'\t\t\twhen {i+1} =>\n')
					signal_dict = {'RED':'DOUBLE_YELLOW','DOUBLE_YELLOW':'YELLOW','YELLOW':'GREEN','GREEN':'GREEN'}
					if not paths[path]['Share']:
						conditions = " or ".join(f'{x}_state = OCCUPIED or {x}_lock = LOCKED'  for x in paths[i+1]['FirstPath'])
						f.write(f'\t\t\t\tif ({conditions}) then\n')
						f.write(f'\t\t\t\t\taspectStateOut <= RED;\n')
						f.write(f'\t\t\t\telse\n')

						for j in signal_dict:
							f.write(f'\t\t\t\t\tif ({paths[i+1]['Signals'][1]}_aspect = {j}) then\n')
							f.write(f'\t\t\t\t\t\taspectStateOut <= {signal_dict[j]};\n')
							f.write(f'\t\t\t\t\tend if;\n')
					
						f.write(f'\t\t\t\tend if;\n')
					else:
						for j in signal_dict:
							f.write(f'\t\t\t\tif ({paths[i+1]['Signals'][1]}_aspect = {j}) then\n')
							f.write(f'\t\t\t\t\taspectStateOut <= {signal_dict[j]};\n')
							f.write(f'\t\t\t\tend if;\n')

				f.write(f'\t\t\twhen {len(paths)+1} =>\n')
				f.write(f'\t\t\t\taspectStateOut <= GREEN;\r\n')
				f.write(f'\t\t\twhen others =>\n')
				f.write(f'\t\t\t\taspectStateOut <= RED;\n')
				f.write(f'\t\tend case;\n')
				f.write(f'\tend process;\n') 
			
			f.write(f'\n\tprocess(clock,reset,Q,restart)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tif (reset = \'1\' or Q = "{timeout}") then\n')
			f.write(f'\t\t\ttimeout <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\t\tif (restart = \'1\') then\n')
			f.write(f'\t\t\ttimeout <= \'0\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'\n\tprocess(timeout,aspectStateOut,aspectStateIn)\n')
			f.write(f'\tbegin\n')
		
			f.write(f'\t\tif(aspectStateOut = RED and aspectStateIn = RED) then\n')
			f.write(f'\t\t\tcorrespondenceState <= RED;\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\n')

			f.write(f'\t\tif(aspectStateOut = GREEN and aspectStateIn = GREEN) then\n')
			f.write(f'\t\t\tcorrespondenceState <= GREEN;\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\n')

			f.write(f'\t\tif(aspectStateOut = DOUBLE_YELLOW and aspectStateIn = DOUBLE_YELLOW) then\n')
			f.write(f'\t\t\tcorrespondenceState <= DOUBLE_YELLOW;\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\n')

			f.write(f'\t\tif(aspectStateOut = YELLOW and aspectStateIn = YELLOW) then\n')
			f.write(f'\t\t\tcorrespondenceState <= YELLOW;\n')
			f.write(f'\t\t\trestart <= \'1\';\r\n')
			f.write(f'\t\tend if;\n')

			f.write(f'\tend process;\n')  
			
			f.write(f'end Behavioral;') 
			f.close()  # Close header file
		
	def getSignalGraph(self,name,data):
		ocupationLevel_0 = data[name]['Start']
		signal_0 = name

		paths = {}
		ocupationLevel_1 = []
		subLevel_order = []
		signal_1 = []
		switches_1 = []
		sub_switch_order = []
		# level 1
		if 'Path' in data[name]:
			subLevel = [item for sublist in data[name]['Path'] for item in sublist]
			for item in subLevel:
				if item not in subLevel_order:
					subLevel_order.append(item)
			for i in subLevel_order:
				if i not in ocupationLevel_1:
					ocupationLevel_1.append(i)
			for j in data[name]['Next']:
				if j not in signal_1:
					signal_1.append(j)

			sub_switch = [item for sublist in data[name]['Switches'] for item in sublist]	

			path = 0
			if data[name]['Switches'] != []:
				for i in range(len(data[name]['Switches'])):
					if 'Next' in data[name]:
						next = data[name]['Next'][i]
						net = data[name]['Path'][i]
		
						if 'Switches' in data[next] and data[next]['Switches'] != []:
							for j in range(len(data[next]['Switches'])):
								path = path + 1
								#print(f'{path} {data[name]['Switches'][i]} {data[next]['Switches'][j]}')
								paths[path] = {'Switches':[],'Path':[],'LevelCrossings':[],'Signals':[]}
								for k in data[name]['Switches'][i]:
									paths[path]['Switches'].append(k)
								paths[path]['Path'].append(data[name]['Start'])
								paths[path]['Signals'].append(signal_0)
								paths[path]['Signals'].append(next)
								paths[path]['Signals'].append(data[next]['Next'][j])
					
								for k in net:
									paths[path]['Path'].append(k)
								for k in data[next]['Switches'][j]:
									paths[path]['Switches'].append(k)

								if 'LevelCrossings' in data[name]:
									for k in data[name]['LevelCrossings'][i]:
										if k != []:
											paths[path]['LevelCrossings'].append(k)

								for k in data[next]['Path'][j]:
									paths[path]['Path'].append(k)
						else:
							path = path +1
							#print(f'{path} {data[name]['Switches'][i]}')
							paths[path] = {'Switches':[],'Path':[],'LevelCrossings':[],'Signals':[]}
							for k in data[name]['Switches'][i]:
								paths[path]['Switches'].append(k)
							paths[path]['Path'].append(data[name]['Start'])
							paths[path]['Signals'].append(signal_0)
							paths[path]['Signals'].append(next)
							
							if 'Next' in data[next]:
								paths[path]['Signals'].append(data[next]['Next'][0])
							
							if 'LevelCrossings' in data[name]:
								for k in data[name]['LevelCrossings']:
									for n in k:
										if n != []:
											paths[path]['LevelCrossings'].append(n)

							if 'LevelCrossings' in data[next]:
								for k in data[next]['LevelCrossings']:
									for n in k:
										if n != []:
											paths[path]['LevelCrossings'].append(n)

							for k in net:
								paths[path]['Path'].append(k)
			else:
				if 'Next' in data[name]:
					path = path + 1		
					paths[path] = {'Switches':[],'Path':[],'LevelCrossings':[],'Signals':[]}
					
					next = data[name]['Next'][0]
					
					paths[path]['Path'].append(data[name]['Start'])
					for i in data[name]['Path']:
						for j in i:
							if j != []:
								paths[path]['Path'].append(j)

					if 'LevelCrossings' in data[name]:
						for i in data[name]['LevelCrossings'][0]:
							if i != []:
								paths[path]['LevelCrossings'].append(i)

					paths[path]['Signals'].append(name)
					paths[path]['Signals'].append(next)
					
					if 'Switches' in data[next]:
						for i in range(len(data[next]['Switches'])):
							paths[path+i] = paths[path]	
							paths[path+i]['Signals'].append(data[next]['Next'][i])
							for j in data[next]['Switches'][i]:
								paths[path+i]['Switches'].append(j)
							for j in data[next]['Path'][i]:
								paths[path+i]['Path'].append(j)
							for j in data[next]['LevelCrossings'][i]:
								paths[path+i]['LevelCrossings'].append(j)
					
			for item in sub_switch:
				if item not in sub_switch_order:
					sub_switch_order.append(item)
			for i in sub_switch_order:
				if i not in switches_1:
					switches_1.append(i)

		for path in paths:
			if 'Path' in paths[path]:
				if paths[path]['Path'][0] == data[paths[path]['Signals'][1]]['Start']:
					paths[path]['Share'] = True
				else:
					paths[path]['Share'] = False
					fullPath = paths[path]['Path'][1:]
					stop = data[paths[path]['Signals'][1]]['Start']
							
					firstPath = [j for j in fullPath if (fullPath.index(j) <= fullPath.index(stop) if stop in fullPath else len(fullPath))]
					secondPath = [j for j in fullPath if (fullPath.index(j) > fullPath.index(stop) if stop in fullPath else len(fullPath))]

					paths[path]['FirstPath'] = firstPath
					paths[path]['SecondPath'] = secondPath
			

		#print(f'{name}')
		#for path in paths:
		#	print(f'\t{path} {paths[path]}')	

		ocupationLevel_2 = []
		signal_2 = []
		switches_2 = []
		sub_switch_order = []
		# level 2
		if 'Next' in data[name]:
			for next in data[name]['Next']:
				if data[next]['Start'] not in ocupationLevel_2:
					ocupationLevel_2.append(data[next]['Start'])
				if 'Path' in data[next]:
					sub_level = list(set([item for sublist in data[next]['Path'] for item in sublist]))
					for i in sub_level:
						if i not in ocupationLevel_2:
							ocupationLevel_2.append(i)
					for j in data[next]['Next']:
						if j not in signal_2:
							signal_2.append(j)

				if 'Switches' in data[next]:
					sub_switch = [item for sublist in data[next]['Switches'] for item in sublist]	
					for item in sub_switch:
						if item not in sub_switch_order:
							sub_switch_order.append(item)
					for i in sub_switch_order:
						if i not in switches_2:
							switches_2.append(i)

		#print(f'{name} {ocupationLevel_0} {[i for i in ocupationLevel_1 if i not in ocupationLevel_0]} {[i for i in ocupationLevel_2 if i not in ocupationLevel_1 if i != ocupationLevel_0]} | {signal_0} {signal_1} {signal_2} | {switches_1} {switches_2}')	
							
		return ocupationLevel_0,[i for i in ocupationLevel_1 if i != ocupationLevel_0],[i for i in ocupationLevel_2 if i not in ocupationLevel_1],signal_0,signal_1,signal_2,switches_1,switches_2,paths

	def createNode(self,index,nodeId,routes,mode, f = None,example = 1):
		if mode == 'entity':
			node = f'node_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)
		
		node = f'node_{index}'
		f.write(f'\t{mode} {node} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\treset : in std_logic;\n')
		f.write(f'\t\t\ttrack_i : in hex_char;\n')
		
		commands = []
		for route in routes:
			if nodeId in routes[route]['Path']:
				f.write(f'\t\t\tR{route}_command : in routeCommands;\n')	
				commands.append(f'R{route}')

		f.write(f'\t\t\ttrack_o : out hex_char\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {node};\n')

		if mode == 'entity':
			freeState = " and ".join([f'{i}_command = RELEASE' for i in commands])
			reserveState = " or ".join([f'{i}_command = RESERVE' for i in commands])
			lockState = " or ".join([f'{i}_command = LOCK' for i in commands])

			f.write(f'architecture Behavioral of {node} is\n')

			f.write(f'\tsignal commandState : routeCommands := RELEASE;\n')
			f.write(f'\tsignal lock_state : objectLock := RELEASED;\n')
			f.write(f'\tsignal track_state : nodeStates := FREE;\n')

			f.write(f'begin\n')

			f.write(f'\t-- Assign the last 2 bits of track_i to lock_state\n')
			f.write(f"\t--lock_state <= objectLock'val(to_integer(unsigned(hex_to_slv(track_i)(0 to 1))));\n")

			f.write(f'\t-- Assign the first 2 bits of track_i to track_state\n')
			f.write(f"\ttrack_state <= nodeStates'val(to_integer(unsigned(hex_to_slv(track_i)(2 to 3))));\n")

			f.write(f'\t-- Update track_i based on the values of track_state and lock_state\n')
			f.write(f"\ttrack_o <= slv_to_hex(std_logic_vector(to_unsigned(objectLock'pos(lock_state), 2) & to_unsigned(nodeStates'pos(track_state), 2)));\n")

			route_cmd = ",".join([f'{i}_command' for i in commands])

			f.write(f'\n\tprocess(reset,{route_cmd})\n')
			f.write(f'\tbegin\n')
	
			f.write(f'\t\tif (reset = \'1\') then\n')
			f.write(f'\t\t\tcommandState <= RELEASE;\n')
			f.write(f'\t\telse\n')
			f.write(f'\t\t\tif ({freeState}) then\n')
			f.write(f'\t\t\t\tcommandState <= RELEASE;\n')
			f.write(f'\t\t\telse\n')
			f.write(f'\t\t\t\tif ({reserveState}) then\n')
			f.write(f'\t\t\t\t\tcommandState <= RESERVE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif ({lockState}) then\n')
			f.write(f'\t\t\t\t\tcommandState <= LOCK;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\tend if;\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\n') 

			f.write(f'\n\tprocess(commandState)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tcase commandState is\n')
			f.write(f'\r\t\t\twhen RELEASE => -- AUTOMATIC\n')
			f.write(f'\t\t\t\tlock_state <= RELEASED;\n')
			f.write(f'\r\t\t\twhen RESERVE => -- DONT CHANGE\n')
			f.write(f'\t\t\t\tlock_state <= RESERVED;\n')
			f.write(f'\r\t\t\twhen LOCK => -- DONT CHANGE\n')
			f.write(f'\t\t\t\tlock_state <= LOCKED;\n')
			f.write(f'\r\t\t\twhen others =>\n')
			f.write(f'\t\t\t\tlock_state <= LOCKED;\n')
			f.write(f'\t\tend case;\n')
			f.write(f'\tend process;\n') 

			f.write(f'end Behavioral;') 
			f.close()  # Close header file

	def createRoute(self,index,route,levelCrossingData,singleSwitchData,doubleSwitchData,scissorCrossingData,mode, f = None,example = 1):
		
		# End signals should be commanded by routes also	
		
		if mode == 'entity':
			node = f'route_{index}'
			f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
			
			# Initial comment
			self.initialComment(node,f)
			
			# Include library
			self.includeLibrary(f,True)
		
		sw_list = [key for key, value in singleSwitchData.items() if f'R{index+1}' in value['Routes']]
		dw_list = [key for key, value in doubleSwitchData.items() if f'R{index+1}' in value['Routes']]		
		sc_list = [key for key, value in scissorCrossingData.items() if f'R{index+1}' in value['Routes']]
		lc_list = [key for key, value in levelCrossingData.items() if f'R{index+1}' in value['Routes']]

		f.write(f'--sw  R{index+1} {sw_list} \r\n')	
		f.write(f'--dw  R{index+1} {dw_list} \r\n')	
		f.write(f'--sc  R{index+1} {sc_list} \r\n')	
		f.write(f'--lc  R{index+1} {lc_list} \r\n')

		node = f'route_{index}'
		f.write(f'\t{mode} {node} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
		f.write(f'\t\t\treset : in std_logic := \'0\';\n')
		f.write(f'\t\t\trouteRequest : in hex_char;\n')
	
		for netElement in route['Path']:
			f.write(f'\t\t\ttrack_{netElement} : in hex_char;\n')
			f.write(f'\t\t\t{netElement}_command : out routeCommands := RELEASE;\n')	

		for levelCrossing in lc_list:
			if levelCrossing != None:
				f.write(f'\t\t\t{levelCrossing}_state : in hex_char;\n')
				f.write(f'\t\t\t{levelCrossing}_command : out routeCommands := RELEASE;\n')

		for switch in sw_list:
			if switch != None:
				f.write(f'\t\t\t{"s" if switch[0].isdigit() else ""}{switch}_state : in hex_char;\n')
				f.write(f'\t\t\t{"s" if switch[0].isdigit() else ""}{switch}_command : out routeCommands := RELEASE;\n')

		for dswitch in dw_list:
			if dswitch != None:
				f.write(f'\t\t\t{"s" if dswitch[0].isdigit() else ""}{dswitch}_state : in hex_char;\n')
				f.write(f'\t\t\t{"s" if dswitch[0].isdigit() else ""}{dswitch}_command : out routeCommands := RELEASE;\n')

		for scissorCrossing in sc_list:
			scissor_aux = scissorCrossing.split('_')
			f.write(f'\t\t\t{"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_state : in hex_char;\n')
			f.write(f'\t\t\t{"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_command : out routeCommands := RELEASE;\n')	

		f.write(f'\t\t\t{route['Start']}_state : in hex_char;\n')
		f.write(f'\t\t\t{route['Start']}_command : out routeCommands := RELEASE;\n')	

		f.write(f'\t\t\t{route['End']}_state : in hex_char;\n')
		f.write(f'\t\t\t{route['End']}_command : out routeCommands := RELEASE;\n')

		f.write(f'\t\t\trouteExecute : out hex_char\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend {mode} {node};\n')

		if mode == 'entity':
			releasedLocks = " and ".join([f'{i}_lock = RELEASED' for i in route['Path']])
			freeStates = " and ".join([f'{i}_state = FREE' for i in route['Path'][1:]])
			
			reservedLocks = " and ".join([f'{i}_lock = RESERVED' for i in route['Path']])
			lockedLocks = " and ".join([f'{i}_lock = LOCKED' for i in route['Path']])

			reserveState = " or ".join([f'{i}_state = RESERVE' for i in route['Path']])
			lockState = " or ".join([f'{i}_state = LOCK' for i in route['Path']])
				
			freq = 100e6
			timeout = 30

			FF = math.ceil(math.log2(timeout*freq))

			t = [(2**(i+1))/freq for i in range(FF)]
			sequence = [0]*FF
			total = 0
			for i in range(FF-1,-1,-1):
				if total + t[i] <= timeout:
					total += t[i]
					sequence[i] = 1
			timeout_stop = " and ".join([f'Q({i}) = \'{sequence[i]}\'' for i in range(FF)])
			timeout = ''.join(map(str, sequence[::-1]))+'0'

			f.write(f'architecture Behavioral of {node} is\n')
			f.write(f'\tcomponent flipFlop is\n')
			f.write(f'\t\tport(\n')
			f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
			f.write(f'\t\t\treset : in std_logic := \'0\';\n')
			f.write(f'\t\t\tQ : out std_logic := \'0\'\n')
			f.write(f'\t\t);\n')
			f.write(f'\tend component flipFlop;\r\n')

			#routeStates is (WAITING_COMMAND,RESERVING_TRACKS,LOCKING_TRACKS,RESERVING_INFRASTRUCTURE,LOCKING_INFRASTRUCTURE,DRIVING_SIGNAL,SEQUENCIAL_RELEASE,RELEASING_INFRASTRUCTURE,RELEASING_TRACKS);\r\n')

			f.write(f'\tsignal restart : std_logic := \'1\';\n')
			f.write(f'\tsignal Q : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal clock_in : std_logic_vector({FF} downto 0) := (others => \'0\');\n')
			f.write(f'\tsignal timeout : std_logic := \'0\';\n')
			
			f.write(f'\tsignal routeState : routeStates := WAITING_COMMAND;\n')
			f.write(f'\tsignal routingIn : routeStates;\n')
			#f.write(f'\tsignal routeOutput : routeCommands := RELEASE;\n')

			f.write(f'\tsignal {" , ".join([f'{i}_used' for i in route['Path']])} : std_logic := \'0\';\n')

			for netElement in route['Path']:
				f.write(f'\tsignal {netElement}_state : nodeStates := FREE;\n')	
				f.write(f'\tsignal {netElement}_lock : objectLock := RELEASED;\n')	
			for levelCrossing in lc_list:
				if levelCrossing != None:
					f.write(f'\tsignal {levelCrossing}_position : levelCrossingStates := UP;\n')
					f.write(f'\tsignal {levelCrossing}_lock : objectLock := RELEASED;\n')
			for switch in sw_list:
				if switch != None:
					f.write(f'\tsignal {"s" if switch[0][0].isdigit() else ""}{switch}_position : singleSwitchStates := NORMAL;\n')
					f.write(f'\tsignal {"s" if switch[0][0].isdigit() else ""}{switch}_lock : objectLock := RELEASED;\n')
			for dswitch in dw_list:
				if dswitch != None:
					f.write(f'\tsignal {"s" if dswitch[0][0].isdigit() else ""}{dswitch}_position : doubleSwitchStates := DOUBLE_NORMAL;\n')
					f.write(f'\tsignal {"s" if dswitch[0][0].isdigit() else ""}{dswitch}_lock : objectLock := RELEASED;\n')
			for scissorCrossing in sc_list:
				scissor_aux = scissorCrossing.split('_')
				f.write(f'\tsignal {"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_position : scissorCrossingStates := NORMAL;\n')
				f.write(f'\tsignal {"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_lock : objectLock := RELEASED;\n')	

			f.write(f'\tsignal {route['Start']}_aspectIn : signalStates := RED;\n')
			f.write(f'\tsignal {route['Start']}_lock: objectLock := RELEASED;\n')	

			f.write(f'\tsignal {route['End']}_aspectIn : signalStates := RED;\n')
			f.write(f'\tsignal {route['End']}_lock : objectLock := RELEASED;\n')
			
			f.write(f'begin\n')

			f.write(f'\tclock_in(0) <= clock;\r\n')
			
			f.write(f"\troutingIn <= routeStates'val(to_integer(unsigned(hex_to_slv(routeRequest))));\n")
			f.write(f"\trouteExecute <= slv_to_hex(std_logic_vector(to_unsigned(routeStates'pos(routeState),4)));\n")

			for netElement in route['Path']:
				f.write(f"\t{netElement}_state <= nodeStates'val(to_integer(unsigned(hex_to_slv(track_{netElement})(2 to 3))));\n")
				f.write(f"\t{netElement}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv(track_{netElement})(0 to 1))));\n")
			for levelCrossing in lc_list:
				if levelCrossing != None:
					f.write(f"\t{levelCrossing}_position <= levelCrossingStates'val(to_integer(unsigned(hex_to_slv({levelCrossing}_state)(2 to 3))));\n")
					f.write(f"\t{levelCrossing}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({levelCrossing}_state)(0 to 1))));\n")
	
			for switch in sw_list:
				if switch != None:
					f.write(f"\t{"s" if switch[0][0].isdigit() else ""}{switch}_position <= singleSwitchStates'val(to_integer(unsigned(hex_to_slv({"s" if switch[0][0].isdigit() else ""}{switch}_state)(2 to 3))));\n")
					f.write(f"\t{"s" if switch[0][0].isdigit() else ""}{switch}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({"s" if switch[0][0].isdigit() else ""}{switch}_state)(0 to 1))));\n")

			for dswitch in dw_list:
				if dswitch != None:
					f.write(f"\t{"s" if dswitch[0][0].isdigit() else ""}{dswitch}_position <= doubleSwitchStates'val(to_integer(unsigned(hex_to_slv({"s" if dswitch[0][0].isdigit() else ""}{dswitch}_state)(2 to 3))));\n")
					f.write(f"\t{"s" if dswitch[0][0].isdigit() else ""}{dswitch}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({"s" if dswitch[0][0].isdigit() else ""}{dswitch}_state)(0 to 1))));\n")

			for scissorCrossing in sc_list:
				scissor_aux = scissorCrossing.split('_')
				f.write(f"\t{"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_position <= scissorCrossingStates'val(to_integer(unsigned(hex_to_slv({"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_state)(2 to 3))));\n")
				f.write(f"\t{"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({"s" if scissor_aux[0][0].isdigit() else ""}{scissor_aux[0]}_state)(0 to 1))));\n")

			f.write(f"\t{route['Start']}_aspectIn <= signalStates'val(to_integer(unsigned(hex_to_slv({route['Start']}_state)(2 to 3))));\n")
			f.write(f"\t{route['Start']}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({route['Start']}_state)(0 to 1))));\n")

			f.write(f"\t{route['End']}_aspectIn <= signalStates'val(to_integer(unsigned(hex_to_slv({route['End']}_state)(2 to 3))));\n")
			f.write(f"\t{route['End']}_lock <= objectLock'val(to_integer(unsigned(hex_to_slv({route['End']}_state)(0 to 1))));\n")

			f.write(f'\tgen : for i in 0 to {FF-1} generate\r\n')
			f.write(f'\t\t inst: flipFlop port map(clock_in(i), restart, Q(i));\r\n')
			f.write(f'\t\tclock_in(i+1) <= Q(i);\r\n')
			f.write(f'\tend generate;\r\n')

			nets_state = ",".join([f'{net}_state' for net in route['Path']])
			nets_lock = ",".join([f'{net}_lock' for net in route['Path']])

			sws_lock = ",".join([f'{"s" if sw[0][0].isdigit() else ""}{sw}_lock' for sw in sw_list])
			dws_lock = ",".join([f'{"s" if dw[0][0].isdigit() else ""}{dw}_lock' for dw in dw_list])
			scs_lock = ",".join([f'{"s" if sc[0][0].isdigit() else ""}{sc}_lock' for sc in sc_list])
			lcs_lock = ",".join([f'{lc}_lock' for lc in lc_list])

			infra = [nets_state,nets_lock,sws_lock,dws_lock,scs_lock,lcs_lock]
			infras = ",".join([f'{inf}' for inf in infra if inf])

			f.write(f'\n\tprocess(clock,reset,Q,restart)\n')
			f.write(f'\tbegin\n')
			f.write(f'\t\tif (reset = \'1\' or Q = "{timeout}") then\n')
			f.write(f'\t\t\ttimeout <= \'1\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\t\tif (restart = \'1\') then\n')
			f.write(f'\t\t\ttimeout <= \'0\';\n')
			f.write(f'\t\tend if;\n')
			f.write(f'\tend process;\r\n') 

			#f.write(f'\n\tprocess(routingIn,routeState,{infras})\n')
			f.write(f'\n\tprocess(clock)\n')
			f.write(f'\tbegin\n')
	
			f.write(f'\tif (clock\'Event and clock = \'1\') then\n')

			f.write(f'\t\tcase routeState is\n')

			f.write(f'\r\t\t\twhen WAITING_COMMAND =>\n')
			f.write(f'\t\t\t\tif (routingIn = ROUTE_REQUEST) then\n')
			f.write(f'\t\t\t\t\trouteState <= RESERVING_TRACKS;\n')
			f.write(f'\t\t\t\tend if;\n')

			f.write(f'\r\t\t\twhen RESERVING_TRACKS =>\n')
			f.write(f'\t\t\t\trestart <= \'0\';\n')
			f.write(f'\t\t\t\tif (routingIn = CANCEL_ROUTE or timeout =\'1\') then\n')
			f.write(f'\t\t\t\t\trouteState <= CANCEL_ROUTE;\n')
			f.write(f'\t\t\t\tend if;\n')

			if freeStates != '':
				f.write(f'\t\t\t\tif (({releasedLocks}) and ({freeStates})) then\n')
			else:
				f.write(f'\t\t\t\tif ({releasedLocks}) then\n')

			for net in route['Path']:
				f.write(f'\t\t\t\t\t{net}_command <= RESERVE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif ({reservedLocks})then\n')
			f.write(f'\t\t\t\t\trestart <= \'1\';\n')
			f.write(f'\t\t\t\t\trouteState <= LOCKING_TRACKS;\n')
			f.write(f'\t\t\t\tend if;\n')

			f.write(f'\r\t\t\twhen LOCKING_TRACKS =>\n')
			f.write(f'\t\t\t\trestart <= \'0\';\n')
			f.write(f'\t\t\t\tif (routingIn = CANCEL_ROUTE or timeout =\'1\') then\n')
			f.write(f'\t\t\t\t\trouteState <= CANCEL_ROUTE;\n')
			f.write(f'\t\t\t\tend if;\n')
			if freeStates != '':
				f.write(f'\t\t\t\tif (({reservedLocks}) and ({freeStates})) then\n')
			else:
				f.write(f'\t\t\t\tif ({reservedLocks}) then\n')

			for net in route['Path']:
				f.write(f'\t\t\t\t\t{net}_command <= LOCK;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\tif ({lockedLocks})then\n')
			f.write(f'\t\t\t\t\trestart <= \'1\';\n')
			f.write(f'\t\t\t\t\trouteState <= RESERVING_INFRASTRUCTURE;\n')
			f.write(f'\t\t\t\tend if;\n')

			f.write(f'\r\t\t\twhen RESERVING_INFRASTRUCTURE =>\n')
			f.write(f'\t\t\t\trestart <= \'0\';\n')
			f.write(f'\t\t\t\tif (routingIn = CANCEL_ROUTE or timeout =\'1\') then\n')
			f.write(f'\t\t\t\t\trouteState <= CANCEL_ROUTE;\n')
			f.write(f'\t\t\t\tend if;\n')
			infraestructure = []
			for levelCrossing in lc_list:
				if levelCrossing != None:
					infraestructure.append(levelCrossing)
			for switch in sw_list:
				if switch != None:	
					x = f'{"s" if switch[0][0].isdigit() else ""}{switch}'	
					infraestructure.append(x)
			for dswitch in dw_list:
				if dswitch != None:	
					x = f'{"s" if dswitch[0][0].isdigit() else ""}{dswitch}'	
					infraestructure.append(x)
			for scissorSwitch in sc_list:
				if scissorSwitch != None:	
					x = f'{"s" if scissorSwitch[0][0].isdigit() else ""}{scissorSwitch}'	
					infraestructure.append(x)

			generalRelease = " and ".join(f'{s}_lock = RELEASED' for s in infraestructure if s)	
			if any(element != None for element in infraestructure):
				f.write(f'\t\t\t\tif ({generalRelease}) then\n')
				
				for i in infraestructure:
					f.write(f'\t\t\t\t\t{i}_command <= RESERVE;\n')
				f.write(f'\t\t\t\tend if;\n')
			generalReserve = " and ".join(f'{s}_lock = RESERVED' for s in infraestructure if s)
			if any(element != None for element in infraestructure):
				f.write(f'\t\t\t\tif ({generalReserve})then\n')
				f.write(f'\t\t\t\t\trestart <= \'1\';\n')
				f.write(f'\t\t\t\t\trouteState <= LOCKING_INFRASTRUCTURE;\n')
				f.write(f'\t\t\t\tend if;\n')
			else:
				f.write(f'\t\t\t\t\trestart <= \'1\';\n')
				f.write(f'\t\t\t\trouteState <= LOCKING_INFRASTRUCTURE;\n')

			f.write(f'\r\t\t\twhen LOCKING_INFRASTRUCTURE =>\n')
			f.write(f'\t\t\t\trestart <= \'0\';\n')
			f.write(f'\t\t\t\tif (routingIn = CANCEL_ROUTE or timeout =\'1\') then\n')
			f.write(f'\t\t\t\t\trouteState <= CANCEL_ROUTE;\n')
			f.write(f'\t\t\t\tend if;\n')
			infraestructure = []
			for levelCrossing in lc_list:
				if levelCrossing != None:
					infraestructure.append(levelCrossing)
			for switch in sw_list:
				if switch != None:			
					x = f'{"s" if switch[0][0].isdigit() else ""}{switch}'	
					infraestructure.append(x)
			for dswitch in dw_list:
				if dswitch != None:			
					x = f'{"s" if dswitch[0][0].isdigit() else ""}{dswitch}'	
					infraestructure.append(x)
			for scissorSwitch in sc_list:
				if scissorSwitch != None:			
					x = f'{"s" if scissorSwitch[0][0].isdigit() else ""}{scissorSwitch}'	
					infraestructure.append(x)

			generalRelease = " and ".join(f'{s}_lock = RESERVED' for s in infraestructure if s)		
			if any(element != None for element in infraestructure):
				f.write(f'\t\t\t\tif ({generalRelease}) then\n')
				for i in infraestructure:
					f.write(f'\t\t\t\t\t{i}_command <= LOCK;\n')		
				f.write(f'\t\t\t\tend if;\n')
			generalLock = " and ".join(f'{s}_lock = LOCKED' for s in infraestructure if s)
			if any(element != None for element in infraestructure):
				f.write(f'\t\t\t\tif ({generalLock})then\n')
				for net in route['Path']:
					f.write(f'\t\t\t\t\t{net}_used <= \'0\';\n')
				f.write(f'\t\t\t\t\trestart <= \'1\';\n')
				f.write(f'\t\t\t\t\trouteState <= DRIVING_SIGNAL;\n')	
				f.write(f'\t\t\t\tend if;\n')
			else:
				for net in route['Path']:
					f.write(f'\t\t\t\t\t{net}_used <= \'0\';\n')
				f.write(f'\t\t\t\t\trestart <= \'1\';\n')
				f.write(f'\t\t\t\t\trouteState <= DRIVING_SIGNAL;\n')
			
			f.write(f'\r\t\t\twhen DRIVING_SIGNAL =>\n')
			f.write(f'\t\t\t\trestart <= \'0\';\n')
			f.write(f'\t\t\t\tif (routingIn = CANCEL_ROUTE or timeout =\'1\') then\n')
			f.write(f'\t\t\t\t\trouteState <= CANCEL_ROUTE;\n')
			f.write(f'\t\t\t\tend if;\n')
			
			f.write(f'\t\t\t\tif ({route['Start']}_lock = RELEASED and {route['End']}_lock = RELEASED) then\n')
			f.write(f'\t\t\t\t\t{route['Start']}_command <= RESERVE;\n')
			f.write(f'\t\t\t\t\t{route['End']}_command <= LOCK;\n')
			f.write(f'\t\t\t\tend if;\n')
			#f.write(f'\t\t\t\tif ({route['Start']}_lock = RESERVED and {route['Start']}_state /= RED) then\n')
			f.write(f'\t\t\t\tif ({route['Start']}_lock = RESERVED and {route['End']}_lock = LOCKED) then\n')
			f.write(f'\t\t\t\t\trestart <= \'1\';\n')
			f.write(f'\t\t\t\t\trouteState <= SEQUENTIAL_RELEASE;\n')
			f.write(f'\t\t\t\tend if;\n')		

			f.write(f'\r\t\t\twhen SEQUENTIAL_RELEASE =>\n')
			f.write(f'\t\t\t\trestart <= \'0\';\n')
			f.write(f'\t\t\t\tif (routingIn = CANCEL_ROUTE or timeout =\'1\') then\n')
			f.write(f'\t\t\t\t\trouteState <= CANCEL_ROUTE;\n')
			f.write(f'\t\t\t\tend if;\n')
			f.write(f'\t\t\t\t--- Sequential release\n')

			for i,net in enumerate(route['Path']):
				if (net != route['Path'][0]):
					f.write(f'\t\t\t\t\t---\n')
					f.write(f'\t\t\t\tif ({route['Path'][i-1]}_lock = RELEASED and {net}_used = \'0\' and {net}_state = OCCUPIED) then \n')
				else:
					f.write(f'\t\t\t\tif ({net}_used = \'0\' and {net}_state = OCCUPIED) then \n')
				f.write(f'\t\t\t\t\t{net}_used <= \'1\';\n')

				if net == route['Path'][-1]:
					f.write(f'\t\t\t\t\t--- Finish -> Release all\n')	
					f.write(f'\t\t\t\t\trestart <= \'1\';\n')		
					f.write(f'\t\t\t\t\trouteState <= RELEASING_INFRASTRUCTURE;\n')
				f.write(f'\t\t\t\tend if;\n')

				if net != route['Path'][-1]:
					f.write(f'\t\t\t\tif ({net}_used = \'1\' and {net}_state = FREE) then\n')
					f.write(f'\t\t\t\t\t{net}_used <= \'0\';\n')
					f.write(f'\t\t\t\t\t{net}_command <= RELEASE;\n')
					f.write(f'\t\t\t\tend if;\n')

			f.write(f'\r\t\t\twhen RELEASING_INFRASTRUCTURE =>\n')

			for levelCrossing in lc_list:
				if levelCrossing != None:
					f.write(f'\t\t\t\t{levelCrossing}_command <= RELEASE;\n')
			for switch in sw_list:
				if switch != None:
					f.write(f'\t\t\t\t{"s" if switch[0][0].isdigit() else ""}{switch}_command <= RELEASE;\n')
			for dswitch in dw_list:
				if dswitch != None:
					f.write(f'\t\t\t\t{"s" if dswitch[0][0].isdigit() else ""}{dswitch}_command <= RELEASE;\n')
			for scissorSwitch in sc_list:
				if scissorSwitch != None:
					f.write(f'\t\t\t\t{"s" if scissorSwitch[0][0].isdigit() else ""}{scissorSwitch}_command <= RELEASE;\n')

			for net in route['Path']:
				f.write(f'\t\t\t\t{net}_command <= RELEASE;\n')
			
			f.write(f'\t\t\t\t{route['Start']}_command <= RELEASE;\n')
			f.write(f'\t\t\t\t{route['End']}_command <= RELEASE;\n')
			f.write(f'\t\t\t\trestart <= \'1\';\n')
			f.write(f'\t\t\t\trouteState <= WAITING_COMMAND;\n')

			f.write(f'\r\t\t\twhen CANCEL_ROUTE =>\n')
			f.write(f'\t\t\t\trouteState <= RELEASING_INFRASTRUCTURE;\n')

			f.write(f'\r\t\t\twhen others =>\n')
			f.write(f'\t\t\t\trouteState <= WAITING_COMMAND;\n')
			f.write(f'\t\tend case;\r\n')
			f.write(f'\tend if;\r\n')
			f.write(f'\tend process;\r\n') 

			f.write(f'end Behavioral;') 
			f.close()
    		
	def createPrinter(self,N,example = 1):
		node = 'printer'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f,True)
			
		# printer entity
		printer = 'printer'
		f.write(f'\tentity {printer} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tprocessing : in std_logic;\n')
		f.write(f'\t\t\tprocessed : out std_logic;\n')
		f.write(f'\t\t\tpacket_i : in hex_array({str(N)}-1 downto 0);\n')
		f.write(f'\t\t\tw_data : out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\twr_uart : out std_logic; -- \'char_disp\'\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {printer};\r\n') 
	
		f.write(f'architecture Behavioral of {printer} is\r\n') 

		f.write(f'\ttype states_t is (RESTART,CYCLE_1,CYCLE_2);\n') 
		f.write(f'\tsignal mux_out_s : hex_char;\n') 
		f.write(f'\tsignal state, next_state : states_t;\n') 
		f.write(f'\tsignal ena_s,rst_s,reg_aux : std_logic;\n') 
		f.write(f'\tsignal mux_s : std_logic_vector({str(math.ceil(np.log2(N+1)))}-1 downto 0);\r\n')  ### TODO:
	
		f.write(f'\t-- Lookup table for hex_char to ASCII conversion\n')
		f.write(f'\tconstant hex_to_ascii : ascii_packet := (\n')
		f.write(f'\t\t\'0\' => "00110000", \'1\' => "00110001", \'2\' => "00110010", \'3\' => "00110011",\n')
		f.write(f'\t\t\'4\' => "00110100", \'5\' => "00110101", \'6\' => "00110110", \'7\' => "00110111",\n')
		f.write(f'\t\t\'8\' => "00111000", \'9\' => "00111001", \'A\' => "01000001", \'B\' => "01000010",\n')
		f.write(f'\t\t\'C\' => "01000011", \'D\' => "01000100", \'E\' => "01000101", \'F\' => "01000110"\n')
		f.write(f'\t);\n')
		f.write(f'\t-- Function to convert mux_s to integer\n')
		f.write(f'\tfunction mux_to_int(mux : std_logic_vector) return integer is\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\treturn to_integer(unsigned(mux));\n')
		f.write(f'\tend function mux_to_int;\n')

		f.write(f'begin\r\n')
		
		f.write(f'\tcontador : process(clock)\n')
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (clock = \'1\' and clock\'event) then\n')
		f.write(f'\t\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\t\tmux_s <= "{str('0'*math.ceil(np.log2(N+1)))}";\n')               ### TODO:
		f.write(f'\t\t\telse\n')
		f.write(f'\t\t\t\tif (ena_s = \'1\') then\n')        
		f.write(f'\t\t\t\t\tif (mux_s /= "{'{0:b}'.format(N)}") then\n')     ### TODO:
		f.write(f'\t\t\t\t\t\tif (state = CYCLE_1 or state = CYCLE_2) then\n')
		f.write(f'\t\t\t\t\t\t\tmux_s <= std_logic_vector(to_unsigned(to_integer(unsigned(mux_s)) + 1 , {str(math.ceil(np.log2(N+1)))}));\n')     ### TODO:     
		f.write(f'\t\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\t\tif (processing = \'0\') then\n')
		f.write(f'\t\t\t\t\tmux_s <= "{str('0'*math.ceil(np.log2(N+1)))}";\n')             ### TODO:
		f.write(f'\t\t\t\tend if;\n')             
		f.write(f'\t\t\tend if;\n') 
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')
		
		f.write(f'\tmultiplexor : process(packet_i,mux_s)\n')
		f.write(f'\tbegin\n')
		#f.write(f'\t\tcase mux_s is\n')
		
		f.write(f'\t\tmux_out_s <= packet_i(mux_to_int(mux_s));\n')

		#for i in range(N):
		#	f.write(f'\t\t\twhen "{str(bin(i))[2:].zfill(math.ceil(np.log2(N+1)))}" => mux_out_s <= packet_i({str(i)});\n')

		#f.write(f'\t\t\twhen others => mux_out_s <= \'0\';\n')
		#f.write(f'\t\tend case;\n')     
		f.write(f'\tend process;\r\n')   
					
		#f.write(f'\tw_data <= "00110001" when mux_out_s = \'1\' else "00110000";\r\n')

		f.write(f'\tw_data <= hex_to_ascii(mux_out_s);\r\n')

		f.write(f'\tFSM_reset : process(clock)\n') 
		f.write(f'\tbegin\n') 
		f.write(f'\t\tif (clock = \'1\' and clock\'event) then\n') 
		f.write(f'\t\t\tif reset = \'1\' then\n') 
		f.write(f'\t\t\t\tstate <= RESTART;\n')           
		f.write(f'\t\t\telse\n')                  
		f.write(f'\t\t\t\tif (processing = \'1\') then\n')           
		f.write(f'\t\t\t\t\tstate <= next_state;\n') 
		f.write(f'\t\t\t\telse\n') 
		f.write(f'\t\t\t\t\tstate <= RESTART;\n') 
		f.write(f'\t\t\t\tend if;\n') 
		f.write(f'\t\t\tend if;\n')  
		f.write(f'\t\tend if;\n') 
		f.write(f'\tend process;\r\n') 
		
		f.write(f'\tFSM : process(processing,state,mux_s)\n') 
		f.write(f'\tbegin\n') 
		f.write(f'\t\tnext_state <= state;\n')    
		f.write(f'\t\tcase state is\n') 
		f.write(f'\t\t\twhen RESTART =>\n') 
		f.write(f'\t\t\t\twr_uart <= \'0\';\n') 
		f.write(f'\t\t\t\trst_s <= \'1\';\n') 
		f.write(f'\t\t\t\tena_s <= \'0\';\n') 
		f.write(f'\t\t\t\tprocessed <= \'0\';\n') 
		f.write(f'\t\t\t\treg_aux <= \'0\';\n')  
		f.write(f'\t\t\t\tif (processing = \'1\' and mux_s /= "{'{0:b}'.format(N)}" ) then\n') 
		f.write(f'\t\t\t\t\tnext_state <= CYCLE_1;\n') 
		f.write(f'\t\t\t\tend if;\n') 
		f.write(f'\t\t\twhen CYCLE_1 =>\n') 
		f.write(f'\t\t\t\twr_uart <= \'0\';\n') 
		f.write(f'\t\t\t\trst_s <= \'0\';\n') 
		f.write(f'\t\t\t\tena_s <= \'0\';\n') 
		f.write(f'\t\t\t\t--processed <= \'0\';\n')                
		f.write(f'\t\t\t\tnext_state <= CYCLE_2;\n')              
		f.write(f'\t\t\twhen CYCLE_2 =>\n') 
		f.write(f'\t\t\t\twr_uart <= \'1\';\n') 
		f.write(f'\t\t\t\trst_s <= \'0\';\n') 
		f.write(f'\t\t\t\tena_s <= \'1\';\n')               
		f.write(f'\t\t\t\tprocessed <= \'0\';\n') 
		f.write(f'\t\t\t\treg_aux <= \'0\';\n')          
		f.write(f'\t\t\t\tif mux_s = "{'{0:b}'.format(N-1)}" then\n') 
		f.write(f'\t\t\t\t\tprocessed <= \'1\';\n') 
		f.write(f'\t\t\t\t\treg_aux <= \'1\';\n') 
		f.write(f'\t\t\t\t\tnext_state <= RESTART;\n')            
		f.write(f'\t\t\t\telse\n') 
		f.write(f'\t\t\t\t\tnext_state <= CYCLE_1;\n') 
		f.write(f'\t\t\t\tend if;\n') 
		f.write(f'\t\t\twhen others => null;\n') 
		f.write(f'\t\tend case;\n') 
		f.write(f'\tend process;\r\n') 
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file

	def createSelector(self,example = 1):
		
		node = 'selector'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# selector entity
		selector = "selector"
		f.write(f'\tentity {selector} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic;\n')
		f.write(f'\t\t\tselector : in std_logic;\n')
		f.write(f'\t\t\tleds : out std_logic_vector(4-1 downto 0);\n')
		f.write(f'\t\t\twr_uart_1 : in std_logic;\n')
		f.write(f'\t\t\twr_uart_2 : in std_logic;\n')
		f.write(f'\t\t\twr_uart_3 : out std_logic;\n')
		f.write(f'\t\t\tw_data_1 : in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tw_data_2 : in std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\tw_data_3 : out std_logic_vector(8-1 downto 0);\n')
		f.write(f'\t\t\treset : in std_logic\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {selector};\r\n') 
	
		f.write(f'architecture Behavioral of {selector} is\r\n')            
		
		f.write(f'\tsignal disp_aux : std_logic_vector(8-1 downto 0);\r\n') 
	
		f.write(f'begin\r\n')
		
		f.write(f'\tselectors : process(clock)\n')   
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (clock = \'1\' and clock\'event) then\n')
		f.write(f'\t\t\tif reset = \'1\' then\n')
		f.write(f'\t\t\t\tw_data_3 <= "00000000";\n')
		f.write(f'\t\t\t\twr_uart_3 <= \'0\';\n')
		f.write(f'\t\t\telse\n') 
		f.write(f'\t\t\t\tif selector = \'1\' then\n')                                    
		f.write(f'\t\t\t\t\tdisp_aux <= w_data_2;\n')                  
		f.write(f'\t\t\t\t\tw_data_3 <= disp_aux;\n')                               
		f.write(f'\t\t\t\t\twr_uart_3 <= wr_uart_2;\n')                            
		f.write(f'\t\t\t\t\tleds <= "0010";\n')
		f.write(f'\t\t\t\telse\n')         
		f.write(f'\t\t\t\t\tdisp_aux <= w_data_1;\n')                   
		f.write(f'\t\t\t\t\tw_data_3 <= disp_aux;\n')                               
		f.write(f'\t\t\t\t\twr_uart_3 <= wr_uart_1;\n')
		f.write(f'\t\t\t\t\tleds <= "0001";\n')
		f.write(f'\t\t\t\tend if;\n')
		f.write(f'\t\t\tend if;\n')
		f.write(f'\t\tend if;\n')
		f.write(f'\tend process;\r\n')
			
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file   
	
	def createFlipFlop(self,example):
		node = 'flipFlop'
		f = open(f'App/Layouts/Example_{example}/VHDL/{node}.vhd',"w+")
		
		# Initial comment
		self.initialComment(node,f)
		
		# Include library
		self.includeLibrary(f)
			
		# flipFlop entity
		flipFlop = "flipFlop"
		f.write(f'\tentity {flipFlop} is\n')
		f.write(f'\t\tport(\n')
		f.write(f'\t\t\tclock : in std_logic := \'0\';\n')
		f.write(f'\t\t\treset : in std_logic := \'0\';\n')
		f.write(f'\t\t\tQ : out std_logic := \'0\'\n')
		f.write(f'\t\t);\n')
		f.write(f'\tend entity {flipFlop};\r\n') 
	
		f.write(f'architecture Behavioral of {flipFlop} is\r\n')            
		f.write(f'\tsignal Q_aux : std_logic := \'0\';\n')
		f.write(f'begin\r\n')
		
		f.write(f'\tflip_flop : process(clock)\n')   
		f.write(f'\tbegin\n')
		f.write(f'\t\tif (reset = \'1\') then\n')
		f.write(f'\t\t\tQ_aux <= \'0\';\n')
		f.write(f'\t\telsif(falling_edge(clock)) then\n')
		f.write(f'\t\t\tQ_aux<= not Q_aux;\n')
		f.write(f'\t\tend if;\n') 
		f.write(f'\tend process;\r\n')
		f.write(f'\tQ <= Q_aux;\r\n')
		f.write(f'end Behavioral;') 
		
		f.close()  # Close header file

	def get_data(self):
		return self.data
	
	def __init__(self,RML,routes,example = 1):
		print("#"*50+' Reading railML object '+"#"*50)
		
		network = self.create_graph_structure(RML,example)
		self.print_network(network)
		
		n_routes = len(routes)
		#for route in routes:
		#	print('R'+str(route),routes[route])

		# Enable to plot graph
		#self.create_graph(RML,network,example)

		# Calculate N and M
		N,M,n_netElements,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,n_signals_1,n_signals_2,n_signals_3 = self.calculate_parameters(network)
		N = N + n_routes
		M = M + n_routes
		print(f'N : {N}\nM : {M}')

		n_signals = n_signals_1 + n_signals_2 + n_signals_3

		print("#"*30+' Creating VHDL files '+"#"*30)
		
		print(f'Creating package ... ',end='')
		self.createPacket(N,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,n_signals,example)
		print(f'Done')
		
		print(f'Creating global wrapper ... ',end='')
		self.createGlobal(N,M,example)
		print(f'Done')
		
		print(f'Creating UARTs ... ',end='')
		self.createUARTs(N,M,example)
		print(f'Done')

		print(f'Creating system ... ',end='')
		self.createSystem(N,M,example)
		print(f'Done')
		
		print(f'Creating detector ... ',end='')
		self.createDetector(N,example)
		print(f'Done')
		
		print(f'Creating interlocking ... ',end='')
		self.createInterlocking(N,M,n_netElements,n_routes,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,n_signals,example)
		print(f'Done')
		
		print(f'Creating splitter ... ',end='')
		self.createSplitter(N,n_netElements,n_routes,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example)
		print(f'Done')
		
		print(f'Creating mediator ... ',end='')
		self.createMediator(N,M,n_netElements,n_routes,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example)
		print(f'Done')
		
		print(f'Creating network ... ',end='')
		self.createNetwork(network,routes,N,n_netElements,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example)
		print(f'Done')

		print(f'Creating voter ... ',end='')
		self.createVoter(network,routes,N,n_netElements,n_signals,n_switches,n_doubleSwitch,n_scissorCrossings,n_levelCrossings,example)
		print(f'Done')
	
		print(f'Creating printer ... ',end='')
		self.createPrinter(N,example)
		print(f'Done')
		
		print(f'Creating selector ... ',end='')
		self.createSelector(example)
		print(f'Done')
		
		print(f'Creating timers ... ',end='')
		self.createFlipFlop(example)
		print(f'Done')

		print("#"*30+' VHDL files Created '+"#"*30)

		self.data = [N,M,n_netElements,n_routes,n_signals,n_levelCrossings,n_switches,n_doubleSwitch,n_scissorCrossings]