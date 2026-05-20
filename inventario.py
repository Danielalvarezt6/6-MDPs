"""
Para desarrollar el problema del inventario.

"""

from MDPs import MDP, iteracion_valor
import math

class Inventario(MDP):
    """
    Clase que representa un MDP para el problema de inventario.
    
    El gerente decide cuántas unidades pedir para minimizar costos de 
    almacenamiento y backlogging, maximizando la ganancia.
    
    """    
    
    def __init__(self, gamma, lambda_, precio_venta=150, costo_compra=80, 
                 costo_fijo_pedido=40, costo_almacen=5, costo_backlog=15, 
                 capacidad=20, backlog_max=10, k_max=20):
        """
        parámetros:
        gamma: factor de descuento (0.95)
        lambda_: media de la demanda poisson (4)
        precio_venta, costo_compra, costo_fijo_pedido, costo_almacen, costo_backlog
        capacidad: máxima unidades en almacén (20)
        backlog_max: límite inferior del inventario (negativo), ej. 10 -> -10
        k_max: truncamiento de la distribución poisson (probabilidad acumulada ~1)
        """         
        # generar espacio de estados: desde -backlog_max hasta capacidad
        estados = list(range(-backlog_max, capacidad + 1))

        # llamar al constructor de la clase base mdp
        super().__init__(estados, gamma)
        
        # guardar parámetros adicionales
        self.lambda_ = lambda_
        self.precio_venta = precio_venta
        self.costo_compra = costo_compra
        self.costo_fijo_pedido = costo_fijo_pedido
        self.costo_almacen = costo_almacen
        self.costo_backlog = costo_backlog
        self.capacidad = capacidad
        self.backlog_max = backlog_max
        self.k_max = k_max

        # precalcular probabilidades poisson hasta k_max
        self.poisson_probs = {}
        total = 0.0
        for k in range(k_max + 1):
            p = math.exp(-lambda_) * (lambda_ ** k) / math.factorial(k)
            self.poisson_probs[k] = p
            total += p
        # normalizar para que sume exactamente 1 (aunque la suma ya es muy cercana)
        for k in self.poisson_probs:
            self.poisson_probs[k] /= total
    
    def acciones_legales(self, s):
        """
        devuelve lista de acciones factibles dado el estado s.
        la acción es la cantidad a pedir (entero >= 0).
        restricción: s + a <= capacidad (no exceder almacén al recibir el pedido).
        """
        if s > self.capacidad:
            return [0]  # seguridad, no debería ocurrir
        max_a = self.capacidad - s
        return list(range(0, max_a + 1))

    def prob_transicion(self, s, a, s_):
        """
        probabilidad de transición de s a s_ con acción a.
        acumula la probabilidad de la cola en el estado límite inferior.
        """
        if s_ not in self.estados:
            return 0.0
            
        d = s + a - s_
        if d < 0:
            return 0.0 # no es posible que el inventario crezca sin pedir

        # si el estado de llegada no es el limite inferior (-10)
        if s_ > -self.backlog_max:
            return self.poisson_probs.get(d, 0.0)
            
        # si el estado de llegada es el límite inferior (-10)
        # acumulamos la probabilidad de que la demanda sea d o mayor, lo que llevaría a s' <= -10
        elif s_ == -self.backlog_max:
            # 1.0 menos la probabilidad de todas las demandas menores a d
            prob_menores = sum(self.poisson_probs.get(k, 0.0) for k in range(d))
            return max(0.0, 1.0 - prob_menores)

    def recompensa(self, s, a, s_):
        """
        recompensa inmediata por la transición (s, a, s_).
        se calcula con la demanda d = s + a - s_ (determinística dada la transición).
        incluye ingresos por ventas, costos de pedido, almacenamiento, backlog
        y pérdida de oportunidad (margen no ganado).
        """
        d = s + a - s_
        if d < 0:
            return -1e9  # transición imposible (castigo grande)

        I = s + a
        ventas = min(d, max(0, I))
        ingresos = self.precio_venta * ventas

        # costo de pedido
        if a > 0:
            costo_pedido = self.costo_fijo_pedido + self.costo_compra * a
        else:
            costo_pedido = 0

        # costo de almacenamiento (por inventario final positivo)
        costo_almacen = self.costo_almacen * max(s_, 0)

        # costo de backlog (por inventario final negativo)
        costo_backlog = self.costo_backlog * max(-s_, 0)

        # pérdida por demanda no satisfecha en el momento (margen no ganado)
        margen_unitario = self.precio_venta - self.costo_compra  # 70
        demanda_no_servida = d - ventas
        perdida_oportunidad = margen_unitario * demanda_no_servida

        recomp = ingresos - costo_pedido - costo_almacen - costo_backlog - perdida_oportunidad
        return recomp

    def es_terminal(self, s):
        """
        como el ciclo de inventario nunca se acaba y el negocio opera 
        todos los días, ningún estado es el final. siempre es false.
        """
        return False

if __name__ == "__main__":

    inventario = Inventario(0.9, 0.5, ...)  #TODO: Agregar lo que se requiera

    pi_star, V = iteracion_valor(inventario, ...) #TODO: Agregar lo que se requiera

    print("-" * 60)
    print("Estado".center(20) + "Acción".center(20) + "Valor".center(20))
    print("-" * 60 )
    for s in pi_star:
        print(f"{s:^20}{pi_star[s]:^20}{V[s]:^20.2f}")
    print("-" * 60)


"""
Contesta las preguntas aquí mismo (has espacio entre las preguntas):

1. ¿Cómo se comporta las transiciones y las ganancias para casos específicos de $s$ y $a$? 
2. ¿Qué psa si hay mucho almacen? 
3. ¿Que pasa si hay muy poco o estamos sin almacen? 
4. ¿Existe un punto donde la ganancia sea máxima?  
---
5. ¿Cómo se ve la política óptima? ¿Tiene sentido?
6. ¿Como se comporta la función de valor de estado V(s)?
7. ¿Cómo cambiaría la política si la variabilidad de la demanda (lambda) aumenta de 4 a 8?

"""