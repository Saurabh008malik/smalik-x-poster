import anim
JORDAN=[(35.64,33.05),(35.60,32.90),(35.57,32.70),(35.55,32.45),(35.53,32.20),(35.52,32.00),(35.55,31.76)]
GALILEE=[(35.52,32.86),(35.60,32.90),(35.65,32.82),(35.63,32.72),(35.57,32.70),(35.52,32.76),(35.52,32.86)]
DEADSEA=[(35.55,31.76),(35.58,31.50),(35.52,31.40),(35.42,31.45),(35.45,31.70),(35.55,31.76)]
COAST1=[(35.10,33.05),(34.98,32.82),(34.90,32.50),(34.75,32.05),(34.55,31.70),(34.45,31.50)]
COAST2=COAST1+[(34.20,31.30),(33.80,31.13),(33.20,31.10),(32.57,31.04),(32.30,31.25),(31.90,31.50),(31.00,31.60),(30.30,31.45),(29.90,31.20)]
NILE_E=[(31.23,30.05),(31.40,30.60),(31.60,31.05),(31.81,31.42)]
NILE_W=[(31.23,30.05),(30.95,30.50),(30.65,31.00),(30.42,31.40)]
NILE_S=[(31.25,29.70),(31.23,30.05)]
def m1(out,secs=22):
    stops=[('Nazareth',35.30,32.70),('Jezreel valley',35.40,32.55),('Jordan valley',35.53,32.25),('Jericho',35.44,31.86),('Jerusalem',35.23,31.78),('Bethlehem',35.20,31.70)]
    return anim.journey_map(out,'From Nazareth to Bethlehem','One likely path, by the Jordan valley (about 90 miles). The gospels do not record the route.',
        stops,(34.55,36.05,31.40,33.05),rivers=[JORDAN,GALILEE,DEADSEA,COAST1],secs=secs,
        label_side={'Nazareth':'t','Jezreel valley':'r','Jordan valley':'r','Jericho':'r','Jerusalem':'l','Bethlehem':'b'})
def m2(out,secs=20):
    stops=[('Bethlehem',35.20,31.70),('Gaza',34.46,31.50),('El-Arish',33.80,31.13),('Pelusium',32.57,31.04)]
    return anim.journey_map(out,'Into Egypt','One likely road, along the coast. Matthew does not say where in Egypt they stayed.',
        stops,(29.70,35.80,29.70,32.30),rivers=[COAST2,NILE_E,NILE_W,NILE_S,DEADSEA],dashed_tail=((32.57,31.04),(31.40,30.70),'the Nile delta'),secs=secs,
        label_side={'Bethlehem':'r','Gaza':'t','El-Arish':'b','Pelusium':'b'})
