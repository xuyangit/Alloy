import xlwings as xw
from sqlUtil import *
from os import listdir

def getFiles():
    files = []
    for file in listdir("./xlsx"):
        if(not file.startswith("~")):
            files.append(file)
    return files

files = getFiles()
dbSession = initDB()
#ingredient
def getIngredients(filename):
    workbook = xw.Book(filename)
    sheet = workbook.sheets[0]
    elements = []
    for i in range(2, 108):
        if(sheet.range((2, i)).value != None):
            elements.append(sheet.range((2, i)).value)
        else:
            break
    i = 1
    while(True):
        firstRow = i * 2 + 1
        id = str(sheet.range((firstRow, 1)).value)
        if(id == "None"):
            break
        else:
            row1 = sheet.range((firstRow, 2), (firstRow, len(elements) + 1)).value
            row2 = sheet.range((firstRow + 1, 2), (firstRow + 1, len(elements) + 1)).value
            for col in range(0, len(elements)):
                val1 = row1[col]
                val2 = row2[col]
                if(val1 != None and val2 != None):
                    try:
                        val1, val2 = min(val1, val2), max(val1, val2)
                    except Exception as e:
                        print(filename, firstRow, col, val1, val2)
                        raise
                elif(val2 != None):
                    val1, val2 = 0, val2
                elif(val1 != None):
                    val1, val2 = 0, val1
                else:
                    val1, val2 = 0, 0
                if(val1 != 0 or val2 != 0):
                    try:
                        if(type(val2) is str):
                            get_or_create(dbSession, Ingredient, alloyName=id, elementName=elements[col], misc=val2)
                        else:
                            get_or_create(dbSession, Ingredient, alloyName=id, elementName=elements[col], minPer=val1, maxPer=val2)
                    except Exception as e:
                        dbSession.rollback()
        i += 1
def getPhysics(filename):
    workbook = xw.Book(filename)
    sheet = workbook.sheets[1]
    propertyNum = 20
    i = 4
    alloyType = filename.split("/")[2][0:-5]
    while(True):
        id = str(sheet.range((i, 1)).value)
        if(id == "None"):
            break
        else:
            row = sheet.range((i, 2), (i, propertyNum + 1)).value
            dbSession.add(PhysicsPerformance(id, alloyType,
                                             row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                             row[7], row[8], row[9], row[10], row[11], row[12], row[13],
                                             row[14], row[15], row[16], row[17], row[18], row[19]
                                             ))
            dbSession.commit()
        i += 1
def getMechanical(filename):
    workbook = xw.Book(filename)
    sheet = workbook.sheets[2]
    i = 4
    alloyType = filename.split("/")[2][0:-5]
    while(True):
        id = str(sheet.range((i, 1)).value)
        print(id)
        if(id.endswith(".0")):
            id = id[:-2]
        if (id == "None"):
            break
        else:
            if(alloyType in ["Al合金", "Mg合金", "焊料合金"]):
                row = sheet.range((i, 2), (i, 15)).value
                dbSession.add(MechanicalPerformance(id, alloyType, row[0], row[1], row[2], row[3], row[4],
                                                    row[5], row[6], row[7], row[8], row[9],
                                                    row[10], row[11], row[12], row[13]
                                                    ))
            elif(alloyType == "不锈钢"):
                row = sheet.range((i, 2), (i, 10)).value
                if(row[0] == None):
                    row[0] = "无"
                dbSession.add(MechanicalPerformance(id, alloyType, row[0], "无", row[1], row[2],
                                                    row[3], row[4], row[5], None, row[6], rotateTiredness=row[7],
                                                    hotChangeIntensity=row[8]
                                                    ))
                dbSession.commit()
            elif(alloyType == "单晶高温合金"):
                row = sheet.range((i, 2), (i, 10)).value
                dbSession.add(MechanicalPerformance(id, alloyType, row[0] if row[0] != None else "无", row[1] if row[1] != None else "无",
                                                    row[2], row[3], row[4], cellTem=row[5], cellStrength=row[6], cellTime=row[7],
                                                    cellPer=row[8]))
                dbSession.commit()
            else:
                row = sheet.range((i, 2), (i, 11)).value
                dbSession.add(MechanicalPerformance(id, alloyType, row[0] if row[0] != None else "无", row[1] if row[1] != None else "无",
                                                    row[2], row[3], row[4], cellTem=row[5], cellStrength=row[6], cellTime=row[7],
                                                    cellPer=row[8], sickness=row[9]))
                dbSession.commit()
        i += 1
def transferPhys():
    for file in files:
        getPhysics("./xlsx/" + file)
def transferGredients():
    for file in files:
        getIngredients("./xlsx/" + file)
def transferMechanical():
    for file in files:
        getMechanical("./xlsx/" + file)
if __name__=="__main__":
    transferMechanical()


