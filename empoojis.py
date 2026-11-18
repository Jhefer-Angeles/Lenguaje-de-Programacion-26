from datetime import datetime

print(f"fecha y hora:{datetime.now()}")
print("clase con herencia")

class Comida:
    def preparar(self):
        print("Comida preparada")

class Hamburguesa(Comida):
    pass  

class Pizza(Comida):
    pass  

class Papas(Comida):
    pass  

hamburguesa = Hamburguesa()  
hamburguesa.preparar()       

pizza = Pizza()             
pizza.preparar()            

papas = Papas()             
papas.preparar()              