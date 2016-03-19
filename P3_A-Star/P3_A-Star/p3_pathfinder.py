# Amir Ashkan Nourkhalaj
# Matthew Sandfrey


from math import sqrt
from heapq import heappush, heappop

#coordinates are in y1, y2, x1, x2 order
#x and y are reverse
def find_path(source, destination, mesh):
    adj = mesh['adj']
    forw_dist = {}
    back_dist = {}
    forw_prev = {}
    back_prev = {}
    queue = []
    path = []
    detail_points = {}
    alt = 0
    build = False

    sourceBox = find_source_box(source, mesh)
    forw_dist[sourceBox] = 0
    print(source, destination)
    destBox = find_source_box(destination, mesh)
    back_dist[destBox] = 0
    print(sourceBox, destBox)
    if sourceBox == destBox:
        return ([(source, destination)], [(sourceBox)])
    #else:
        #print ("No path can be found!")
        #return ([], [])

    queue = [(forw_dist[sourceBox], sourceBox, source, "destination")]
    heappush(queue, (back_dist[destBox], destBox, destination, "source"))
    forw_prev[sourceBox] = None
    back_prev[destBox] = None
    forw_last = sourceBox
    back_last = destBox

    try:
        while queue:
            priority, currBox, currCoor, currGoal = heappop(queue)

            if currGoal == 'destination':
                for next in adj[currBox]:
                    if next == back_last:
                        build = True
                        forw_last = currBox
                        break
                if build:
                    break

                for next_box in adj[currBox]:
                    nextCoordinate = find_detail_points(currCoor, next_box)
                    trueDistance = true_distance(currCoor, nextCoordinate)
                    alt = forw_dist[currBox] + trueDistance

                    if next_box not in forw_prev or alt < forw_dist[next_box]:
                        forw_dist[next_box] = alt
                        priority = alt + true_distance(destination, nextCoordinate)
                        forw_prev[next_box] = currBox
                        heappush(queue, (priority, next_box, nextCoordinate, currGoal))
                        forw_last = currBox
            else:
                for next in adj[currBox]:
                    if next == forw_last:
                            build = True
                            back_last = currBox
                            break
                if build:
                    break
                for next_box in adj[currBox]:
                    nextCoordinate = find_detail_points(currCoor, next_box)
                    trueDistance = true_distance(currCoor, nextCoordinate)
                    alt = back_dist[currBox] + trueDistance

                    if next_box not in back_prev or alt < back_dist[next_box]:
                        back_dist[next_box] = alt
                        priority = alt + true_distance(source, nextCoordinate)
                        back_prev[next_box] = currBox
                        heappush(queue,(priority, next_box, nextCoordinate, currGoal))
                        back_last = currBox
    except:
            print("Not a valid starting point.")
            return ([], [])
            #print("test")

    if build:
        currentBox = forw_last
        while currentBox != None:
            path.append(currentBox)
            currentBox = forw_prev[currentBox]
        path.reverse()
        currentBox = back_last
        while currentBox != None:
            if currentBox not in path:
                path.append(currentBox)
            currentBox = back_prev[currentBox]

        print ("Path: ", len(path))
        for box in path:
            new_point = find_detail_points(source, box)
            if box != sourceBox:
                detail_points[box] = (source, new_point)
            if box != destBox and box != sourceBox:
                source = new_point
        #detail_points[destBox] = (new_point, destination)
        points = []
        for point in detail_points.values():
            points.append(point)
        points.append((new_point, destination))
        visited = []
        for forw in forw_prev.keys():
            visited.append(forw)
        for back in back_prev.keys():
            visited.append(back)
        print("Number of Visited: ", len(visited))
        return points, path
    else:
        print ("No path possible!")
        return ([], [])

def find_detail_points(current_coords, end_box):

    x, y = current_coords

    e_x1, e_x2, e_y1, e_y2 = end_box

    new_x = min(e_x2, max(e_x1, x))
    new_y = min(e_y2, max(e_y1, y))

    return(new_x, new_y)


def find_source_box(xy_coord, mesh):

    for box in mesh['boxes']:

        x1, x2, y1, y2 = box
        start_x, start_y = xy_coord

        if x1 < start_x < x2 and y1 < start_y < y2:
                return box


def is_in_box(a, b):
    if b[1] >= a[0] >= b[0] and b[3] >= a[1] >= b[2]:
        return True
    else:
        return False


def true_distance(a, b):
    x1, y1 = a
    x2, y2 = b

    return sqrt((x1-x2)**2+(y1-y2)**2)