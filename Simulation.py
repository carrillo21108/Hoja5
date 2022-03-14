# Simulacion DES
# Author: Brian Carrillo
# Version 2.0
# Fecha: 13/03/2022

#Importaciones
import simpy
import random
import statistics

#Semilla para random
RANDOM_SEED = 10

def program(name, env, cpu, ram, io, instructions, velocity, llegada):
    #Variables globales
    global total
    global tiempos

    #Memoria necesaria
    cant_memory = random.randint(1,10)

    #Tiempo de llegada en ejecucion
    yield env.timeout(llegada)

    print('%s llegando al SO en %f necesita %d de memoria' % (name, env.now, cant_memory))

    #Almacenamiento del tiempo inicial
    start = env.now

    #Cola memoria - Asignacion de cantidad
    yield ram.get(cant_memory)

    print('%s asignado en espacio de memoria en %f' % (name, env.now))
    print('Espacio en memoria actual: %s' % (ram.level))

    #Estado ready
    state=2

    while(state!=0):

        if(state==2):
            #Request al recurso CPU
            with cpu.request() as req_cpu:
                print('%s en estado "ready", contiene %d instrucciones' % (name, instructions))
                yield req_cpu

                #Tiempo de ejecucion running
                print('%s en estado "running" en %f' % (name, env.now))
                yield env.timeout(1)

                #Disminucion de instrucciones
                if (instructions < velocity):
                    instructions = 0
                else:
                    instructions = instructions - velocity

                print('%s sale de cpu a las %f' % (name, env.now))

                #Proxima cola
                if (instructions != 0):
                    state = random.randint(1, 2)

        elif(state==1):
            #Request al recurso IO
            with io.request() as req_io:

                #Tiempo de ejecucion waiting
                print('%s en estado "waiting", contiene %d instrucciones' % (name, instructions))
                yield req_cpu
                yield env.timeout(random.randint(1,5))

                print('%s sale de la cola "waiting" a las %f' % (name, env.now))
                state = 2

        if(instructions==0):
            #Estado terminado
            state=0
            print('%s en estado "terminated" en %f' % (name, env.now))

    #Desasignacion de memoria RAM
    print('%s desasignado en espacio de memoria en %f' % (name, env.now))
    print('Espacio en memoria actual: %s' % (ram.level+cant_memory))
    yield ram.put(cant_memory)

    #Calculo del tiempo total
    tiempo = env.now - start
    tiempos.append(tiempo)
    print('%s ha tardado %f en ejecucion' % (name, tiempo))
    total = total + tiempo


env = simpy.Environment() #ambiente de simulacion

#Solicitud de datos de ingreso
print('Ingrese la cantidad de procesos: ')
n = input()

print('Ingrese el intervale de llegada: ')
interval = input()

print('Ingrese las instrucciones/unidad de tiempo del cpu: ')
velocity = input()

print('Ingrese la capacidad de la RAM: ')
ram_capacity = input()

print('Ingrese la cantidad de CPUs: ')
cpu_capacity = input()

#Variables de tiempo
total = 0
tiempos = []

#Recursos
cpu = simpy.Resource(env, capacity=int(cpu_capacity)) #CPU como recurso a compartir
io = simpy.Resource(env, capacity=1) #I/O como recurso a compartir

#Contenedor
ram = simpy.Container(env, init=int(ram_capacity), capacity=int(ram_capacity)) #RAM como contenedor

#Semilla
random.seed(RANDOM_SEED)

#Proceso de creacion de programas
for i in range(int(n)):
    #Tiempo de llegada
    llegada = random.expovariate(1.0/int(interval))

    #Creacion de proceso
    env.process(program('Programa %d' % i, env, cpu, ram, io, random.randint(1,10), int(velocity), llegada))

env.run()

#Estadisticas
print ("Tiempo promedio por proceso es: ", total/int(n))
print ("Desviacion estandar del tiempo por proceso es: ", statistics.stdev(tiempos))