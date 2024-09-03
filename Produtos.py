class Produto:
    def __init__(self, name: str, code:str, category:str, quantity:int, price:float, description:str,supplier:str ):
        self.name= name
        self.code = code
        self.category = category
        self.quantity = quantity
        self.price = price
        self.description = description
        self.supplier = supplier

    def update_price(self, price:float):
        self.price = float(price)
    def update_description(self, desc:str):
        self.desc = desc
    def update_category(self,category:str ):
        self.category = category
    def update_supplier(self, supplier:str):
        self.supplier = supplier
    def remove_from_invetory(self, qtd:int):
        self.quantity = self.quantity- qtd
    def update_invetory(self, qtd:int):
        self.quantity =  qtd
    def add_to_invetory(self, qtd:int):
        self.quantity = self.quantity+ qtd


# prod1 = Produto("xpto", "123","batata", 30, 45.90,"description", "MAGALU")

# print(prod1.price)
# prod1.update_price(10)

# print(prod1.price)