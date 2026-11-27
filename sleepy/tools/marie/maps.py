import anim
DANUBE=[(9.99,48.40),(11.4,48.75),(12.1,49.02),(13.46,48.57),(14.29,48.31),(15.33,48.23),(16.37,48.21),(17.1,48.14)]
RHINE=[(7.59,47.56),(7.60,48.0),(7.75,48.58),(8.20,48.95),(8.45,49.45),(8.27,50.0),(7.6,50.3)]
SEINE=[(4.0,48.4),(3.1,48.4),(2.6,48.6),(2.35,48.86),(2.05,48.95),(1.6,49.05)]
MARNE=[(5.15,48.1),(4.36,48.96),(3.4,49.05),(2.88,48.96),(2.45,48.82)]
def m1(out,secs=22):
    stops=[('Vienna',16.37,48.21),('Melk',15.33,48.23),('Munich',11.58,48.14),('Augsburg',10.90,48.37),('Freiburg',7.85,47.99),
           ('Strasbourg',7.75,48.58),('Nancy',6.18,48.69),('Châlons',4.36,48.96),('Reims',4.03,49.26),('Soissons',3.32,49.38),
           ('Compiègne',2.83,49.42),('Versailles',2.13,48.80)]
    return anim.journey_map(out,'From Vienna to Versailles, spring 1770','The bride’s journey, 21 April to 16 May 1770 (route simplified)',
        stops,(1.6,17.2,47.4,50.1),rivers=[DANUBE,RHINE,SEINE,MARNE],secs=secs,
        label_side={'Melk':'t','Munich':'b','Augsburg':'t','Freiburg':'b','Strasbourg':'r','Nancy':'b','Châlons':'b','Reims':'t','Soissons':'b','Compiègne':'t','Versailles':'b','Vienna':'t'})
def m2(out,secs=20):
    stops=[('Paris',2.35,48.86),('Meaux',2.88,48.96),('Châlons',4.36,48.96),('Sainte-Menehould',4.90,49.09),('Varennes',5.03,49.22)]
    return anim.journey_map(out,'The flight to Varennes, June 1791','About 250 km, from midnight to late evening, 20 to 21 June 1791 (route simplified)',
        stops,(1.9,5.9,48.55,49.75),rivers=[SEINE,MARNE],dashed_tail=((5.03,49.22),(5.37,49.52),'Montmédy (never reached)'),secs=secs,
        label_side={'Paris':'b','Meaux':'t','Châlons':'b','Sainte-Menehould':'b','Varennes':'l'})
if __name__=='__main__':
    import sys
    m1('test/m1.mp4',secs=float(sys.argv[1])) ; m2('test/m2.mp4',secs=float(sys.argv[1]))
