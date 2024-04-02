
import logging



#logging.basicConfig(level=logging.DEBUG)         
#logging.basicConfig(level=logging.INFO)          
#logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.ERROR)          

LevelState=logging.ERROR
#LevelState=logging.INFO

#logging.basicConfig(filename='example.log', encoding='utf-8', level=LevelState)
logging.basicConfig( level=LevelState)
logging.debug('This message should go to the log file')         
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')   


print(LevelState)

if LevelState ==  logging.INFO:
    print("INFO")