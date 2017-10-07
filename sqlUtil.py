from sqlalchemy import Column, String, Text, Float, Integer, PrimaryKeyConstraint, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#ORM基类
Base = declarative_base()

class Ingredient(Base):
    __tablename__ = "ingredient"
    __table_args__ = (
        PrimaryKeyConstraint("alloyName", "elementName"),
    )
    alloyName = Column(String(length=30, convert_unicode=True))
    elementName = Column(String(length=3, convert_unicode=True))
    minPer = Column(Float)
    maxPer = Column(Float)
    misc = Column(Text)
    def __init__(self, alloyName=None, elementName=None, minPer=None, maxPer=None, misc=None):
        self.alloyName = alloyName
        self.elementName = elementName
        self.minPer = minPer
        self.maxPer = maxPer
        self.misc = misc
    def __getitem__(self, item):
        return getattr(self, item)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PhysicsPerformance(Base):
    __tablename__ = "physics"
    __table_args__ = (
        PrimaryKeyConstraint("alloyName"),
    )
    alloyName = Column(String(length=30, convert_unicode=True))
    alloyType = Column(String(length=10))
    picPath = Column(Text)
    solidMelt = Column(Float)
    liquidMelt = Column(Float)
    density = Column(Float)
    densityK = Column(Float)
    modulus = Column(Float)
    modulusK = Column(Float)
    poisson = Column(Float)
    poissonK = Column(Float)
    heatConduct = Column(Float)
    heatConductK = Column(Float)
    elecConduct = Column(Float)
    elecConductK = Column(Float)
    heatDilation = Column(Float)
    heatDilationK = Column(Float)
    heatHan = Column(Float)
    heatHanK = Column(Float)
    heatCapacity = Column(Float)
    heatCapacityK = Column(Float)
    latentHeat = Column(Float)
    shrink = Column(Float)
    def __init__(self, alloyName=None, alloyType=None, picPath=None, solidMelt=None,
                 liquidMelt=None, density=None, densityK=None, modulus=None, modulusK=None,
                 poisson=None, poissonK=None, heatConduct=None, heatConductK=None, elecConduct=None,
                 elecConductK=None, heatDilation=None, heatDilationK=None, heatHan=None,
                 heatHanK=None, heatCapacity=None, heatCapacityK=None, latentHeat=None, shrink=None):
        self.alloyName = alloyName
        self.alloyType = alloyType
        self.picPath = picPath
        self.solidMelt = solidMelt
        self.liquidMelt = liquidMelt
        self.density = density
        self.densityK = densityK
        self.modulus = modulus
        self.modulusK = modulusK
        self.poisson = poisson
        self.poissonK = poissonK
        self.heatConduct = heatConduct
        self.heatConductK = heatConductK
        self.elecConduct = elecConduct
        self.elecConductK = elecConductK
        self.heatDilation = heatDilation
        self.heatDilationK = heatDilationK
        self.heatHan = heatHan
        self.heatHanK = heatHanK
        self.heatCapacity = heatCapacity
        self.heatCapacityK = heatCapacityK
        self.latentHeat = latentHeat
        self.shrink = shrink
    def __getitem__(self, item):
        return getattr(self, item)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class MechanicalPerformance(Base):
    __tablename__ = "mechanical"
    __table_args__ = (
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    alloyName = Column(String(length=30, convert_unicode=True))
    craft = Column(Text)
    testTem = Column(Text)
    stretchU = Column(Integer)
    stretchY = Column(Integer)
    stretchP = Column(Float)
    sickness = Column(Integer)
    compressIntensity = Column(Float)
    compressShuxing = Column(Text)
    corrodeSpeed = Column(Text)
    tiredR1 = Column(Text)
    tiredR0 = Column(Text)
    corrodeSpeedKIC = Column(Text)
    changeK = Column(Text)
    changeN = Column(Text)
    rotateTiredness = Column(Text)
    hotChangeIntensity = Column(Text)
    cellTem = Column(Integer)
    cellStrength = Column(Integer)
    cellTime = Column(Integer)
    cellPer = Column(Float)

    def __init__(self, alloyName=None, craft=None, testTem=None, stretchU=None, stretchY=None, stretchP=None,
                 sickness=None, compressIntensity=None, compressShuxing=None, corrodeSpeed=None, tiredR1=None,
                 tiredR0=None, corrodeSpeedKIC=None, changeK=None, changeN=None, rotateTiredness=None,
                 hotChangeIntensity=None, cellTem=None, cellStrength=None, cellTime=None, cellPer=None):
        self.alloyName = alloyName
        self.craft = craft
        self.testTem = testTem
        self.stretchU = stretchU
        self.stretchP = stretchP
        self.stretchY = stretchY
        self.sickness = sickness
        self.compressIntensity = compressIntensity
        self.compressShuxing = compressShuxing
        self.corrodeSpeed = corrodeSpeed
        self.tiredR0 = tiredR0
        self.tiredR1 = tiredR1
        self.corrodeSpeedKIC = corrodeSpeedKIC
        self.changeK = changeK
        self.changeN = changeN
        self.rotateTiredness = rotateTiredness
        self.hotChangeIntensity = hotChangeIntensity
        self.cellTem = cellTem
        self.cellPer = cellPer
        self.cellStrength = cellStrength
        self.cellTime = cellTime
    def __getitem__(self, item):
        return getattr(self, item)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

def initDB():
    engine = create_engine('sqlite:///alloy.db')
    dbSession = scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=engine))
    Base.metadata.create_all(bind=engine)
    return dbSession