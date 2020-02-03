print(banner1,'Aligning ground (XY) plane with coded targets...')
        
    def vect(a, b):
        """
        Normalized vector product for two vectors
        """

        result = Metashape.Vector([a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y *b.x])
        return result.normalized()

    def get_marker(label, chunk):
        """
        Returns marker instance from chunk based on the label correspondence
        """
        
        for marker in chunk.markers:
            if label == marker.label:
                return marker
        print("Marker not found! " + label)
        return False

    chunk = Metashape.app.document.chunk
    region = chunk.region
    '''vertical = ["target 9", "target 3"] 
    horizontal = ["target 9", "target 1"]'''
    
    horizontal = ["point 1", "point 2"]#["target 9", "target 16"]
    vertical = ["point 1", "point 4"]#["target 9", "target 3"] #fails on S08, S12
    #vertical = ["target 2", "target 15"] #run for all?
    
    print('H0: ',get_marker(horizontal[0], chunk).position)
    print('H1: ',get_marker(horizontal[1], chunk).position)
    print('V0: ',get_marker(vertical[0], chunk).position)
    print('V1: ',get_marker(vertical[1], chunk).position)
           
    horizontal = get_marker(horizontal[0], chunk).position - get_marker(horizontal[1], chunk).position
    vertical = get_marker(vertical[0], chunk).position - get_marker(vertical[1], chunk).position

    '''normal = vect(horizontal, vertical)
    vertical = - vertical.normalized()
    horizontal = vect(vertical, normal)'''
    normal = vect(horizontal, vertical)
    horizontal = - horizontal.normalized()
    vertical = - vect(horizontal, normal)

    R = Metashape.Matrix ([horizontal, vertical, normal]) #horizontal = X, vertical = Y, normal = Z

    print(R.det())
    region.rot = R.t()
    chunk.region = region
    R = chunk.region.rot        #Bounding box rotation matrix
    C = chunk.region.center        #Bounding box center vector

    if chunk.transform.matrix:
        T = chunk.transform.matrix
        s = math.sqrt(T[0,0] ** 2 + T[0,1] ** 2 + T[0,2] ** 2)         #scaling # T.scale()
        S = Metashape.Matrix().Diag([s, s, s, 1]) #scale matrix
    else:
        S = Metashape.Matrix().Diag([1, 1, 1, 1])
    T = Metashape.Matrix( [[R[0,0], R[0,1], R[0,2], C[0]], [R[1,0], R[1,1], R[1,2], C[1]], [R[2,0], R[2,1], R[2,2], C[2]], [0, 0, 0, 1]])
    chunk.transform.matrix = S * T.inv()        #resulting chunk transformation matrix        

    chunk.resetRegion()

    print(" Ground alignment finished")