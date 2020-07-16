
from warn_uploads import send_query
from find_broken_crons import broken_crons
from move_old_data import move_data 

def main():
    
    broken_crons()
    send_query()
    move_data()

if __name__ == '__main__':
    main()