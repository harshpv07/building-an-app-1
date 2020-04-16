from flask import Flask, render_template,request
import requests,json    


app = Flask(__name__)

@app.route('/',methods = ["GET","POST"])
def root():
    import pandas as pd
    import numpy as np
    dataset = pd.read_csv("Data/covid_19_india2.csv")
    dataset1 = pd.read_csv("Data/HospitalBedsIndia.csv")

    result = pd.merge(dataset,dataset1,left_on = 'State/UnionTerritory',right_on = 'State/UT',how = 'left')
    dataset2 = pd.read_csv("Data/population_india_census2011.csv")
    resultfinal  = pd.merge(result,dataset2,left_on = 'State/UnionTerritory',right_on = 'State / Union Territory',how = 'left')
    result = result.drop(columns=["Unnamed: 12","Unnamed: 13"])
    newdf = pd.DataFrame()

    l = len(resultfinal) - 1
    temparr = []
    popu_arr = []
    Density = []
    Density_clean = []
    Sexratio = []
    curedpercent = []
    deathpercent = []
    urbanbedspercent = []
    ruralbedpercent = []
    affectedpercent = []
    count = 0
    while(l>0):
        if(resultfinal["State/UnionTerritory"][l] not in temparr):
            temparr.append(resultfinal["State/UnionTerritory"][l])
            popu_arr.append(resultfinal["Urban population"][l])
            Density.append(resultfinal["Density"][l])
            Sexratio.append(resultfinal["Sex Ratio"][l])
            curedpercent.append(resultfinal["Cured"][l] / resultfinal["Confirmed"][l])
            deathpercent.append(resultfinal["Deaths"][l] / resultfinal["Confirmed"][l])
            urbanbedspercent.append(((resultfinal["NumUrbanBeds_NHP18"][l] + (float(resultfinal["NumPublicBeds_HMIS"][l]) * 0.7)) * 0.12) / (resultfinal["Urban population"][l] - resultfinal["Confirmed"][l]))
            ruralbedpercent.append(((resultfinal["NumRuralBeds_NHP18"][l] + (float(resultfinal["NumPublicBeds_HMIS"][l]) * 0.3)) * 0.08) / (resultfinal["Rural population"][l] - resultfinal["Confirmed"][l]))
            affectedpercent.append(resultfinal['Confirmed'][l]/(resultfinal["Urban population"][l] +resultfinal["Rural population"][l]))
            count+=1
            if(count == 23):
                break
            
            l = l - 1
    for g in range(len(Density)):
        if(g != 6):
            h = str(Density[g])
            k = h.split("/")
            
            Density_clean.append(float(k[0].replace(',', '')))
        else:
            Density_clean.append(306)
            
    #print(Density)
    newdf.insert(0,"State/UnionTerritory",temparr)
    newdf.insert(1,"Urban population",popu_arr)
    newdf.insert(2,"Density",Density_clean)
    newdf.insert(3,"Sex ratio",Sexratio)
    newdf.insert(4,"Cured_percent",curedpercent)
    newdf.insert(5,"Death_percent",deathpercent)
    newdf.insert(6,"Urban_Bed_percent",urbanbedspercent)
    newdf.insert(7,"Rural_Bed_percent",ruralbedpercent)
    newdf.insert(8,"Affected_percent",affectedpercent)


    newdf['Urban population'].fillna((newdf['Urban population'].mean()), inplace=True)
    #newdf['Density'].fillna((newdf['Density'].mean()), inplace=True)
    newdf['Sex ratio'].fillna((newdf['Sex ratio'].mean()), inplace=True)
    newdf['Urban_Bed_percent'].fillna((newdf['Urban_Bed_percent'].mean()), inplace=True)
    newdf['Rural_Bed_percent'].fillna((newdf['Rural_Bed_percent'].mean()), inplace=True)
    newdf['Density'].fillna((newdf['Density'].mean()), inplace=True)
    newdf['Affected_percent'].fillna((newdf['Affected_percent'].mean()), inplace=True)


    from sklearn.preprocessing import StandardScaler,MinMaxScaler
    scaler = MinMaxScaler()
    newdf['Urban population'] = scaler.fit_transform(newdf['Urban population'].values.reshape(-1,1)) 
    newdf['Sex ratio'] = scaler.fit_transform(newdf['Sex ratio'].values.reshape(-1,1)) 
    newdf['Density'] = scaler.fit_transform(newdf['Density'].values.reshape(-1,1)) 
    res = []
    for k in range(len(newdf)):
        tl = []
        res.append(((((newdf["Urban population"][k]*0.6)+newdf["Density"][k] + newdf["Affected_percent"][k]) + newdf["Death_percent"][k])/(((newdf["Sex ratio"][k]*0.5)+newdf["Urban_Bed_percent"][k]+newdf["Rural_Bed_percent"][k]) + newdf["Cured_percent"][k])))
    newdf.insert(9,"res",res)
    tempdf = newdf.sort_values(by=['res'])
    l = ""
    col = ""
    indexscore = ""
    desc = ""
    arr = []
    for k in range(len(tempdf)):
        arr.append(tempdf["State/UnionTerritory"][k])
    #arr = ["Tamil Nadu","Kerala","Mizoram"]
    if(request.method == "POST"):
        us = request.form["loc"]
        for i in range(len(tempdf)):
            if(tempdf["State/UnionTerritory"][i] == us):
                f = tempdf["res"][i]
                indexscore = round(f,2)
                if(f>1.5):
                    l = str("Very Bad Situation")
                    desc = "Stay home, monitor your health, and practice social distancing for 14 days. Social distancing means staying out of crowded places, avoiding group gatherings, and maintaining distance (approximately 6 feet or 2 meters) from others when possible and also maintain personal hygiene"
                    col = "card text-white bg-danger mb-3"
                elif(f<=1.5 and f>0.65):
                    l = str("Sitution is moderatly controlled")
                    desc = "Situation is still bad. Would recommend you to stay at home and practise social distancing. "
                    col = "card text-white bg-warning mb-3"
                elif(f<=0.65):
                    l = str("Situation is under control by the govt")
                    desc = "It is relatively safe for you to head outside for essential items. But take precautions like practising social distancing and also maintain personal hygiene"
                    col = "card text-white bg-success mb-3"
                print(l)
    return render_template('index.html',data = l,dat = tempdf,col = col,arr = arr,f=indexscore,desc = desc)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)