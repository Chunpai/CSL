def readAPDM(filename):
    """
    :param   filename: the name of the input APDM file
    :return: V: the node list. For example, [0,1,2,...]
             E: the edge list. For example, [(0,1),(1,2)...]
             Obs: a dictionary. {Key:Value} Key is edge represented as (endpoint0,endpoint1); 
                    Value is a list of congestion observations {0,1}^T for example [0,1,0,1,1,...]; 
                
             Omega: a dictionary. {Key:Value} Key is edge represented as (endpoint0,endpoint1); 
                    Value is a list of beta distribution tuples [alpha,beta]^T for example [(alpha_0, beta_0),(alpha_1, beta_1)...];
    """
    V = [] #  [0, 1, 2]
    E = [] # [(0, 1), (1, 2), (0, 2)]
    Obs = {} # {(0, 1): [0,1,0], (1, 2): [1,1,0], (0, 2): [0,0,1]}
    Omega = {} # {(0, 1): [1,3], (1, 2): [1,3], (0, 2): [4,1]}

    #print '---readAPDM starts'
    f = open(filename)
    lineStr = f.readline().strip()
    #print '---line 20 lineStr', lineStr
    while lineStr:

        # if lineStr.startswith('#'):
        #     continue
        # print '---line 24'
        if lineStr.startswith('Endpoint0 Endpoint1 obs'):
            lineStr = f.readline().strip()

        #     print 'lineStr 24'
        #     print lineStr
            while True:
                if lineStr == 'END':
                    break
                # print 'while lineStr:', lineStr
                # print lineStr.split(' ')[0], lineStr.split(' ')[1]
                E.append((int(lineStr.split(' ')[0]), int(lineStr.split(' ')[1])))
                lineStr = f.readline().strip()

        #         print lineStr
        lineStr = f.readline().strip()

    # while(lineStr):
    #     if(lineStr.startswith("#")):
    #         continue
    #     if (lineStr.startswith("SECTION1")):
    #         while True:
    #             lineStr = f.readline().strip()
    #             if ( lineStr == "END"):
    #                 break
    #             if (lineStr.startswith("numNodes")):
    #                 numNodes = int(lineStr.split(" ")[2])
    #             if (lineStr.startswith("numEdges")):
    #                 numEdges = int(lineStr.split(" ")[2])
    #             if (lineStr.startswith("dataSource")):
    #                 dataSource = lineStr.split(" ")[2]
    #     if (lineStr.startswith("SECTION2")):
    #         while True:
    #             lineStr = f.readline().strip()
    #             if ( lineStr == "END"):
    #                 break
    #             if ( lineStr == "NodeID"):
    #                 continue
    #             else:
    #                 V.append(int(lineStr))
    #     if (lineStr.startswith("SECTION3")):
    #         while True:
    #             lineStr = f.readline().strip()
    #             if ( lineStr == "END"):
    #                 break
    #             if (lineStr.startswith("Endpoint")):
    #                 continue
    #             else:
    #                 edgeObsTempList = [int(item) for item in lineStr.split(" ")]
    #                 E.append((edgeObsTempList[0],edgeObsTempList[1]))
    #                 Obs[(edgeObsTempList[0],edgeObsTempList[1])] = edgeObsTempList[2:]
    #     if (lineStr.startswith("SECTION4")):
    #         while True:
    #             lineStr = f.readline().strip()
    #             if ( lineStr == "END"):
    #                 break
    #             if (lineStr.startswith("Endpoint")):
    #                 continue
    #             else:
    #                 edgeObsTempList = [int(item) for item in lineStr.split(" ")]
    #                 Omega[(edgeObsTempList[0], edgeObsTempList[1])] = edgeObsTempList[2:]
    #     lineStr = f.readline().strip()

    f.close()
    # print 'in readAPDM E'
    # print E
    return V, E, Obs, Omega




