from src.UtilsCode.SqlCode import *
from src.UtilsCode.SourceCode import *
import emoji


class Basket():
    def __init__(self, ci='',bi=-1, tp=0, p=[], c=[]):
        self.Client = ci
        self.BasketId=bi
        self.TotalPrice=tp
        self.Products=p
        self.Counts=c

        #self.GetBasketFromDB()


    def __deepcopy__(self, memo):
        id_self = id(self)
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(
                deepcopy(self.Client, memo),
                deepcopy(self.BasketId, memo),
                deepcopy(self.TotalPrice, memo),
                deepcopy(self.Products, memo),
                deepcopy(self.Counts, memo))
            memo[id_self] = _copy
        return _copy

    def GetBasketFromDB(self):
        buff=SelectInTable('baskets', '*', 'clientId', self.Client)
        if buff:
            self.BasketId=buff[0][0]
            self.TotalPrice=buff[0][1]
            Prods=SelectInTable('baskets_products', '*', 'basket_basketID', self.BasketId)
            self.Counts=[]
            self.Products=[]
            for p in Prods:
                self.Counts.append(p[2])
                CP=ClientProduct(p[3])
                self.Products.append(CP)
        else:
            pass
        return self

    def SaveBasketToDB(self):
        try:
            if self.BasketId==-1:
                addquery =f"""
                    INSERT INTO
                        baskets(`clientId`, `totalPrice`) 
                    VALUES
                        ('{str(self.Client)}', {self.TotalPrice})
                    """
                self.BasketId = execute_query(addquery)
            else:
                addquery = f"""
                                        UPDATE
                                            baskets 
                                        SET
                                            `totalPrice`={self.TotalPrice}
                                        WHERE `clientId`={self.Client}
                                        """

                execute_query(addquery)


            addquery2=f"""
                INSERT INTO
                   baskets_products(`basket_basketID`, `products_productID`, `count`, `productKindId`)
               VALUES 
                   ({self.BasketId}, {self.Products[-1].ProductId}, {self.Counts[-1]}, '{str(self.Products[-1].KindId)}')
            """
            execute_query(addquery2)


        except Error as e:
            print(e)


    def AddToBasket(self, product, count):
        self.Products.append(product)
        self.Counts.append(count)
        self.TotalPrice=self.TotalPrice+int(product.Price)*int(count)
        self.SaveBasketToDB()

    def DeleteFromBasket(self):

        deletequery = f"DELETE FROM baskets_products WHERE basket_basketID= {self.BasketId}"
        execute_query(deletequery)

        updatequery=f"UPDATE baskets SET `totalprice`=0 WHERE `clientId`={self.Client}"
        execute_query(updatequery)


        self.Products.clear()
        self.Counts.clear()
        self.TotalPrice=0



    def SaveToFormedDB(self, orderId):
        try:
            addquery = f""" INSERT INTO formed_baskets(`orderId`, `totalPrice`) VALUES ('{str(orderId)}', {self.TotalPrice})"""
            bId=execute_query(addquery)

            i=0
            for p in self.Products:
                addquery=f"""INSERT INTO formed_baskets_products(`basketId`, `productId`, `count`, `kindId`) VALUES
                         ({bId}, {p.ProductId}, {self.Counts[i]}, '{str(p.KindId)}')"""
                execute_query(addquery)
                i+=1
        except Error as e:
            print(e)

    def GetFromFormedDB(self, orderId):
        buff = SelectInTable('formed_baskets', '*', 'orderId', orderId)
        if buff:
            self.BasketId = buff[0][0]
            self.TotalPrice = buff[0][1]
            Prods = SelectInTable('formed_baskets_products', '*', 'basketId', self.BasketId)
            self.Counts = []
            self.Products = []
            for p in Prods:
                self.Counts.append(p[2])
                CP = ClientProduct(p[3])
                self.Products.append(CP)


    def GetStringBasket(self):
        text=''
        i = 0
        for p in self.Products:
            text += '\n\n' + NumToEmoji(i + 1) + ' Товар: ' + p.Name + '\n' + str(
                p.StringKind) + '\nКоличество: ' + str(self.Counts[i]) + ' шт.'
            text += '\n'+emoji.emojize('💰')+'Цена: ' + str(p.Price) + '*' + str(self.Counts[i]) + '=' + str(
                p.Price * self.Counts[i])

            i += 1
        return text