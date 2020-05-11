from warn_scraper_al import alabama
from warn_scraper_az import arizona
from warn_scraper_dc import districtcolumbia
from warn_scraper_de import delaware
from warn_scraper_fl import florida
from warn_scraper_in import indiana
from warn_scraper_ks import kansas
from warn_scraper_md import maryland
from warn_scraper_mi import michigan
from warn_scraper_mo import missouri
from warn_scraper_ne import nebraska
from warn_scraper_ne2 import nebraska_two
from combine_ne_scrapers import combine
from warn_scraper_nj import newjersey
from warn_scraper_ny import newyork
from warn_scraper_oh import ohio
from warn_scraper_ok import oklahoma
from warn_scraper_or import oregon
# print("got to oregon")
from warn_scraper_ri import rhodeisland
from warn_scraper_sd import southdakota
from warn_scraper_tn import tennessee
from warn_scraper_ut import utah
from warn_scraper_wa import washington
from warn_scraper_wi import wisconsin
from warn_uploads import send_query
from move_old_data import move_data 

def main():

    alabama()
    arizona()
    districtcolumbia()
    delaware()
    florida()
    indiana()
    kansas()
    maryland()
    michigan()
    missouri()
    nebraska()
    nebraska_two()
    combine()
    newjersey()
    newyork()
    ohio()
    oklahoma()
    oregon()
    rhodeisland()
    southdakota()
    tennessee()
    utah()
    washington()
    wisconsin()
    send_query()
    move_data()
    # try_this()

if __name__ == '__main__':
    main()