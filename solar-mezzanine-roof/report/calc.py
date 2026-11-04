"""Sizing, BOQ and financial model for the rooftop PV report. Prints JSON used by build_report.py."""
import json
N=299; P=620; KWP=N*P/1000
AC=160.0
SY=1480                      # kWh/kWp/yr year-1 specific yield (PR included)
TARIFF=0.12                  # USD/kWh avoided grid energy (assumption)
ESC=0.02                     # tariff escalation / yr
DEG1, DEG=0.01, 0.004        # TOPCon degradation
DISC=0.10
LOAD_YR=12_000_000
boq=[ # (item, qty text, unit cost text, amount)
 ("PV modules, 620 Wp bifacial TOPCon, Tier-1 (landed, cleared)", f"{N} nos", "USD 0.150/Wp", round(KWP*1000*0.150)),
 ("String inverters, 80 kW, 1,100 V, multi-MPPT (incl. comms)", "2 nos", "USD 4,800 each", 9600),
 ("Mounting structure, aluminium, 10° tilt, ballasted/anchored, incl. roof pads", f"{KWP:.1f} kWp", "USD 0.090/Wp", round(KWP*1000*0.090)),
 ("DC system: 6 mm² PV cable, MC4 connectors, DC isolators, SPD Type II", "Lot", "USD 0.040/Wp", round(KWP*1000*0.040)),
 ("AC system: AC combiner panel, 250 A MCCB, 4C×120 mm² Cu XLPE to main LV board (≈80 m), cable tray", "Lot", "Lump sum", 9500),
 ("Zero-export controller, CT/power meter, data logger & remote monitoring", "1 set", "Lump sum", 3500),
 ("Earthing, equipotential bonding & lightning protection integration", "Lot", "Lump sum", 3000),
 ("Roof walkways, safety lifeline & water point for cleaning", "Lot", "Lump sum", 3500),
 ("Installation, testing & commissioning (labour, supervision, lifting)", f"{KWP:.1f} kWp", "USD 0.060/Wp", round(KWP*1000*0.060)),
 ("Engineering: detailed design, structural check of slab, PVsyst, as-builts", "Lot", "Lump sum", 4000),
 ("Approvals & utility interface (ERA / UEDCL), O&M manuals, training", "Lot", "Lump sum", 2000),
 ("Transport, logistics & customs clearing", "Lot", "Lump sum", 4000),
]
sub=sum(b[3] for b in boq); cont=round(sub*0.07); capex=sub+cont
om0=round(capex*0.012)
gen=[]; sav=[]; cash=[-capex]; cum=[-capex]; rows=[]
for y in range(1,26):
    e=KWP*SY*(1-DEG1)*(1-DEG)**(y-1) if y>1 else KWP*SY
    t=TARIFF*(1+ESC)**(y-1)
    s=e*t; om=om0*(1.03)**(y-1); inv=9600*1.0 if y==12 else 0
    cf=s-om-inv
    gen.append(e); sav.append(s); cash.append(cf); cum.append(cum[-1]+cf)
    rows.append((y,round(e),round(t,4),round(s),round(om),inv,round(cf),round(cum[-1])))
npv=sum(c/(1+DISC)**i for i,c in enumerate(cash))
def irr(c):
    lo,hi=0.0,2.0
    for _ in range(200):
        m=(lo+hi)/2; v=sum(x/(1+m)**i for i,x in enumerate(c))
        lo,hi=(m,hi) if v>0 else (lo,m)
    return m
pb=next(i for i,c in enumerate(cum) if c>=0); prev=cum[pb-1]; pbf=pb-1+(-prev)/(cum[pb]-prev)
disc_e=sum(g/(1+DISC)**(i+1) for i,g in enumerate(gen))
disc_c=capex+sum((om0*1.03**i)/(1+DISC)**(i+1) for i in range(25))+9600/(1+DISC)**12
out=dict(N=N,P=P,KWP=KWP,AC=AC,SY=SY,TARIFF=TARIFF,ESC=ESC,DISC=DISC,LOAD_YR=LOAD_YR,
 boq=boq,sub=sub,cont=cont,capex=capex,usd_wp=capex/(KWP*1000),om0=om0,
 y1_gen=gen[0],y1_sav=sav[0],gen25=sum(gen),sav25=sum(sav),npv=npv,irr=irr(cash),payback=pbf,
 lcoe=disc_c/disc_e,share=gen[0]/LOAD_YR,cum=cum,rows=rows)
# sensitivity on tariff
out["sens"]=[]
for t in (0.09,0.10,0.12,0.14,0.16):
    c=[-capex]+[KWP*SY*((1-DEG1)*(1-DEG)**(y-1) if y>1 else 1)*t*(1+ESC)**(y-1)-om0*1.03**(y-1)-(9600 if y==12 else 0) for y in range(1,26)]
    cu=0;p=None
    for i,x in enumerate(c):
        cu+=x
        if cu>=0 and p is None: p=i-1+(-(cu-x))/x
    out["sens"].append((t,p,irr(c),sum(x/(1+DISC)**i for i,x in enumerate(c))))
json.dump(out,open(__file__.replace("calc.py","calc.json"),"w"),indent=1)
print(f"kWp {KWP:.1f} capex {capex} ({capex/KWP/1000:.3f}/Wp) y1 gen {gen[0]:.0f} sav {sav[0]:.0f} payback {pbf:.1f} IRR {irr(cash)*100:.1f}% NPV {npv:.0f} LCOE {disc_c/disc_e:.3f} share {gen[0]/LOAD_YR*100:.2f}%")
for s in out["sens"]: print(s)
