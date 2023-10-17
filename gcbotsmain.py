import multiprocessing
import RentRegisterEmail
import ObjectsNoTenant
import NewRentTelegram2
import ThreeiBot
import UZ_Kyiv_Lviv_GC_Bot
import Protokoly

if __name__ == "__main__":
    processes = []

    # Create separate processes for each script and start them concurrently
    processes.append(multiprocessing.Process(target=RentRegisterEmail.run))
    #processes.append(multiprocessing.Process(target=ObjectsNoTenant.run))
    #processes.append(multiprocessing.Process(target=NewRentTelegram2.run))
    #processes.append(multiprocessing.Process(target=ThreeiBot.run))
    #processes.append(multiprocessing.Process(target=UZ_Kyiv_Lviv_GC_Bot.run))
    #processes.append(multiprocessing.Process(target=Protokoly.run))

    # Start all processes
    for process in processes:
        process.start()
