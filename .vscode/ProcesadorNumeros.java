import java.util.*;
import java.util.stream.*;

public class ProcesadorNumeros {
    public static void main(String[] args) {
        Coleccion c = new Coleccion(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10));

        System.out.println("Cuadrados (map): " + c.cuadrados());
        System.out.println("Pares (filter): " + c.pares());
        System.out.println("Suma (reduce): " + c.suma());
    }
}

class Coleccion {
    private List<Integer> datos;

    public Coleccion(List<Integer> datos) {
        this.datos = datos;
    }

    public List<Integer> cuadrados() {
        return datos.stream().map(x -> x * x).collect(Collectors.toList());
    }

    public List<Integer> pares() {
        return datos.stream().filter(x -> x % 2 == 0).collect(Collectors.toList());
    }

    public int suma() {
        return datos.stream().reduce(0, (acc, x) -> acc + x);
    }
}

