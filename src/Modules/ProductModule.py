from src.UtilsCode.SqlCode import *


class Product():
    def __init__(self, id=-1):
        self.ProductId=id
        buff=SelectInTable('products', '*', 'productId', self.ProductId)
        if buff:
            self.Name=buff[0][2]
            self.Type=buff[0][1]
            self.Description=buff[0][5]
        else:
            self.Name = ''
            self.Type = ''
            self.Description = ''


class MainProduct(Product):
    def __init__(self, id=-1):
        Product.__init__(self, id)
        self.Present=True
        self.Photo=''
        self.Kinds=[]
        self.Prices=[]
    #
    #
    #
    # def __init__(self, id=-1,type='',name='', pht='', dscrpt=''):
    #     self.ProductId=id
    #     self.Type=type
    #     self.Name = name
    #     self.Present=True
    #     self.Photo=pht
    #     self.Description=dscrpt
    #     self.Kinds=[]
    #     self.Prices=[]


    def SetFromDB(self, DB, KINDS):
        self.ProductId=DB[0]
        self.Type=DB[1]
        self.Name=DB[2]
        self.Description = DB[5]
        self.Present=DB[3]
        self.Photo=DB[4]
        for k in KINDS:
            self.Kinds.append(int(k[0]))
            self.Prices.append(int(k[3]))



    def AddToDB(self, producttype, productName, photo, dscrp):
        try:
            addquery = f"""
                        INSERT INTO
                            products(`productType`, `productName`, `present`, `photo`, `description`) 
                        VALUES
                            ('{str(producttype)}', '{str(productName)}', {True}, {str(photo)}, '{str(dscrp)}')
                        """
            execute_query(addquery)
            return True
        except Exception as e:
            print(e)
            return False

    def UpdateProduct(self):
        try:
            updateQuery1=f'''UPDATE products SET 
                    `productName`='{self.Name}', `present`={self.Present}, `photo`='{self.Photo}', `description`='{self.Description}'
        WHERE `productId`={self.ProductId}'''
            execute_query(updateQuery1)
            return True
        except Exception as e:
            print(e)
            return False

    def GetProductString(self):
        text = str(self.Name)
        text += '\n\n' + self.Description + '\n'
        i = 0
        text += '\n💲 Цены:'
        for k in self.Kinds:
            text += '\n' + str(GetKindById(k)[0][2]) + ' - ' + str(self.Prices[i]) + ' руб.'
            i += 1

        return text

class ClientProduct(Product):
    def __init__(self, kindId=-1):
        id=SelectInTable('kinds', 'productId', 'kindId', kindId)[0][0]
        Product.__init__(self, id)
        self.KindId=kindId
        self.Price=SelectInTable('kinds', 'price', 'kindId', kindId)[0][0]
        self.StringKind=SelectInTable('kinds', 'kind', 'kindId', kindId)[0][0]




def GetKindById(id):
    try:
        k=SelectInTable('kinds', '*', 'kindId', id)
        return k
    except Exception as e:
        print(e)
        return None

def GetProductNameById(id):
    name=SelectInTable('products', 'productName', 'productId', int(id))
    return str(name[0][0])

