import src.UtilsCode.SqlCode as yo


class Info():
    TextDirectory='src/TextInfo/'
    ImgDirectory='src/ImgInfo/'
    def __init__(self,id=-1,name='',tf='', imgf=''):
        self.Id=id
        self.Name=name
        self.TextFile=tf
        self.ImgFile=imgf

    def SaveToDb(self):
        addquery=f'''INSERT INTO `Info`(`TextFile`, `ImgFile`, `Name`) 
            VALUES ('{str(self.TextFile)}', '{str(self.ImgFile)}', '{str(self.Name)}')'''
        yo.execute_query(addquery)