import qiskit
import numpy as np
import networkx as nx


class Lattice:
    # Initializes a lattice configuration suitable for Kitaev's toric code. 
    # Qubits are arranged in a rows x cols grid, qubit locations are specified by (row index, column index, orientation), 
    # where orientation can be vertical or horizontal. 
    
    #For example, for the 3x3 lattice grid below: 
    
    #    (0,0) --h0-- (0,1) --h1-- (0,2) --h2-- (0,0)  
    #    |             |             |             |
    #    v0            v1            v2            v0
    #    |             |             |             |
    #  (1,0) --h3-- (1,1) --h4-- (1,2) --h5-- (1,0)  
    #    |             |             |             |
    #    v3            v4            v5            v3
    #    |             |             |             |
    #  (2,0) --h6-- (2,1) --h7-- (2,2) --h8-- (2,0)  
    #    |             |             |             |
    #    v6            v7            v8            v6
    #    |             |             |             |
    #  (0,0) --h0-- (0,1) --h1-- (0,2) --h2-- (0,0)  
    #
    #  qubits are denoted by h0,h1,.. , h8 and v0,v1,..,v8
    #  qubit h0 is at location (0,0, horizontal) while v0 is at location (0,0,vertical)
    #  qubit v5 is at location (1,2, vertical)
    #  in other words, we may view these coordinates as specifying two 3x3 lattices that are interlaced with each other: 
    #  one lattice is called "horizontal" and the other lattice is called "vertical"
    
    def __init__(self,rows, cols):
        self.rows = rows
        self.cols = cols
        self.num_of_qubits = 2* rows*cols
        
        plaquettes = [] 
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                P = Plaquette(i,j)
                row.append(P)
            plaquettes.append(row)
            
        self.plaquettes = plaquettes
        self.plaquettes_lin = self.order_plaquettes()
        
        stars = [] 
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                S = Star(i,j)
                row.append(S)
            stars.append(row)
            
        self.stars = stars
        self.stars_lin = self.order_stars()       
        
    
        
    def get_flat_index_horizontal(self, x, y):
        # given an index specified by (x,y,horizontal), return the corresponding "flat index". That is, 
        # starting from the top left to bottom right, return the corresponding index from 0 to 2*rows*cols 
        
        return 2*x*self.cols + y
    
    def get_flat_index_vertical( self, x, y): 
        # given an index specified by (x,y,vertical), return the corresponding "flat index". That is, 
        # starting from the top left to bottom right, return the corresponding index from 0 to 2*rows*cols  
        return 2*x*self.cols + y + self.cols
    def get_flat_indices_bulk(self, L):
        # given a list of tuples (row,col,orientation), where orientation is specified by a single character 'h' or 'v'
        # return (in place) a list of flat indices corresponding to each tuple.
       flat_coords = []
       for t in L:
            if t[2] == 'h':
               flat_coords.append(self.get_flat_index_horizontal(t[0] % self.rows ,t[1]  % self.cols  ) )
            elif t[2] == 'v':
                flat_coords.append(self.get_flat_index_vertical(t[0]  % self.rows ,t[1]  % self.cols))
       return flat_coords       

    
    def get_plaquette_indices(self, p_x,p_y):
        # where p_x , p_y specifies the horizontal index of the top edge of a plaquette, 
        # return a list consisting of all the flat indices of the edges forming the boundary of the specific plaquette.
        # For example, in the 3x3 case specifying the plaquette at index (0,1) specifies the plaquette 
        #              -- h1 --
        #              |       |      
        #              v1      v2   
        #              |       |
        #              -- h4 --
        # the corresponding list of flat indices should be [1,4,7,5]
        
        L = [
            
            (p_x,p_y, 'h'),    #top edge 
            (p_x,p_y, 'v'),    # left edge 
            (p_x + 1 , p_y, 'h'), #bottom edge
            (p_x , p_y + 1, 'v')   # right edge
        ]
        
        return self.get_flat_indices_bulk(L)  
    
    
    def order_plaquettes(self):
        L = []
        for i in range(self.rows):
            for j in range(self.cols):
                L.append(self.plaquettes[i][j]) 
        return L 
    
    def order_stars(self):
        L = []
        for i in range(self.rows):
            for j in range(self.cols):
                L.append(self.stars[i][j]) 
        return L 

  
    def get_star_indices(self, s_x,s_y):
        # where s_x , s_y specifies the horizontal index of the top (vertical) edge of a star, 
        # return a list consisting of all the flat indices of the edges forming the star (of a vertex)
        # For example, in the 3x3 case specifying the star at index (0,1) specifies the star          
        #
        #              |             
        #              v1         
        #              |       
        #      -- h3 --  --h4 -- 
        #              |
        #              v4
        #              |
                             
        # the corresponding list of flat indices should be [4,6,10,7]
        
        L = [
            
            (s_x,s_y, 'v'),    #top edge 
            (s_x + 1 , s_y - 1, 'h'),    # left edge 
            (s_x + 1 , s_y, 'v'), #bottom edge
            (s_x + 1 , s_y, 'h')   # right edge
        ]
        
        return self.get_flat_indices_bulk(L)  
    
    def populate_plaquettes(self, LatticeCircuit):
        for i in range(self.rows):
            for j in range(self.cols):
                self.plaquettes[i][j].qubits = [ LatticeCircuit.qubits[idx] for idx in self.get_plaquette_indices(i,j)]
        
    def populate_stars(self, LatticeCircuit):
        for i in range(self.rows):
            for j in range(self.cols):
                self.stars[i][j].qubits = [ LatticeCircuit.qubits[idx] for idx in self.get_star_indices(i,j)]
                
                
    # def get_stars(self, LatticeCircuit):
    #     L = [ ]
    #     for i in range(self.rows):
    #         row = []
    #         for j in range(self.cols):
    #             S = Star(i,j)
    #             S.qubits = [ LatticeCircuit.qubits[idx] for idx in self.get_star_indices(i,j)]
    #             row.append(S)
    #         L.append(row)
    #     return L
    

    def marked_plaquettes_graph(self, marked_plaquettes):
        # returns a weighted graph of marked plaquettes, edges are weighted by the distance between marked plaquettes
        plaquette_graph = nx.complete_graph(len(marked_plaquettes))
        
        labels_dict = dict(enumerate(marked_plaquettes) )
        plaquette_graph = nx.relabel_nodes(plaquette_graph, labels_dict)
        
        for edge in plaquette_graph.edges:
            
            plaquette_graph.edges[ edge[0], edge[1] ]['weight'] = self.plaquettes_lin[edge[0]].dist(self.plaquettes_lin[edge[1]], self.rows, self.cols)
        return plaquette_graph     

    def marked_stars_graph(self, marked_stars):
        # returns a weighted graph of marked stars, edges are weighted by the distance between marked stars
        star_graph = nx.complete_graph(len(marked_stars))
        
        labels_dict = dict(enumerate(marked_stars) )
        star_graph = nx.relabel_nodes(star_graph, labels_dict)
        
        for edge in star_graph.edges:
            
            star_graph.edges[ edge[0], edge[1] ]['weight'] = self.stars_lin[edge[0]].dist(self.stars_lin[edge[1]], self.rows, self.cols)
        return star_graph     
                
    
    def plaquette_path(self, LatticeCircuit, P1,P2):
        
        # returns a list of qubits along a path connecting two plaquettes
        # plaquettes = self.get_plaquettes(LatticeCircuit)
        
        path = []
        source = P1 
        
        
        while source.row_idx != P2.row_idx:
            row_fwd = source = self.stars[( source.row_idx + 1  ) % self.rows ][(source.col_idx ) % self.cols ]    
            row_back = self.stars[(source.row_idx  - 1) % self.rows][(source.col_idx ) % self.cols ]  
            
            if P2.dist( row_fwd, self.rows, self.cols  ) <= P2.dist( source, self.rows, self.cols  ):
                path.append( source.qubits[2] )
                source = row_fwd
            else:
                path.append( source.qubits[0] )
                source = row_back
            
            
            # if abs( (source.row_idx - 1)%3 -  P2.row_idx ) <=  abs( (source.row_idx + 1)%3 -  P2.row_idx ):
            #     path.append( source.qubits[0] )
            #     source = self.plaquettes[(source.row_idx  - 1) % 3][(source.col_idx ) % 3]        
            # else:
            #     path.append( source.qubits[2] )
            #     source = self.plaquettes[( source.row_idx + 1  ) % 3][(source.col_idx ) % 3]     
                
                     
        while source.col_idx != P2.col_idx:
            col_fwd =  self.stars[(source.row_idx    ) % self.rows ][(source.col_idx + 1) % self.cols ]  
            col_back = self.stars[( source.row_idx   ) % self.rows ][(source.col_idx - 1) % self.cols ]     
            if P2.dist( col_fwd, self.rows, self.cols ) <= P2.dist(source, self.rows, self.cols ):
                path.append( source.qubits[3] )
                source = col_fwd
            else:
                path.append( source.qubits[1] )
                source = col_back            
                            
            
            
            # if abs( (source.col_idx - 1)%3 -  P2.col_idx ) <=  abs( (source.col_idx + 1)%3 -  P2.col_idx ):
            #     path.append( source.qubits[1] )
            #     source = self.plaquettes[( source.row_idx   ) % 3][(source.col_idx - 1) % 3]        
      
            # else:
            #     path.append( source.qubits[3] )
            #     source = self.plaquettes[(source.row_idx    ) % 3][(source.col_idx + 1) % 3]  


        return path
        
    def star_path(self, LatticeCircuit, S1,S2):
        
        # returns a list of qubits along a path connecting two stars
        # stars = self.get_stars(LatticeCircuit)
        
        path = []
        source = S1 
        
        while source.col_idx != S2.col_idx:
            col_fwd =  self.stars[(source.row_idx    ) % self.rows  ][(source.col_idx + 1) % self.cols ]  
            col_back = self.stars[( source.row_idx   ) % self.rows ][(source.col_idx - 1) % self.cols ]     
            if S2.dist( col_fwd, self.rows, self.cols ) <= S2.dist( source, self.rows, self.cols ):
                path.append( source.qubits[3] )
                source = col_fwd
            else:
                path.append( source.qubits[1] )
                source = col_back            
                
            # if abs( (source.col_idx - 1)%3 -  S2.col_idx ) <=  abs( (source.col_idx + 1)%3 -  S2.col_idx ):
                
            #     path.append( source.qubits[1] )
            #     source = self.stars[( source.row_idx   ) % 3][(source.col_idx - 1) % 3]        
      
            # else:
            #     path.append( source.qubits[3] )
            #     source = self.stars[(source.row_idx    ) % 3][(source.col_idx + 1) % 3]  

                
        while source.row_idx != S2.row_idx:
            row_fwd = source = self.stars[( source.row_idx + 1  ) % self.rows  ][(source.col_idx ) % self.cols  ]    
            row_back = self.stars[(source.row_idx  - 1) %  self.rows ][(source.col_idx ) % self.cols ]  
            
            if S2.dist( row_fwd, self.rows, self.cols ) <= S2.dist( source, self.rows, self.cols ):
                path.append( source.qubits[2] )
                source = row_fwd
            else:
                path.append( source.qubits[0] )
                source = row_back
                  
            # if abs( (source.row_idx - 1)%3 -  S2.row_idx ) <=  abs( (source.row_idx + 1)%3 -  S2.row_idx ):
            #     path.append( source.qubits[0] )
            #     source = self.stars[(source.row_idx  - 1) % 3][(source.col_idx ) % 3]        
            # else:
                
            #     source = self.stars[( source.row_idx + 1  ) % 3][(source.col_idx ) % 3]            
            
        

        return path           


        
        
class Plaquette:
    def __init__(self,row_idx , col_idx ):
        self.row_idx = row_idx
        self.col_idx  = col_idx
        self.qubits = []
        
    def dist(self, P, height, width):
        hor =  self.col_idx - P.col_idx
        vert = self.row_idx - P.row_idx
        
        if vert > height/2:
            vert  = vert - height
        if vert < -height/2:
            vert = vert + height 
            
        if hor > width/2:
            hor  = hor - height
        if hor < -width/2:
            hor = hor + width              
        
        
        return abs(hor) + abs(vert)  
        
        
        
class Star:
    def __init__(self,row_idx , col_idx ):
        self.row_idx = row_idx
        self.col_idx  = col_idx
        self.qubits = []
        
        
    def dist(self, S, height, width):
        hor =  self.col_idx - S.col_idx
        vert = self.row_idx - S.row_idx
        
        if vert > height/2:
            vert  = vert - height
        if vert < -height/2:
            vert = vert + height 
            
        if hor > width/2:
            hor  = hor - height
        if hor < -width/2:
            hor = hor + width              
        
        return abs(hor) + abs(vert)             
        