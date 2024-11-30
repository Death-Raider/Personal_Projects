# from pathlib import Path,WindowsPath
import json, math
import numpy as np

# location = Path("labels")
# for file in location.glob("*.json"):
#     print(file)
#     with open(file, "r+") as f:
#         data = json.load(f)
#         data["imagePath"] = f"..\\Annoted_images\\{file.stem}.png"
#         data["imageData"] = None
#         f.seek(0)
#         json.dump(data,f,indent = 4)
#         f.truncate()
# location = Path("labels")
# File_List = [*location.glob("*.json")]
# FileSeperate = WindowsPath('labels/51.json')
# index = File_List.index(FileSeperate)
# File_List = File_List[index:]
# print(File_List)

def floodFillLOOP(matrix):
    checkPoint = lambda P: (P[0] >= len(matrix) or P[1] >= len(matrix[0]) or P[0] < 0 or P[1] < 0)
    p = [ [i,e.index(1)] for i,e in enumerate(matrix) if 1 in e ]
    if len(p) > 0:
        A = p[0]
    else:
        return []
    boundary_points = []
    Stack = [A]
    while len(Stack) > 0:
        A = Stack.pop(0)
        if A in boundary_points:
            continue
            # return boundary_points
        back_down_diagonal_point = [A[0]+1, A[1]-1]
        back_up_diagonal_point = [A[0]-1, A[1]-1]
        front_down_diagonal_point = [A[0]+1, A[1]+1]
        front_up_diagonal_point = [A[0]-1, A[1]+1]
        front_point = [A[0], A[1]+1]
        right_point = [A[0]+1, A[1]]
        back_point = [A[0], A[1]-1]
        left_point = [A[0]-1, A[1]]

        c1 = False if checkPoint(A) else matrix[A[0]][A[1]] == 1

        Q = [False]*4
        if not checkPoint(front_point):
            Q[0] = matrix[front_point[0]][front_point[1]] == 0
        if not checkPoint(right_point):
            Q[1] = matrix[right_point[0]][right_point[1]] == 0
        if not checkPoint(left_point):
            Q[2] = matrix[left_point[0]][left_point[1]] == 0
        if not checkPoint(back_point):
            Q[3] = matrix[back_point[0]][back_point[1]] == 0

        c2 = (np.array(Q)==True).any()
        if c1 and c2:
            boundary_points.append(A)
            Stack.insert(0,back_point)
            Stack.insert(0,back_down_diagonal_point)
            Stack.insert(0,right_point)
            Stack.insert(0,front_down_diagonal_point)
            Stack.insert(0,front_point)
            Stack.insert(0,front_up_diagonal_point)
            Stack.insert(0,left_point)
            Stack.insert(0,back_up_diagonal_point)
    return boundary_points


def floodFill(matrix):

    """
        go to A
        c1 =  check if A == 1
        c2 = check if left to A == 0
        if c1 and c2 then add point A to list
        go straight and repeat from step 1
        if c1 fails go to right and repeat from step 1
        if c1 fails again go to diagonal up and repeat from step 1
        if c1 fails again go to diagonal down and repeat from step 1
        if c1 fails again go to diagonal back up and repeat from step 1
        if c1 fails again go to diagonal back down and repeat from step 1
        if that failes return False
        if A repeats in list end cycle
    """

    matrix = list(matrix) # just in case matrix is np.array
    p = [ [i,e.index(1)] for i,e in enumerate(matrix) if 1 in e ]
    if len(p) > 0:
        A = p[0]
    else:
        return []
    def recursive_boi(matrix,A,t=[]):
        checkPoint = lambda P: (P[0] >= len(matrix) or P[1] >= len(matrix[0]) or P[0] < 0 or P[1] < 0)

        if A in t:
            return True
        if checkPoint(A):
            return False

        c1 = matrix[A[0]][A[1]] == 1

        back_down_diagonal_point = [A[0]+1 ,A[1]-1 ]
        back_up_diagonal_point = [A[0]-1 ,A[1]-1 ]
        front_down_diagonal_point = [A[0]+1 ,A[1]+1 ]
        front_up_diagonal_point = [A[0]-1 ,A[1]+1 ]
        front_point = [A[0] ,A[1]+1 ]
        right_point = [A[0]+1 ,A[1] ]
        back_point = [A[0] ,A[1]-1 ]
        left_point = [A[0]-1 ,A[1] ]

        Q = [False]*4
        # print(front_point,right_point,left_point,back_point)
        if not checkPoint(front_point):
            Q[0] = matrix[front_point[0]][front_point[1]] == 0
        if not checkPoint(right_point):
            Q[1] = matrix[right_point[0]][right_point[1]] == 0
        if not checkPoint(left_point):
            Q[2] = matrix[left_point[0]][left_point[1]] == 0
        if not checkPoint(back_point):
            Q[3] = matrix[back_point[0]][back_point[1]] == 0

        c2 = (np.array(Q)==True).any()

        if c1 and c2:
            t.append(A)
            r = [False]*8
            r[0] = recursive_boi(matrix, back_up_diagonal_point, t)
            r[1] = recursive_boi(matrix, left_point, t)
            r[2] = recursive_boi(matrix, front_up_diagonal_point, t)
            r[3] = recursive_boi(matrix, front_point, t)
            r[4] = recursive_boi(matrix, front_down_diagonal_point, t)
            r[5] = recursive_boi(matrix, right_point, t)
            r[6] = recursive_boi(matrix, back_down_diagonal_point, t)
            r[7] = recursive_boi(matrix, back_point, t)
            if (np.array(r,dtype="object")==False).all():
                return False
        return t
    P = recursive_boi(matrix,A)
    print("P",P)
    return P if P else []

matrix = [
    [0,0,0,0,0,0,0,0],
    [0,1,1,0,1,1,0,0],
    [0,1,1,0,1,1,1,0],
    [0,1,1,1,1,1,0,0],
    [0,0,1,1,1,0,0,0],
]
print(floodFillLOOP(matrix))
