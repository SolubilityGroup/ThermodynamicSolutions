import sys 
import pandas as pd
import numpy as np
from IPython.display import display, Math, Latex, Markdown,HTML
from IPython.core.display import display, HTML
from google.colab import files
from scipy.optimize import curve_fit
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


def data_upload(name):
    nombre = name
    uploaded = files.upload()
    for fn in uploaded.keys():
        nombre = fn
    return nombre


class dataset:

    """class to enter the dataset according to the format of the standard table in 
    format "xlsx" or "csv", `data("url")`:enter data from a url,`data()`:enter 
    the data from the pc.
    """
    def __init__(self,url):
        global URL
        global entorno
        self.url = url
        entorno = str(sys.executable)
        if self.url == "" and entorno == "/usr/bin/python3" :
            name = data_upload(self.url)
            URL= "/content/"+ name
        else:
            URL =self.url
       
   
    @property
    def show(self):

        L = URL.split(".")

        if L[-1]=="csv":
            df = pd.read_csv(URL)
        if L[-1]=="xlsx":
            df = pd.read_excel(URL)
        return df
    
    
    @property
    def temperature_values(self):
        df = self.show
        if "x1" in df.columns or "x2" in df.columns:
            temp = df.drop(['x1',"x2"], axis=1).columns[1:]
        else:
            temp = df.columns[1:]
        return pd.DataFrame({"T":temp})
    
    @property
    def mass_fractions(self):
        df = self.show
        fm = df["w1"]
        df_fm = pd.DataFrame({"w1":fm})
        return df_fm

    @property
    def experimental_values(self):
        df = self.show
        if "x1" in df.columns or "x2" in df.columns:
            df_ev = df.drop(['x1',"x2"], axis=1)
        else:
            df_ev = df
        return df_ev


    def molar_fractions(self,mf):
        if mf == "x1":
            df_mf = print("Does not exist mole fraction for "+ mf)
        if mf == "x2":
            df_mf = print("Does not exist mole fraction for "+ mf)
        if mf == "x3":
            df_mf = self.experimental_values
        return df_mf


class model:

    """class to choose the solubility model for a dataset with melting temperature Tf 
    and enthalpy of fusion ΔHf.
    # solubility models
    -----------------
    `modified_apelblat(dataset)`
    `vant_hoff(dataset)`
    `vant_hoff_yaws(dataset)`
    `modified_wilson(dataset)`
    `buchowski_ksiazaczak(dataset,Tf)`
    `NRTL(dataset,Tf,ΔHf)`
    `wilson(dataset,Tf,ΔHf)`
    `weilbull(dataset,Tf,ΔHf)`
    """

    def __init__(self):
        self.modified_apelblat    = self.modified_apelblat()
        self.vant_hoff            = self.vant_hoff()
        self.vant_hoff_yaws       = self.vant_hoff_yaws()
        self.modified_wilson      = self.modified_wilson()
        self.buchowski_ksiazaczak = self.buchowski_ksiazaczak()
        self.NRTL                 = self.NRTL()
        self.wilson               = self.wilson()
        self.weibull              = self.weibull()




    #CLASE PARA EL MODELO DE SOLUBILIDAD APELBLAT MODIFICADO

    class modified_apelblat(dataset):
        def __init__(self, url):
            self.url = url

        
        @property
        def show(self):
            L = URL.split(".")

            if L[-1]=="csv":
                df = pd.read_csv(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
            
            if L[-1]=="xlsx":
                df = pd.read_excel(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)

            return DFF

        @property
        def temperature_values(self):
            df = self.show
            tem = df["T"]
            return pd.DataFrame({"T":tem})
                    

        @property
        def mass_fractions(self):
            df = self.show
            mf = df.columns[1:]
            return pd.DataFrame({"w1":mf})

        @property
        def equation(self):
            salida = display(HTML('<h2> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Modified Apelblat Model Equation</h2>'))
            display(Math(r'$$\ln(x_3) = A + \dfrac{B}{T} + C \cdot \ln T$$'))
            return salida

    
        def __kernel(self, method="lm",p0 =[1,1,1], maxfev=20000, sd = False, opt = "calculate"):
            
            def fT(T,A,B,C):
                return np.exp(A + B/T + C*np.log(T))


            df = self.show
            W  = df.columns[1:].tolist()
            Temp = df["T"].values
            

            para_A,para_B,para_C = [],[],[]
            desv_A,desv_B,desv_C = [],[],[]
            desv_para_A,desv_para_B,desv_para_C = [],[],[]
            L_para,L_desv,L_desv_para= [para_A,para_B,para_C],[desv_A,desv_B,desv_C],[desv_para_A,desv_para_B,desv_para_C]
            
            for i in  W:
                xdat = df[i]
                Tdat = df["T"]
                popt, mcov= curve_fit(fT,Tdat,xdat,method= "lm",p0=p0,maxfev=20000)
                
                for j in L_para:
                    j.append(popt[L_para.index(j)])
                    
                for k in L_desv:
                    k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))
                    
                for l in L_desv_para:
                    l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

        
            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in W:

                wdat = len(Temp)*[i]
                Wdat = wdat

                tdat = Temp
                Tdat = tdat.tolist()

                x3_exp = df[i].values
                X3_exp =  x3_exp.tolist()

                x3_cal = fT(tdat,para_A[W.index(i)],para_B[W.index(i)],para_C[W.index(i)])
                X3_cal = x3_cal.tolist()

                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w    += Wdat
                C_temp += Tdat
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w   = np.array(C_w)
            arr_temp = np.array(C_temp)
            arr_exp = np.array(C_exp)
            arr_cal = np.array(C_cal)
            arr_RD  = np.array(C_RD )

            dataframe = pd.DataFrame({"w1":arr_w,'RD':arr_RD})

            MAPES = []

            for i in range(len(W)):

                df_mask = dataframe['w1'] == W[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["w1"])
                MAPES.append(MRDP)

            df_para      = pd.DataFrame({"w1":W,'A':para_A,'B':para_B,'C':para_C,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"w1":W,'A ± σ':desv_para_A,'B ± σ':desv_para_B,'C ± σ':desv_para_C,"MRD%":MAPES})
            df_cal       = pd.DataFrame({"w1":arr_w,'T': arr_temp,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return  df_kernel 

        def parameters(self, method="lm",p0 =[1,1,1], maxfev=20000, sd = False):
            DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,method="lm",p0 =[1,1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,method="lm",p0 =[1,1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return df


        def relative_deviations(self, method="lm",p0 =[1,1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,method="lm",p0 =[1,1,1], maxfev=20000):
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD  = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 3  # Número de parámetros del modelo
            Q = 1   # Número de variables independientes
            N    = len(DF["RD"])
            AIC  = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2   = 1 - (ss_res / ss_tot)
            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad = [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names  = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self,  method="lm",p0 =[1,1,1], maxfev=20000):
            MRD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self,method="lm",p0 =[1,1,1], maxfev=20000):
            MAPE= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self,method="lm",p0 =[1,1,1], maxfev=20000):
            RMSD= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self,method="lm",p0 =[1,1,1], maxfev=20000):
            AIC= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,method="lm", p0 =[1,1,1],maxfev=20000):
            R2= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,method="lm", p0 =[1,1,1],maxfev=20000):
            R2_a= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, method="lm",p0 =[1,1,1], maxfev=20000, sd = False, name = "Modified Apelblat"):
            
            nombre       = name
            listaval     = self.values( method = method,p0 =p0, maxfev=maxfev)
            calculados   = self.calculated_values( method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations( method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters( method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self,method="lm",p0 =[1,1,1], maxfev=20000, name = "Modified Apelblat",separated = False, cols=2, rows =6,height=1100, width=1300):

            nombre= name

            df_values = self.values(method=method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"

            else:

                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"


            W = self.mass_fractions["w1"]
            Temp = self.temperature_values["T"]
            
            numerofilas = len(Temp)
            numerocolumnas = len(W)
            L = [numerofilas*i for i in range(numerocolumnas+2)]


            if separated == False :

                fig = go.Figure()          
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "w1 =" + str(W[i]) ,
                                            text= Temp.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))


                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))


                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica = fig.show()
            
            if  separated == True and cols*rows >= len(W):
                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                w= W.values.tolist()
                name =["w1"+" = "+str(i)+", "+"RMD% = "+str(RMDP[w.index(i)].round(5)) for i in w]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= Temp.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color='Red')),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(W)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        

        def summary_download(self,method="lm",p0 =[1,1,1], maxfev=20000, sd = False,name = "Modified Apelblat",extension= "xlsx"):

            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= nombre + name_archi +"."+extension
                salida = url
            return DATA

        def plot_download(self,method="lm",p0 =[1,1,1], maxfev=20000, name ="Modified Apelblat",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida


    class vant_hoff(dataset):
        def __init__(self,url):
            self.name = url

        
        @property
        def show(self):
            L = URL.split(".")

            if L[-1]=="csv":
                df = pd.read_csv(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
            
            if L[-1]=="xlsx":
                df = pd.read_excel(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)

            return DFF

        @property
        def temperature_values(self):
            df = self.show
            tem = df["T"]
            return pd.DataFrame({"T":tem})
                    

        @property
        def mass_fractions(self):
            df = self.show
            mf = df.columns[1:]
            return pd.DataFrame({"w1":mf})

        @property
        def equation(self):
            salida = display(HTML('<h2> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Van’t Hoff Model Equation</h2>'))
            display(Math(r'$$\large{\ln(x_3) = \dfrac{a}{T} + b }$$'))
            return salida

    
        def __kernel(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, sd = False, opt = "calculate"):

            def fT(T,a,b):
                return np.exp(a/T + b)  

            def fx(x,a,b):
                return a/(np.log(x)-b)


            df = self.show
            W  = df.columns[1:].tolist()
            Temp = df["T"].values
            

            para_a,para_b = [],[]
            desv_a,desv_b = [],[]
            desv_para_a,desv_para_b = [],[]
            L_para,L_desv,L_desv_para= [ para_a,para_b],[desv_a,desv_b],[desv_para_a,desv_para_b]
            
        
            if funtion== "fx":
                
                for i in  W:
                    xdat = df[i]
                    Tdat = df["T"]
                    popt, mcov= curve_fit(fx,xdat,Tdat,method= "lm",p0=p0,maxfev=20000)

                    for j in L_para:
                        j.append(popt[L_para.index(j)])

                    for k in L_desv:
                        k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))

                    for l in L_desv_para:
                        l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

            
            if funtion == "fT":

                for i in  W:
                    xdat = df[i]
                    Tdat = df["T"]
                    popt, mcov= curve_fit(fT,Tdat,xdat,method= "lm",p0=p0,maxfev=20000)

                    for j in L_para:
                        j.append(popt[L_para.index(j)])

                    for k in L_desv:
                        k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))

                    for l in L_desv_para:
                        l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

            
            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in W:

                wdat = len(Temp)*[i]
                Wdat = wdat

                tdat = Temp
                Tdat = tdat.tolist()

                x3_exp = df[i].values
                X3_exp =  x3_exp.tolist()

                x3_cal = fT(tdat,para_a[W.index(i)],para_b[W.index(i)])
                X3_cal = x3_cal.tolist()

                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w    += Wdat
                C_temp += Tdat
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w    = np.array(C_w)
            arr_temp = np.array(C_temp)
            arr_exp  = np.array(C_exp)
            arr_cal  = np.array(C_cal)
            arr_RD   = np.array(C_RD )

            dataframe = pd.DataFrame({"w1":arr_w,'RD':arr_RD})

            MAPES = []

            for i in range(len(W)):

                df_mask = dataframe['w1'] == W[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["w1"])
                MAPES.append(MRDP)

            df_para = pd.DataFrame({"w1":W,'a':para_a,'b':para_b,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"w1":W,'a ± σ':desv_para_a,'b ± σ':desv_para_b,"MRD%":MAPES})
            df_cal  = pd.DataFrame({"w1":arr_w,'T': arr_temp,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return  df_kernel 

        def parameters(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, sd = False):
            DF = self.__kernel(funtion = funtion, method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return df


        def relative_deviations(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD  = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 2  # Número de parámetros del modelo
            Q = 1   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)

            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self, funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            MRD= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self, funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            MAPE= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            RMSD= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            AIC= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,funtion = "fx",method="lm", p0 =[1,1],maxfev=20000):
            R2= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,funtion = "fx",method="lm", p0 =[1,1],maxfev=20000):
            R2_a= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Van’t Hoff"):
            
            nombre       = name
            listaval     = self.values(funtion = funtion, method = method,p0 =p0, maxfev=maxfev)
            calculados   = self.calculated_values(funtion = funtion, method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations(funtion = funtion, method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters(funtion = funtion, method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(funtion = funtion, method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, name = "Van’t Hoff",separated = False, cols=2, rows =6,height=1100, width=1300):

            nombre= name

            df_values = self.values(funtion =funtion, method= method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"
            else:
                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"


            
            W = self.mass_fractions["w1"]
            Temp = self.temperature_values["T"]


            numerofilas = len(Temp)
            numerocolumnas = len(W)
            L = [numerofilas*i for i in range(numerocolumnas+2)]

            if separated == False :
                fig = go.Figure()
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "w1 = " + str( W[i]) ,
                                            text= Temp.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))


                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))


                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica = fig.show()

            if  separated == True and cols*rows >= len(W):

                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                w= W.values.tolist()
                name =["w1"+" = "+str(i)+", "+"RMD% = "+str(RMDP[w.index(i)].round(5)) for i in w]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= Temp.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color='Red')),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(W)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        


        def summary_download(self,method="lm",p0 =[1,1], maxfev=20000, sd = False, name ="Van’t Hoff",extension= "xlsx"):

            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)
            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= nombre + name_archi +"."+extension
                salida = url
            return DATA

        def plot_download(self,method="lm",p0 =[1,1], maxfev=20000,name = "Van’t Hoff",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)
            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida


    #CLASE PARA EL MODELO DE SOLUBILIDAD VAN’T HOFF-YAWS

    class vant_hoff_yaws(dataset):
        def __init__(self, url):
            self.url = url

        
        @property
        def show(self):
            L = URL.split(".")

            if L[-1]=="csv":
                df = pd.read_csv(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
            
            if L[-1]=="xlsx":
                df = pd.read_excel(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)

            return DFF

        @property
        def temperature_values(self):
            df = self.show
            tem = df["T"]
            return pd.DataFrame({"T":tem})
                    

        @property
        def mass_fractions(self):
            df = self.show
            mf = df.columns[1:]
            return pd.DataFrame({"w1":mf})

        @property
        def equation(self):
            salida = display(HTML('<h2> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Van’t Hoff-Yaws Model Equation</h2>'))
            display(Math(r'$$\large{\ln(x_3) = a + \dfrac{b}{T}+\dfrac{c}{T^2}} $$'))
            return salida

    
        def __kernel(self, method="lm",p0 =[1,1,1], maxfev=20000, sd = False, opt = "calculate"):
            
            def fT(T,a,b,c):
                return np.exp(a+b/T+c/T**2)


            df = self.show
            W  = df.columns[1:].tolist()
            Temp = df["T"].values
            

            para_a,para_b,para_c = [],[],[]
            desv_a,desv_b,desv_c = [],[],[]
            desv_para_a,desv_para_b,desv_para_c = [],[],[]
            L_para,L_desv,L_desv_para= [para_a,para_b,para_c],[desv_a,desv_b,desv_c],[desv_para_a,desv_para_b,desv_para_c]
            
            for i in  W:
                xdat = df[i]
                Tdat = df["T"]
                popt, mcov= curve_fit(fT,Tdat,xdat,method= "lm",p0=p0,maxfev=20000)
                
                for j in L_para:
                    j.append(popt[L_para.index(j)])
                    
                for k in L_desv:
                    k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))
                    
                for l in L_desv_para:
                    l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

        
            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in W:

                wdat = len(Temp)*[i]
                Wdat = wdat

                tdat = Temp
                Tdat = tdat.tolist()

                x3_exp = df[i].values
                X3_exp =  x3_exp.tolist()

                x3_cal = fT(tdat,para_a[W.index(i)],para_b[W.index(i)],para_c[W.index(i)])
                X3_cal = x3_cal.tolist()

                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w    += Wdat
                C_temp += Tdat
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w    = np.array(C_w)
            arr_temp = np.array(C_temp)
            arr_exp  = np.array(C_exp)
            arr_cal  = np.array(C_cal)
            arr_RD   = np.array(C_RD )

            dataframe = pd.DataFrame({"w1":arr_w,'RD':arr_RD})

            MAPES = []

            for i in range(len(W)):

                df_mask = dataframe['w1'] == W[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["w1"])
                MAPES.append(MRDP)

            df_para      = pd.DataFrame({"w1":W,'a':para_a,'b':para_b,'c':para_c,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"w1":W,'a ± σ':desv_para_a,'b ± σ':desv_para_b,'c ± σ':desv_para_c,"MRD%":MAPES})
            df_cal       = pd.DataFrame({"w1":arr_w,'T': arr_temp,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return  df_kernel 

        def parameters(self, method="lm",p0 =[1,1,1], maxfev=20000, sd = False):
            DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,method="lm",p0 =[1,1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,method="lm",p0 =[1,1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return df


        def relative_deviations(self, method="lm",p0 =[1,1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,method="lm",p0 =[1,1,1], maxfev=20000):
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD  = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 3  # Número de parámetros del modelo
            Q = 1   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)

            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self,  method="lm",p0 =[1,1,1], maxfev=20000):
            MRD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self,method="lm",p0 =[1,1,1], maxfev=20000):
            MAPE= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self,method="lm",p0 =[1,1,1], maxfev=20000):
            RMSD= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self,method="lm",p0 =[1,1,1], maxfev=20000):
            AIC= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,method="lm", p0 =[1,1,1],maxfev=20000):
            R2= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,method="lm", p0 =[1,1,1],maxfev=20000):
            R2_a= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, method="lm",p0 =[1,1,1], maxfev=20000, sd = False, name = "Van’t Hoff-Yaws"):
            
            nombre       = name
            listaval     = self.values( method = method,p0 =p0, maxfev=maxfev)
            calculados   = self.calculated_values( method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations( method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters( method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self,method="lm",p0 =[1,1,1], maxfev=20000, name = "Van’t Hoff-Yaws",separated = False, cols=2, rows =6,height=1100, width=1300):

            nombre= name

            df_values = self.values(method=method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"

            else:

                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"


            W = self.mass_fractions["w1"]
            Temp = self.temperature_values["T"]
            
            numerofilas = len(Temp)
            numerocolumnas = len(W)
            L = [numerofilas*i for i in range(numerocolumnas+2)]


            if separated == False :

                fig = go.Figure()          
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "w1 =" + str(W[i]) ,
                                            text= Temp.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))


                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))


                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica = fig.show()
            
            if  separated == True and cols*rows >= len(W):
                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                w= W.values.tolist()
                name =["w1"+" = "+str(i)+", "+"RMD% = "+str(RMDP[w.index(i)].round(5)) for i in w]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= Temp.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color='Red')),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(W)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        

        def summary_download(self,method="lm",p0 =[1,1,1], maxfev=20000, sd = False,name = "Van’t Hoff-Yaws",extension= "xlsx"):

            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= nombre + name_archi +"."+extension
                salida = url
            return DATA

        def plot_download(self,method="lm",p0 =[1,1,1], maxfev=20000, name ="Van’t Hoff-Yaws",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida


    #CLASE PARA EL MODELO DE WILSON MODIFICADO

    class modified_wilson(dataset):
        def __init__(self, url):
            self.url = url
        
        @property
        def show(self):
            L = URL.split(".")

            if L[-1]=="csv":
                df = pd.read_csv(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1)
                else:
                    DFF = df.rename({'w1': ''}, axis=1)
            
            if L[-1]=="xlsx":
                df = pd.read_excel(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1)
                else:
                    DFF = df.rename({'w1': ''}, axis=1)

            return DFF


        @property
        def equation(self):
            salida = display(HTML('<h2>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Modified Wilson Model Equation</h2>'))
            display(Math(r'$$\Large{\ln(x_3)=-1+\frac{w_1(1+\ln x_{3,1})}{w_1+(1-w_1)\lambda_{12}}+\frac{(1-w_1)(1+\ln x_{3,2})}{(1-w_1)+w_1 \lambda_{21}}}$$'))
            return salida

    
        def __kernel(self, method="lm",p0 =[1,1], maxfev=20000, sd = False, opt = "calculate"):

            df = self.show
            dff = df.drop([i for i in range(1,len(df["w1"])-1)],axis=0)
            W = df["w1"]

            Temp    = self.temperature_values["T"].values
            wdat    = df["w1"].values

            
            def fw(w1,λ12,λ21):
                return np.exp(-1+((w1+w1*np.log(x31))/(w1+(1-w1)*λ12))+(((1-w1)+(1-w1)*np.log(x32))/((1-w1)+w1*λ21)))


            para_λ12,para_λ21 = [],[]
            desv_para_λ12,desv_para_λ21 = [],[]

            L_para = [para_λ12,para_λ21]
            L_desv = [desv_para_λ12,desv_para_λ21]


            for i in Temp:
                x31       =  dff[i].values[1]
                x32       =  dff[i].values[0]
                x3_exp    =  df[i].values
                popt,mcov = curve_fit(fw,wdat,x3_exp,p0 =p0,method=method,maxfev=maxfev)

                for j in L_para:
                    j.append(popt[L_para.index(j)])

                for k in L_desv:
                    k.append(str(popt[L_desv.index(k)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv.index(k)]).round(3)))
            


            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]  

            for i in Temp:
        
                Tdat  =  len(df["w1"])*[float(i)]

                wdat  =  df["w1"].values
                Wdat  =   wdat.tolist()

                x31=  dff[i].values[1]
                x32=  dff[i].values[0]

    
                x3_exp =  df[i].values
                X3_exp =  x3_exp.tolist()


                x3_cal = fw(wdat,para_λ12[Temp.tolist().index(i)],para_λ21[Temp.tolist().index(i)])
                X3_cal = x3_cal.tolist()


                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_temp  += Tdat
                C_w    += Wdat
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD

            arr_w = np.array(C_w )
            arr_temp = np.array(C_temp)
            arr_exp = np.array(C_exp)
            arr_cal = np.array( C_cal)
            arr_RD  = np.array( C_RD )

            data_frame = pd.DataFrame({"w1":arr_w ,"T":arr_temp ,'RD':arr_RD})

            MAPES = []


            for i in range(len(Temp)):
                df_mask = data_frame['T'] == float(Temp[i])
                data_filter = data_frame[df_mask]
                MAPE = sum(data_filter["RD"])*100/len(data_filter["RD"])
                MAPES.append(MAPE)

            df_para = pd.DataFrame({"T":Temp,'λ12':para_λ12,'λ21':para_λ21,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"T":Temp,'λ12 ± σ':desv_para_λ12,'λ21 ± σ':desv_para_λ21,"MRD%":MAPES})
            df_cal  = pd.DataFrame({"w1":arr_w,'T': arr_temp,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return  df_kernel 

        def parameters(self,method="lm",p0 =[1,1], maxfev=20000, sd = False):
            DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,method="lm",p0 =[1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return df


        def relative_deviations(self,method="lm",p0 =[1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD  = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 2   # Número de parámetros del modelo
            Q = 1   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)

            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self,method="lm",p0 =[1,1], maxfev=20000):
            MRD= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self, method="lm",p0 =[1,1], maxfev=20000):
            MAPE= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self,method="lm",p0 =[1,1], maxfev=20000):
            RMSD= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self,method="lm",p0 =[1,1], maxfev=20000):
            AIC= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,method="lm", p0 =[1,1],maxfev=20000):
            R2= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,method="lm", p0 =[1,1],maxfev=20000):
            R2_a= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self,method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Buchowski-Ksiazczak"):
            
            nombre       = name
            listaval     = self.values(method = method,p0 =p0, maxfev=maxfev)
            calculados   = self.calculated_values( method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations(method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters( method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics( method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self,method="lm",p0 =[1,1], maxfev=20000, name = "Modified Wilson",separated = False, cols=3, rows =3,height=1000, width=1300):

            nombre= name

            df_values = self.values( method=method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"

            else:
                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"
                
            Temp = self.temperature_values["T"]
            W   = self.mass_fractions["w1"]

            numerofilas    =  len(W)
            numerocolumnas =  len(Temp)
            L = [numerofilas*i for i in range(numerocolumnas+2)]

            
            if separated == False:
                fig = go.Figure()
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(Temp)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "T"+str(i) + "=" +Temp[i] ,
                                            text= W.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>w1: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))

                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))
            
                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica =fig.show()
            
            if separated == True and cols*rows >= len(Temp):

                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                t= Temp.values.tolist()
                name =["T" + str(t.index(i)+1) +"="+str(i)+", "+"RMD% ="+str(RMDP[t.index(i)].round(5)) for i in t]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(Temp)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]],y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= W.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>w1: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),
                                            row=L_row[i], col=L_col[i])

                for i in range(len(Temp)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color="#2a3f5f")),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(Temp)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(Temp)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        

        def summary_download(self,method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Modified Wilson",extension= "xlsx"):

            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)
            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= nombre + name_archi +"."+extension
                salida = url
            return DATA

        def plot_download(self,method="lm",p0 =[1,1], maxfev=20000,name = "Modified Wilson",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)
            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida

    #CLASE PARA EL MODELO DE SOLUBILIDAD BUCHOWSKI KSIAZCZAK

    class buchowski_ksiazaczak(dataset):
        def __init__(self,url,Tf):
            self.name = url
            self.Tf = Tf
        
        @property
        def show(self):
            L = URL.split(".")

            if L[-1]=="csv":
                df = pd.read_csv(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
            
            if L[-1]=="xlsx":
                df = pd.read_excel(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)

            return DFF

        @property
        def temperature_values(self):
            df = self.show
            tem = df["T"]
            return pd.DataFrame({"T":tem})
                    

        @property
        def mass_fractions(self):
            df = self.show
            mf = df.columns[1:]
            return pd.DataFrame({"w1":mf})

        @property
        def equation(self):
            salida = display(HTML('<h2>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Buchowski Ksiazczak Model Equation</h2>'))
            display(Math(r'$$\ln \left[ 1+ \dfrac{\lambda (1 -x_3)}{x_3} \right] = \lambda h \left( \dfrac{1}{T} - \dfrac{1}{T_f}  \right)$$'))
            return salida

    
        def __kernel(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, sd = False, opt = "calculate"):

            Tf = self.Tf

            def fx(x,λ,h):
                return 1/((np.log(1+(λ*(1-x)/x))/(λ*h))+1/Tf)

            def fT1(T,λ,h):
                return (λ*np.exp(λ*h/Tf))/(λ*np.exp(λ*h/Tf)-np.exp(λ*h/Tf)+np.exp(λ*h/T))


            def fT2(T,λ,h):
                return (λ*np.exp(h*λ*(T-Tf)/(Tf*T)))/(((λ-1)*np.exp(h*λ*(T-Tf)/(Tf*T)))+1)


            df = self.show
            W  = df.columns[1:].tolist()
            Temp = df["T"].values
            

            para_λ,para_h = [],[]
            desv_λ,desv_h = [],[]
            desv_para_λ,desv_para_h = [],[]
            L_para,L_desv,L_desv_para= [para_λ,para_h],[desv_λ,desv_h],[desv_para_λ,desv_para_h]
            
        
            if funtion== "fx":
                
                for i in  W:
                    xdat = df[i]
                    Tdat = df["T"]
                    popt, mcov= curve_fit(fx,xdat,Tdat,method= "lm",p0=p0,maxfev=20000)

                    for j in L_para:
                        j.append(popt[L_para.index(j)])

                    for k in L_desv:
                        k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))

                    for l in L_desv_para:
                        l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

            
            if funtion == "fT1":

                for i in  W:
                    xdat = df[i]
                    Tdat = df["T"]
                    popt, mcov= curve_fit(fT1,Tdat,xdat,method= "lm",p0=p0,maxfev=20000)

                    for j in L_para:
                        j.append(popt[L_para.index(j)])

                    for k in L_desv:
                        k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))

                    for l in L_desv_para:
                        l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

            if funtion == "fT2":

                for i in  W:
                    xdat = df[i]
                    Tdat = df["T"]
                    popt, mcov= curve_fit(fT2,Tdat,xdat,method= "lm",p0=p0,maxfev=20000)

                    for j in L_para:
                        j.append(popt[L_para.index(j)])

                    for k in L_desv:
                        k.append(np.sqrt((np.diag(mcov))[L_desv.index(k)]))

                    for l in L_desv_para:
                        l.append(str(popt[L_desv_para.index(l)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(l)]).round(3)))

            
            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in W:

                wdat = len(Temp)*[i]
                Wdat = wdat

                tdat = Temp
                Tdat = tdat.tolist()

                x3_exp = df[i].values
                X3_exp =  x3_exp.tolist()

                x3_cal = fT2(tdat,para_λ[W.index(i)],para_h[W.index(i)])
                X3_cal = x3_cal.tolist()

                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w    += Wdat
                C_temp += Tdat
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w   = np.array(C_w)
            arr_temp = np.array(C_temp)
            arr_exp = np.array(C_exp)
            arr_cal = np.array(C_cal)
            arr_RD  = np.array(C_RD )

            dataframe = pd.DataFrame({"w1":arr_w,'RD':arr_RD})

            MAPES = []

            for i in range(len(W)):

                df_mask = dataframe['w1'] == W[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["w1"])
                MAPES.append(MRDP)

            df_para = pd.DataFrame({"w1":W,'λ':para_λ,'h':para_h,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"w1":W,'λ ± σ':desv_para_λ,'h ± σ':desv_para_h,"MRD%":MAPES})
            df_cal  = pd.DataFrame({"w1":arr_w,'T': arr_temp,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return  df_kernel 

        def parameters(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, sd = False):
            DF = self.__kernel(funtion = funtion, method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return df


        def relative_deviations(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(funtion = funtion, method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 2  # Número de parámetros del modelo
            Q = 1   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)

            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self, funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            MRD= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self, funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            MAPE= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            RMSD= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000):
            AIC= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,funtion = "fx",method="lm", p0 =[1,1],maxfev=20000):
            R2= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,funtion = "fx",method="lm", p0 =[1,1],maxfev=20000):
            R2_a= self.statistics(funtion = funtion, method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Buchowski-Ksiazczak"):
            
            nombre       = name
            listaval     = self.values(funtion = funtion, method = method,p0 =p0, maxfev=maxfev)
            calculados   = self.calculated_values(funtion = funtion, method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations(funtion = funtion, method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters(funtion = funtion, method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(funtion = funtion, method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self,funtion = "fx", method="lm",p0 =[1,1], maxfev=20000, name = "Buchowski-Ksiazczak",separated = False, cols=2, rows =6,height=1100, width=1300):

            nombre= name

            df_values = self.values(funtion =funtion, method= method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"
            else:
                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"


            
            W = self.mass_fractions["w1"]
            Temp = self.temperature_values["T"]


            numerofilas = len(Temp)
            numerocolumnas = len(W)
            L = [numerofilas*i for i in range(numerocolumnas+2)]

            if separated == False :
                fig = go.Figure()
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "w1 = " + str( W[i]) ,
                                            text= Temp.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))


                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))


                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica = fig.show()

            if  separated == True and cols*rows >= len(W):

                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                w= W.values.tolist()
                name =["w1"+" = "+str(i)+", "+"RMD% = "+str(RMDP[w.index(i)].round(5)) for i in w]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= Temp.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color='Red')),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(W)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        


        def summary_download(self,method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Buchowski-Ksiazczak",extension= "xlsx"):

            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)
            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= nombre + name_archi +"."+extension
                salida = url
            return DATA

        def plot_download(self,method="lm",p0 =[1,1], maxfev=20000,name = "Buchowski-Ksiazczak",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)
            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida

    #CLASE PARA EL MODELO DE SOLUBILIDAD NRTL

    class NRTL(dataset):
        def __init__(self,url,Tf,ΔHf):
            self.url = url
            self.Tf  = Tf
            self.ΔHf = ΔHf

                    
        @property
        def equation(self):
            salida = display(HTML('<h2> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; NRTL Model Equation</h2>'))
            display(Math(r'$$\Large{\ln{\gamma_3}=\frac{x_2\tau_{23}G_{23}+x_1\tau_{13}G_{13}}{x_3+x_2G_{23}+x_1G_{13}}-\frac{x_3(x_2\tau_{23}G_{23}+x_1\tau_{13}G_{13})}{(x_3+x_2G_{23}+x_1G_{13})^2}+\frac{x_2G_{32}}{x_3G_{32}+x_2+x_1G_{12}}\left(\tau_{32}-\frac{x_3\tau_{32}G_{32}+x_1\tau_{12}G_{12}}{x_3G_{32}+x_2+x_1G_{12}}\right)+\frac{x_1G_{31}}{x_3G_{31}+x_2G_{21}+x_1}\left(\tau_{31}-\frac{x_3\tau_{31}G_{31}+x_2\tau_{21}G_{21}}{x_3G_{31}+x_2G_{21}+x_1}\right)}$$'))
            return salida


        @property
        def ideal_solubilities(self):
            df  = self.show
            Tf  = self.Tf        #Temperatura de fusión
            ΔHf = self.ΔHf       #Entalpia de fusión 
            ΔSf = ΔHf/Tf         #Entropía de fusión
            R   = 0.00831433     #Constante de los gases ideales 

            Temp = df.drop(['x1',"x2"], axis=1).columns[1:]
            col_x3id = []

            for i in Temp.astype(float):
                x3=np.exp(-((ΔHf*(Tf-i))/(R*Tf*i))+((ΔSf*(Tf-i))/(R*i))-((ΔSf/R)*np.log(Tf/i)))  #solubilidad ideal
                col_x3id .append(x3)
        
            df_solid = pd.DataFrame({"T":Temp,'x3_id':col_x3id})
            return df_solid
        
        @property
        def activity_coefficients(self):
            
            df  = self.show
            Temp = self.temperature_values["T"].values
            col_x3id = self.ideal_solubilities["x3_id"].values

            cols_γ3  = []  
            namecols = []

            for i in range(len(Temp)):
                col_γ3 = col_x3id[i]/df[Temp[i]]
                cols_γ3.append(col_γ3)
                namecols.append(str(Temp[i]))

            df_ca = pd.DataFrame(dict(zip(namecols ,cols_γ3)))
            data_ca = pd.concat([df['w1'],df_ca], axis=1)
            return data_ca

    
        def __kernel(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False, opt = "calculate"):
            
            def fx(X,τ12,τ13,τ21,τ23,τ31,τ32):
                α = -0.3
                x1, x2, x3= X
        
                A = (x2*τ23*np.exp(α*τ23)+x1*τ13*np.exp(α*τ13))/(x3+x2*np.exp(α*τ23)+x1*np.exp(α*τ13))         
                B = x3*(x2*τ23*np.exp(α*τ23)+x1*τ13*np.exp(α*τ13))/(x3+x2*np.exp(α*τ23)+x1*np.exp(α*τ13))**2
                C = ((x2*np.exp(α*τ32))/(x3*np.exp(α*τ32)+x2+x1*np.exp(α*τ12)))*(τ32-((x3*τ32*np.exp(α*τ32)+x1*τ12*np.exp(α*τ12))/(x3*np.exp(α*τ32)+x2+x1*np.exp(α*τ12))))
                D = ((x1*np.exp(α*τ31))/(x3*np.exp(α*τ31)+x2*np.exp(α*τ21)+x1))*(τ31-((x3*τ31*np.exp(α*τ31)+x2*τ21*np.exp(α*τ21))/(x3*np.exp(α*τ31)+x2*np.exp(α*τ21)+x1)))

                return (A-B+C+D)

                
            df = self.show

            x1dat = df["x1"]
            x2dat = df["x2"]

            
            col_x3id =  self.ideal_solubilities["x3_id"].values
            cols_γ3  =  self.activity_coefficients

            Temp = self.temperature_values["T"].values
            

            para_τ12,para_τ13,para_τ21, para_τ23,para_τ31,para_τ32  = [],[],[],[],[],[]
            desv_para_τ12,desv_para_τ13, desv_para_τ21,desv_para_τ23,desv_para_τ31,desv_para_τ32  = [],[],[],[],[],[]
            L_para,L_desv_para= [ para_τ12,para_τ13,para_τ21, para_τ23,para_τ31,para_τ32 ],[desv_para_τ12,desv_para_τ13, desv_para_τ21,desv_para_τ23,desv_para_τ31,desv_para_τ32 ]

            for i in range(len(Temp)):
                x3dat = df[Temp[i]].values  
                ydat = np.log(cols_γ3[Temp[i]]).values

                popt,mcov = curve_fit(fx,(x1dat,x2dat,x3dat),ydat,p0=p0,method="lm",maxfev=600000)


                for j in L_para:
                    j.append(popt[L_para.index(j)])

                for k in L_desv_para:
                    k.append(str(popt[L_desv_para.index(k)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(k)]).round(3)))

            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in range(len(Temp)):

            
                x3_exp = df[Temp[i]].values
                X3_exp =  x3_exp.tolist()

                X = np.array([x1dat,x2dat,x3_exp])

                γ3_cal = fx(X,para_τ12[i],para_τ13[i],para_τ21[i],para_τ23[i],para_τ31[i],para_τ32[i])
                
                x3_cal = col_x3id[i]/np.exp(γ3_cal)
                X3_cal = x3_cal.tolist()
                
                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w += df["w1"].tolist()
                C_temp += len(df["w1"])*[Temp[i]]
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w   = np.array(C_w)
            arr_tem = np.array(C_temp)
            arr_exp = np.array(C_exp)
            arr_cal = np.array( C_cal)
            arr_RD  = np.array( C_RD )

            dataframe = pd.DataFrame({"T":arr_tem,'RD':arr_RD})

            MAPES = []

            for i in range(len(Temp)):
                df_mask = dataframe['T'] == Temp[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["T"])
                MAPES.append(MRDP)

            df_para      = pd.DataFrame({"T":Temp,'τ12':para_τ12,'τ13':para_τ13,'τ21':para_τ21,'τ23':para_τ23,'τ31':para_τ31,'τ32':para_τ32,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"T":Temp,'τ12 ± σ':desv_para_τ12,'τ13 ± σ':desv_para_τ13,'τ21 ± σ':desv_para_τ21,'τ23 ± σ':desv_para_τ23,'τ31 ± σ':desv_para_τ31,'τ32 ± σ':desv_para_τ32,"MRD%":MAPES})
            df_cal       = pd.DataFrame({"w1":arr_w,'T': arr_tem,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return df_kernel

        def parameters(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False):
            DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            ideal = self.ideal_solubilities.rename({'T':'',"x3_id":"ideal"}, axis=1).set_index('').transpose()

            df = pd.concat(L+[ideal],axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return  df


        def relative_deviations(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 6  # Número de parámetros del modelo
            Q = 3   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)
            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            MRD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            MAPE= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            RMSD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            AIC= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,method="lm", p0 =[1,1,1,1,1,1],maxfev=20000):
            R2= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,method="lm", p0 =[1,1,1,1,1,1],maxfev=20000):
            R2_a= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False, name = "NRTL"):
            
            nombre       = name
            listaval     = self.values( method = method,p0 =p0, maxfev=maxfev)
            coeficientes = self.activity_coefficients
            calculados   = self.calculated_values( method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations(method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters( method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,coeficientes,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, name = "NRTL",separated = False, cols=3, rows =3,height=1000, width=1300):
            
            nombre= name

            df_values = self.values( method=method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"

            else:
                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"
                
            Temp = self.temperature_values["T"]
            W   = self.mass_fractions["w1"]

            numerofilas    =  len(W)
            numerocolumnas =  len(Temp)
            L = [numerofilas*i for i in range(numerocolumnas+2)]

            
            if separated == False:
                fig = go.Figure()
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(Temp)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "T"+str(i) + "=" +Temp[i] ,
                                            text= W.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>w1: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))

                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))
            
                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica =fig.show()
            
            if separated == True and cols*rows >= len(Temp):

                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                t= Temp.values.tolist()
                name =["T" + str(t.index(i)+1) +"="+str(i)+", "+"RMD% ="+str(RMDP[t.index(i)].round(5)) for i in t]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(Temp)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]],y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= W.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>w1: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),
                                            row=L_row[i], col=L_col[i])

                for i in range(len(Temp)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color="#2a3f5f")),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(Temp)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(Temp)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        

    def summary_download(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False, name = "NRTL",extension= "xlsx"):
        
        DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)

        nombre = name
        name_archi = "-" + URL.split("/")[-1].split(".")[-2]
        
        if entorno == "/usr/bin/python3":
            url= "/content/"+ nombre + name_archi +"."+extension
            files.download(url)
        else:
            url= nombre + name_archi +"."+extension
        return DATA

    def plot_download(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, name = "NRTL",extension= "pdf"):

        self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)

        nombre = name
        name_archi = "-" + URL.split("/")[-1].split(".")[-2]
        if entorno == "/usr/bin/python3":
            url= "/content/"+nombre + name_archi +"."+extension
            salida = files.download(url)
        else:
            url= "/content/"+nombre + name_archi +"."+extension
            salida = url    
        return salida

    #CLASE PARA EL MODELO DE SOLUBILIDAD DE WILSON

    class wilson(dataset):
        def __init__(self,url,Tf,ΔHf):
            self.url = url
            self.Tf  = Tf
            self.ΔHf = ΔHf

                    
        @property
        def equation(self):
            salida = display(HTML('<h2> &nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Wilson Model Equation</h2>'))
            display(Math(r'$$\Large{\ln{\gamma_3}=1-\ln{(x_3+x_2Λ_{32}+x_1Λ_{31})}-\left(\frac{x_3}{x_3+x_2Λ_{32}+x_1Λ_{31}}+\frac{x_2Λ_{23}}{x_3Λ_{23}+x_2+x_1Λ_{21}}+\frac{x_1Λ_{13}}{x_3Λ_{13}+x_2Λ_{12}+x_1}\right)}$$'))
            return salida


        @property
        def ideal_solubilities(self):
            df  = self.show
            Tf  = self.Tf        #Temperatura de fusión
            ΔHf = self.ΔHf       #Entalpia de fusión 
            ΔSf = ΔHf/Tf         #Entropía de fusión
            R   = 0.00831433     #Constante de los gases ideales 

            Temp = df.drop(['x1',"x2"], axis=1).columns[1:]
            col_x3id = []

            for i in Temp.astype(float):
                x3=np.exp(-((ΔHf*(Tf-i))/(R*Tf*i))+((ΔSf*(Tf-i))/(R*i))-((ΔSf/R)*np.log(Tf/i)))  #solubilidad ideal
                col_x3id .append(x3)
        
            df_solid = pd.DataFrame({"T":Temp,'x3_id':col_x3id})
            return df_solid
        
        @property
        def activity_coefficients(self):
            
            df  = self.show
            Temp = self.temperature_values["T"].values
            col_x3id = self.ideal_solubilities["x3_id"].values

            cols_γ3  = []  
            namecols = []

            for i in range(len(Temp)):
                col_γ3 = col_x3id[i]/df[Temp[i]]
                cols_γ3.append(col_γ3)
                namecols.append(str(Temp[i]))

            df_ca = pd.DataFrame(dict(zip(namecols ,cols_γ3)))
            data_ca = pd.concat([df['w1'],df_ca], axis=1)
            return data_ca

    
        def __kernel(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False, opt = "calculate"):
            
            def fx(X,Λ32,Λ31,Λ23,Λ21,Λ13,Λ12):
                x1, x2, x3 = X

                A=1-np.log(x3+x2*Λ32+x1*Λ31)
                B=((x3/(x3+x2*Λ32+x1*Λ31))+((x2*Λ23)/(x3*Λ23+x2+x1*Λ21))+((x1*Λ13)/(x3*Λ13+x2*Λ12+x1)))

                return A-B
                
            df = self.show

            x1dat = df["x1"]
            x2dat = df["x2"]

            
            col_x3id =  self.ideal_solubilities["x3_id"].values
            cols_γ3  =  self.activity_coefficients

            Temp = self.temperature_values["T"].values
            

            para_Λ32,para_Λ31,para_Λ23, para_Λ21,para_Λ13,para_Λ12  = [],[],[],[],[],[]
            desv_para_Λ32,desv_para_Λ31, desv_para_Λ23,desv_para_Λ21,desv_para_Λ13,desv_para_Λ12  = [],[],[],[],[],[]
            L_para,L_desv_para= [ para_Λ32,para_Λ31,para_Λ23, para_Λ21,para_Λ13,para_Λ12 ],[desv_para_Λ32,desv_para_Λ31, desv_para_Λ23,desv_para_Λ21,desv_para_Λ13,desv_para_Λ12]

            for i in range(len(Temp)):
                x3dat = df[Temp[i]].values  
                ydat = np.log(cols_γ3[Temp[i]]).values

                popt,mcov = curve_fit(fx,(x1dat,x2dat,x3dat),ydat,p0=p0,method="lm",maxfev=600000)

                for j in L_para:
                    j.append(popt[L_para.index(j)])

                for k in L_desv_para:
                    k.append(str(popt[L_desv_para.index(k)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(k)]).round(3)))

            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in range(len(Temp)):


                x3_exp =  df[Temp[i]].values
                X3_exp =  x3_exp.tolist()

                X = np.array([x1dat,x2dat,x3_exp])

                #para_Λ32,para_Λ31,para_Λ23, para_Λ21,para_Λ13,para_Λ12 

                γ3_cal = fx(X,para_Λ32[i],para_Λ31[i],para_Λ23[i],para_Λ21[i],para_Λ13[i],para_Λ12[i])
                
                x3_cal = col_x3id[i]/np.exp(γ3_cal)
                X3_cal = x3_cal.tolist()

                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w += df["w1"].tolist()
                C_temp += len(df["w1"])*[Temp[i]]
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w   = np.array(C_w)
            arr_tem = np.array(C_temp)
            arr_exp = np.array(C_exp)
            arr_cal = np.array( C_cal)
            arr_RD  = np.array( C_RD )

            dataframe = pd.DataFrame({"T":arr_tem,'RD':arr_RD})

            MAPES = []

            for i in range(len(Temp)):
                df_mask = dataframe['T'] == Temp[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["T"])
                MAPES.append(MRDP)

            #para_Λ32,para_Λ31,para_Λ23, para_Λ21,para_Λ13,para_Λ12 

            df_para      = pd.DataFrame({"T":Temp,'Λ32':para_Λ32,'Λ31':para_Λ31,'Λ23':para_Λ23,'Λ21':para_Λ21,'Λ13':para_Λ13,'Λ12':para_Λ12,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"T":Temp,'Λ32 ± σ':desv_para_Λ32,'Λ31 ± σ':desv_para_Λ31,'Λ23 ± σ':desv_para_Λ23,'Λ21 ± σ':desv_para_Λ21,'Λ13 ± σ':desv_para_Λ13,'Λ12 ± σ':desv_para_Λ12,"MRD%":MAPES})
            df_cal       = pd.DataFrame({"w1":arr_w,'T': arr_tem,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return df_kernel

        def parameters(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False):
            DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            ideal = self.ideal_solubilities.rename({'T':'',"x3_id":"ideal"}, axis=1).set_index('').transpose()

            df = pd.concat(L+[ideal],axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return  df


        def relative_deviations(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 6  # Número de parámetros del modelo
            Q = 3   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)

            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            MRD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            MAPE= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            RMSD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000):
            AIC= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,method="lm", p0 =[1,1,1,1,1,1],maxfev=20000):
            R2= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,method="lm", p0 =[1,1,1,1,1,1],maxfev=20000):
            R2_a= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False, name = "Wilson"):
            
            nombre       = name
            listaval     = self.values( method = method,p0 =p0, maxfev=maxfev)
            coeficientes = self.activity_coefficients
            calculados   = self.calculated_values( method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations(method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters( method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval ,coeficientes,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self, method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, name = "Wilson",separated = False, cols=3, rows =3,height=1000, width=1300):
            
            nombre= name

            df_values = self.values( method=method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"

            else:
                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"
                
            Temp = self.temperature_values["T"]
            W    = self.mass_fractions["w1"]

            numerofilas    =  len(W)
            numerocolumnas =  len(Temp)
            L = [numerofilas*i for i in range(numerocolumnas+2)]

            
            if separated == False:
                fig = go.Figure()
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(Temp)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "T"+str(i) + "=" +Temp[i] ,
                                            text= W.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>w1: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))

                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))
            
                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica =fig.show()
            
            if separated == True and cols*rows >= len(Temp):

                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                t= Temp.values.tolist()
                name =["T" + str(t.index(i)+1) +"="+str(i)+", "+"RMD% ="+str(RMDP[t.index(i)].round(5)) for i in t]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(Temp)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]],y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= W.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>w1: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),
                                            row=L_row[i], col=L_col[i])

                for i in range(len(Temp)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color="#2a3f5f")),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(Temp)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(Temp)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica


        def summary_download(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, sd = False, name = "Wilson",extension= "xlsx"):
            
            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                files.download(url)
            else:
                url= nombre + name_archi +"."+extension
            return DATA

        def plot_download(self,method="lm",p0 =[1,1,1,1,1,1], maxfev=20000, name = "Wilson",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida

    #CLASE PARA EL MODELO DE SOLUBILIDAD WEILBULL DE DOS PARÁMETROS           

    class weibull(dataset):
        def __init__(self,url,Tf,ΔHf):
            self.url = url
            self.Tf  = Tf
            self.ΔHf = ΔHf

        @property
        def show(self):
            L = URL.split(".")

            if L[-1]=="csv":
                df = pd.read_csv(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
            
            if L[-1]=="xlsx":
                df = pd.read_excel(URL)
                if "x1" in df.columns or "x2" in df.columns:
                    DFF = df.drop(['x1',"x2"], axis=1).rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)
                else:
                    DFF = df.rename({'w1': ''}, axis=1).set_index('').transpose().reset_index().rename({'index': 'T'}, axis=1).astype(float)

            return DFF

        @property
        def temperature_values(self):
            df = self.show
            tem = df["T"]
            return pd.DataFrame({"T":tem})
                    

        @property
        def mass_fractions(self):
            df = self.show
            mf = df.columns[1:]
            return pd.DataFrame({"w1":mf})

                    
        @property
        def equation(self):
            salida = display(HTML('<h2> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Two-Parameter Weibull Model Equation</h2>'))
            display(Math(r'$$\Large{\ln(x_3) = \ln{x}_{3}^{id}-\dfrac{A}{T}\left( 1-e^{-\left( \dfrac{B}{T}-\dfrac{B}{T_f}\right)^2}\right)}$$'))
            return salida


        @property
        def ideal_solubilities(self):
            df  = self.show
            Tf  = self.Tf        #Temperatura de fusión
            ΔHf = self.ΔHf       #Entalpia de fusión 
            ΔSf = ΔHf/Tf         #Entropía de fusión
            R   = 0.00831433     #Constante de los gases ideales 

            Temp = self.temperature_values["T"]
            col_x3id = []

            for i in Temp.astype(float):
                x3=np.exp(-((ΔHf*(Tf-i))/(R*Tf*i))+((ΔSf*(Tf-i))/(R*i))-((ΔSf/R)*np.log(Tf/i)))  #solubilidad ideal
                col_x3id .append(x3)
        
            df_solid = pd.DataFrame({"T":Temp,'x3_id':col_x3id})
            return df_solid
        

    
        def __kernel(self,method="lm",p0 =[1,1], maxfev=20000, sd = False, opt = "calculate"):
            
            Tf  = self.Tf        #Temperatura de fusión
            ΔHf = self.ΔHf       #Entalpia de fusión 
            ΔSf = ΔHf/Tf         #Entropía de fusión
            R   = 0.00831433     #Constante de los gases ideales 

            
            def fT(T, A, B):
                lx3_id = -((ΔHf*(Tf-T))/(R*Tf*T))+((ΔSf*(Tf-T))/(R*T))-((ΔSf/R)*np.log(Tf/T))
                return np.exp(lx3_id-(A/T)*(1-np.exp(-((B/T)-(B/Tf))**2)))
                
            df = self.show
            Temp = self.temperature_values["T"].values
            W  = df.columns[1:].tolist()
            

            para_A,para_B = [],[]
            desv_para_A,desv_para_B = [],[]
            L_para,L_desv_para= [para_A,para_B],[desv_para_A,desv_para_B]

            for i in W:
                Tdat = Temp = df["T"].values
                x3_exp = df[i].values  
                popt,mcov = curve_fit(fT,Tdat,x3_exp,p0=p0,method="lm",maxfev=600000)

                for j in L_para:
                    j.append(popt[L_para.index(j)])

                for k in L_desv_para:
                    k.append(str(popt[L_desv_para.index(k)].round(3)) + " ± " + str(np.sqrt((np.diag(mcov))[L_desv_para.index(k)]).round(3)))

            C_w, C_temp, C_exp, C_cal, C_RD  = [],[],[],[],[]
        

            for i in W:

                wdat = len(Temp)*[i]
                Wdat = wdat

                tdat = Temp
                Tdat = tdat.tolist()

                x3_exp = df[i].values
                X3_exp =  x3_exp.tolist()
            
                x3_cal = fT(tdat,para_A[W.index(i)],para_B[W.index(i)])
                X3_cal = x3_cal.tolist()
                
                RD = ((x3_cal - x3_exp)/x3_exp).tolist()

                C_w    += Wdat
                C_temp += Tdat
                C_exp  += X3_exp
                C_cal  += X3_cal
                C_RD   += RD
    
            arr_w    = np.array(C_w)
            arr_temp = np.array(C_temp)
            arr_exp  = np.array(C_exp)
            arr_cal  = np.array(C_cal)
            arr_RD   = np.array(C_RD )


            dataframe = pd.DataFrame({"w1":arr_w,'RD':arr_RD})

            MAPES = []

            for i in range(len(W)):

                df_mask = dataframe['w1'] == W[i]
                data_filter = dataframe[df_mask]
                MRDP = sum(data_filter["RD"])*100/len(data_filter["w1"])
                MAPES.append(MRDP)

            df_para = pd.DataFrame({"w1":W,'A':para_A,'B':para_B,"MRD%":MAPES})
            df_para_desv = pd.DataFrame({"w1":W,'A ± σ':desv_para_A,'B ± σ':desv_para_B,"MRD%":MAPES})
            df_cal  = pd.DataFrame({"w1":arr_w,'T': arr_temp,"x3_Exp":arr_exp,"x3_Cal":arr_cal, "RD":arr_RD })

            if opt == "calculate" and sd == False:
                df_kernel = df_cal
            if opt == "parameters" and sd == True:
                df_kernel = df_para_desv
            if opt == "parameters" and sd == False:
                df_kernel = df_para
            return  df_kernel 

        def parameters(self, method="lm",p0 =[1,1], maxfev=20000, sd = False):
            DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, sd = sd, opt = "parameters")
            return DF
        

        def values(self,method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt = "calculate")
            return DF

        def calculated_values(self,method="lm",p0 =[1,1], maxfev=20000):
            W = self.mass_fractions["w1"]
            DF = self.__kernel( method=method,p0=p0,maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","RD"],axis=1).rename({'T':'','x3_Cal':i}, axis=1).set_index('').transpose()
                L.append(line)

            ideal = self.ideal_solubilities.rename({'T':'',"x3_id":"ideal"}, axis=1).set_index('').transpose()

            df = pd.concat(L+[ideal],axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
            return  df


        def relative_deviations(self,method="lm",p0 =[1,1], maxfev=20000):
            
            W = self.mass_fractions["w1"]
            DF = self.__kernel(method=method,p0=p0,maxfev=maxfev, opt="calculate")
            L = []
            for i in W: 
                mask = DF['w1'] == i
                data_filter = DF[mask]
                line = data_filter.drop(["w1","x3_Exp","x3_Cal"],axis=1).rename({'T':'','RD':i}, axis=1).set_index('').transpose()
                L.append(line)

            df = pd.concat(L,axis =0).reset_index().rename({'index': 'w1'}, axis=1).rename({'T': ''},axis=1)
        
            return df


        def statistics(self,method="lm",p0 =[1,1], maxfev=20000):
            DF = self.__kernel(method=method,p0=p0 , maxfev=maxfev, opt="calculate")

            MAPE = sum(abs(DF["RD"]))*100/len(DF["RD"])
            MRD = sum(DF["RD"])/len(DF["RD"])
            MRDP = sum(DF["RD"])*100/len(DF["RD"])

            ss_res = np.sum((DF["x3_Cal"] - DF["x3_Exp"])**2)
            ss_tot = np.sum((DF["x3_Exp"] - np.mean(DF["x3_Exp"]))**2)

            RMSD = np.sqrt(ss_res/len(DF["x3_Exp"]))

            k = 2  # Número de parámetros del modelo
            Q = 1   # Número de variables independientes
            N =len(DF["RD"])
            AIC = N*np.log(ss_res/N)+2*k
            AICc = abs(AIC +((2*k**2+2*k)/(N-k-1)))

            R2 = 1 - (ss_res / ss_tot)
            R2_a = 1-((N-1)/(N-Q-1))*(1- R2**2)

            L_stad= [MRDP,MAPE,RMSD,AICc,R2,R2_a]
            names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

            df_estadis = pd.DataFrame({"statistic":names,"values":L_stad})

            return df_estadis

        def statistic_MRD(self,method="lm",p0 =[1,1], maxfev=20000):
            MRD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][0]
            return print("Mean relative deviations, MRD = ",MRD)


        def statistic_MAPE(self,method="lm",p0 =[1,1], maxfev=20000):
            MAPE= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][1]
            return print("Mean Absolute Percentage Error, MAPE = ",MAPE)

        def statistic_RMSD(self, method="lm",p0 =[1,1], maxfev=20000):
            RMSD= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][2]
            return print("Root Mean Square Deviation, RMSD = ",RMSD)
            
        def statistic_AIC(self, method="lm",p0 =[1,1], maxfev=20000):
            AIC= self.statistics( method=method,p0 =p0, maxfev=maxfev)["values"][3]
            return print("Akaike Information Criterion corrected , AICc = ",AIC)

        def statistic_R2(self,method="lm", p0 =[1,1],maxfev=20000):
            R2= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][4]
            return print("Coefficient of Determination, R2 =",R2)
        
        def statistic_R2a(self,method="lm", p0 =[1,1],maxfev=20000):
            R2_a= self.statistics(method=method,p0 =p0, maxfev=maxfev)["values"][5]
            return print("Adjusted Coefficient of Determination, R2 =",R2_a)


        def summary(self, method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Weibull Two-Parameter"):
            
            nombre       = name
            listaval     = self.values( method = method,p0 =p0, maxfev=maxfev)
            calculados   = self.calculated_values( method = method,p0 =p0, maxfev=maxfev)
            diferencias  = self.relative_deviations(method = method,p0 =p0, maxfev=maxfev) 
            parametros   = self.parameters( method = method,p0 =p0, maxfev=maxfev,sd = sd)
            estadisticos = self.statistics(method = method,p0 =p0, maxfev=maxfev)

            DATA = pd.concat([listaval,calculados,diferencias,parametros,estadisticos], axis=1)
            
            name_archi = URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_1 = "/content/"+ nombre + "-"+ name_archi +".xlsx"
                url_3 = "/content/"+ nombre + "-"+ name_archi +".csv"
            else:
                url_1 = nombre + "-"+ name_archi +".xlsx"
                url_3 = nombre + "-"+ name_archi +".csv"

            DATA.to_excel(url_1,sheet_name=name_archi)
            DATA.to_csv(url_3)
            return DATA

        def plot(self, method="lm",p0 =[1,1], maxfev=20000, name = "Weibull Two-Parameter",separated = False, cols=3, rows =3,height=1000, width=1300):
            
            nombre= name

            df_values = self.values(method= method,p0 =p0, maxfev=maxfev)

            name_archi ="-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url_2 = "/content/"+ nombre +  name_archi +".pdf"
                url_4 = "/content/"+ nombre +  name_archi +".png"
                url_5 = "/content/"+ nombre +  name_archi +"2"+".png"
            else:
                url_2 = nombre +  name_archi +".pdf"
                url_4 = nombre +  name_archi +".png"
                url_5 = nombre +  name_archi +"2"+".png"


            
            W = self.mass_fractions["w1"]
            Temp = self.temperature_values["T"]


            numerofilas = len(Temp)
            numerocolumnas = len(W)
            L = [numerofilas*i for i in range(numerocolumnas+2)]

            if separated == False :
                fig = go.Figure()
                X = np.linspace(min(df_values["x3_Cal"]),max(df_values["x3_Cal"]),200)

                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            name= "w1 = " + str( W[i]) ,
                                            text= Temp.tolist(),
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))))


                fig.add_trace(go.Scatter(x=X,y=X,name="$x3^{Exp}=x3^{Cal}$",hoverinfo = "skip"))


                fig.update_xaxes(title = "$x3^{Cal}$", title_font=dict(size=20, family='latex', color='rgb(1,21,51)'))
                fig.update_yaxes(title = "$x3^{Exp}$ ",title_font=dict(size=20,family='latex', color='rgb(1,21,51)'))
                fig.update_layout(title='',title_font=dict(size=26, family='latex', color= "rgb(1,21,51)"),width=1010, height=550)
                fig.update_layout(legend=dict(orientation="h",y=1.2,x=0.03),title_font=dict(size=40, color='rgb(1,21,51)'))
                fig.write_image(url_2)
                fig.write_image(url_4)
                grafica = fig.show()

            if  separated == True and cols*rows >= len(W):

                L_r = []
                for i in range(1,rows+1):
                    L_r += cols*[i]

                L_row =10*L_r
                L_col =10*list(range(1,cols+1))

                DF = self.__kernel(method=method,p0 =p0,maxfev=maxfev, opt = "parameters")

                RMDP = DF["MRD%"].values

                w= W.values.tolist()
                name =["w1"+" = "+str(i)+", "+"RMD% = "+str(RMDP[w.index(i)].round(5)) for i in w]

                fig = make_subplots(rows=rows, cols=cols,subplot_titles=name)

        
                for i in range(len(W)):
                    fig.add_trace(go.Scatter(x=df_values["x3_Cal"][L[i]:L[i+1]], y=df_values["x3_Exp"][L[i]:L[i+1]],
                                            text= Temp.tolist(),
                                            name = "",
                                            hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>T: %{text}<br>",
                                            mode='markers',
                                            showlegend= False,
                                            marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    X = np.linspace(min(df_values["x3_Cal"][L[i]:L[i+1]]),max(df_values["x3_Cal"][L[i]:L[i+1]]),200)
                    fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color='Red')),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

                for i in range(len(W)):
                    fig.update_xaxes(title = "$x3^{Cal}$")

                for i in range(len(W)):
                    fig.update_yaxes(title = "$x3^{Exp}$")

                fig.write_image(url_5)

                fig.update_layout(height=height, width=width,showlegend=False)
                grafica = fig.show()

            return grafica
        

        def summary_download(self,method="lm",p0 =[1,1], maxfev=20000, sd = False, name = "Weibull Two-Parameter",extension= "xlsx"):
            
            DATA = self.summary(method=method,p0 =p0, maxfev=maxfev,sd = sd, name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            
            if entorno == "/usr/bin/python3":
                url= "/content/"+ nombre + name_archi +"."+extension
                files.download(url)
            else:
                url= nombre + name_archi +"."+extension
            return DATA

        def plot_download(self,method="lm",p0 =[1,1], maxfev=20000, name = "Weibull Two-Parameter",extension= "pdf"):

            self.plot(method=method,p0 =p0, maxfev=maxfev,name = name)

            nombre = name
            name_archi = "-" + URL.split("/")[-1].split(".")[-2]
            if entorno == "/usr/bin/python3":
                url= "/content/"+nombre + name_archi +"."+extension
                salida = files.download(url)
            else:
                url= "/content/"+nombre + name_archi +"."+extension
                salida = url    
            return salida        
            
        #modified_apelblat   
        #vant_hoff           
        #vant_hoff_yaws       
        #modified_wilson      
        #buchowski_ksiazaczak 
        #NRTL                 
        #wilson               
        #weibull             

class models(model.modified_apelblat,model.vant_hoff,model.vant_hoff_yaws,model.modified_wilson,model.buchowski_ksiazaczak,model.NRTL,model.wilson,model.weibull):

    """class to print summary statistics of all models and summary plots 
    for the dataset according to Tf and ΔHf.
    # models summary 
    ----------------
    `statistics(dataset,Tf,ΔHf)`
    `plots(dataset,Tf,ΔHf)`
    """
    
    def __init__(self):
        
        self.statistics = self.statistics()
        self.plots      = self.plots()
 
    

    def statistics(self,Tf = " ",ΔHf= " ",method="lm",p0_ma =[1,1,1],p0_vh =[1,1],p0_vhy =[1,1,1],p0_mw =[1,1],p0_bk=[1,1],p0_nrtl =[1,1,1,1,1,1],p0_w =[1,1,1,1,1,1],p0_wtp=[1,1],maxfev=20000):

        names = ["MRD%", "MAPE","RMSD","AICc","R2","R2_a"]

        names_model =["statistics"]
        std =        [names]

        modelo_1 = model.modified_apelblat(self)
        std_1    = modelo_1.statistics(method = method, p0 = p0_ma, maxfev=20000)["values"].values
        names_model.append("Mod_Apelblat")
        std.append(std_1)

        modelo_2 = model.vant_hoff(self)
        std_2    = modelo_2.statistics(method = method, p0 = p0_vh, maxfev=20000)["values"].values
        names_model.append("Vant_Hoff")
        std.append(std_2)

        modelo_3 = model.vant_hoff_yaws(self)
        std_3    = modelo_3.statistics(method = method, p0 = p0_vhy, maxfev=20000)["values"].values
        names_model.append("Vant_Hoff_Y")
        std.append(std_3)

        modelo_4 = model.modified_wilson(self)
        std_4    = modelo_4.statistics(method = method, p0 = p0_mw, maxfev=20000)["values"].values
        names_model.append("Mod_Wilson")
        std.append(std_4)

        if Tf != " ": 
            modelo_5 = model.buchowski_ksiazaczak(self,Tf)
            std_5    = modelo_5.statistics(method = method, p0 = p0_bk, maxfev=20000)["values"].values
            names_model.append("Buchowski_K")
            std.append(std_5)

            if ΔHf != " ":
                modelo_6 =  model.NRTL(self,Tf,ΔHf)
                std_6    = modelo_6.statistics(method = method, p0 = p0_nrtl, maxfev=20000)["values"].values
                names_model.append("NRTL")
                std.append(std_6)

                modelo_7 = model.wilson(self,Tf,ΔHf)
                std_7   = modelo_7.statistics(method = method, p0 = p0_w, maxfev=20000)["values"].values
                names_model.append("Wilson")
                std.append(std_7)

                modelo_8 = model.weibull(self,Tf,ΔHf)
                std_8   = modelo_8.statistics(method = method, p0 = p0_wtp, maxfev=20000)["values"].values
                names_model.append("Weibull")
                std.append(std_8)

        dataframe = pd.DataFrame(dict(zip(names_model,std)))
        return dataframe

    def plots(self,Tf = " ",ΔHf= " ",method="lm",p0_ma =[1,1,1],p0_vh =[1,1],p0_vhy =[1,1,1],p0_mw =[1,1],p0_bk=[1,1],p0_nrtl =[1,1,1,1,1,1],p0_w =[1,1,1,1,1,1],p0_wtp=[1,1],maxfev=20000,cols=2, rows =2,height=1000, width=1300):
        
        names_model = []
        L_cal       = []
        L_exp       = []
        L_R2a       = []

        modelo_1 = model.modified_apelblat(self)
        cal_1    = modelo_1.values(method=method,p0=p0_ma , maxfev=maxfev)["x3_Cal"].values
        exp_1    = modelo_1.values(method=method,p0=p0_ma , maxfev=maxfev)["x3_Exp"].values
        R2a_1    = modelo_1.statistics(method = method, p0 = p0_ma, maxfev=20000)["values"][5]
        names_model.append("Modified Apelblat model")
        L_cal.append(cal_1) 
        L_exp.append(exp_1)
        L_R2a.append(R2a_1)

        modelo_2 = model.vant_hoff(self)
        cal_2    = modelo_2.values(method=method,p0=p0_vh , maxfev=maxfev)["x3_Cal"].values
        exp_2    = modelo_2.values(method=method,p0=p0_vh , maxfev=maxfev)["x3_Exp"].values
        R2a_2    = modelo_2.statistics(method = method, p0 = p0_vh, maxfev=20000)["values"][5]
        names_model.append("Vant Hoff model")
        L_cal.append(cal_2) 
        L_exp.append(exp_2)
        L_R2a.append(R2a_2)

        modelo_3 = model.vant_hoff_yaws(self)
        cal_3    = modelo_3.values(method=method,p0=p0_vhy , maxfev=maxfev)["x3_Cal"].values
        exp_3    = modelo_3.values(method=method,p0=p0_vhy , maxfev=maxfev)["x3_Exp"].values
        R2a_3    = modelo_3.statistics(method = method, p0 = p0_vhy, maxfev=20000)["values"][5]
        names_model.append("Vant Hoff Yaws model")
        L_cal.append(cal_3) 
        L_exp.append(exp_3)
        L_R2a.append(R2a_3)

        modelo_4 = model.modified_wilson(self)
        cal_4    = modelo_4.values(method=method,p0=p0_mw , maxfev=maxfev)["x3_Cal"].values
        exp_4    = modelo_4.values(method=method,p0=p0_mw , maxfev=maxfev)["x3_Exp"].values
        R2a_4    = modelo_4.statistics(method = method, p0 = p0_mw, maxfev=20000)["values"][5]
        names_model.append("Modified Wilson model")
        L_cal.append(cal_4) 
        L_exp.append(exp_4)
        L_R2a.append(R2a_4)

        if Tf != " ":
            modelo_5 = model.buchowski_ksiazaczak(self,Tf)
            cal_5    = modelo_5.values(method=method,p0=p0_bk , maxfev=maxfev, )["x3_Cal"].values
            exp_5    = modelo_5.values(method=method,p0=p0_bk , maxfev=maxfev, )["x3_Exp"].values
            R2a_5    = modelo_5.statistics(method = method, p0 = p0_bk, maxfev=20000)["values"][5]
            names_model.append("Buchowski ksiazaczak model")
            L_cal.append(cal_5) 
            L_exp.append(exp_5)
            L_R2a.append(R2a_5)

            if ΔHf != " ":
                modelo_6 = model.NRTL(self,Tf,ΔHf)
                cal_6    = modelo_6.values(method=method,p0=p0_nrtl ,maxfev=maxfev)["x3_Cal"].values
                exp_6    = modelo_6.values(method=method,p0=p0_nrtl ,maxfev=maxfev)["x3_Exp"].values
                R2a_6    = modelo_6.statistics(method = method, p0 = p0_nrtl, maxfev=20000)["values"][5]
                names_model.append("NRTL model")
                L_cal.append(cal_6) 
                L_exp.append(exp_6)
                L_R2a.append(R2a_6)
          
                modelo_7 = model.wilson(self,Tf,ΔHf)
                cal_7    = modelo_7.values(method=method,p0=p0_w, maxfev=maxfev)["x3_Cal"].values
                exp_7    = modelo_7.values(method=method,p0=p0_w, maxfev=maxfev)["x3_Exp"].values
                R2a_7    = modelo_7.statistics(method = method, p0 = p0_w, maxfev=20000)["values"][5]
                names_model.append("Wilson model")
                L_cal.append(cal_7) 
                L_exp.append(exp_7)
                L_R2a.append(R2a_7)

                modelo_8 = model.weibull(self,Tf,ΔHf)
                cal_8    = modelo_8.values(method=method,p0=p0_wtp, maxfev=maxfev)["x3_Cal"].values
                exp_8    = modelo_8.values(method=method,p0=p0_wtp, maxfev=maxfev)["x3_Exp"].values
                R2a_8    = modelo_8.statistics(method = method, p0 = p0_wtp, maxfev=20000)["values"][5]
                names_model.append("Weibull model")
                L_cal.append(cal_8) 
                L_exp.append(exp_8)
                L_R2a.append(R2a_8)
        
        L_r = []

        for i in range(1,rows+1):
            L_r += cols*[i]
            L_row =10*L_r
            L_col =10*list(range(1,cols+1))

            L_row =10*L_r
            L_col =10*list(range(1,cols+1))

        names = []
        for i in range(len(names_model)):
            names.append(names_model[i]+","+"  R2_a = "+ str(L_R2a[i].round(6)))


        fig = make_subplots(rows=rows, cols=cols,subplot_titles=names)
        
        for i in range(len(names_model)):
            fig.add_trace(go.Scatter(x=L_cal[i],y=L_exp[i],
                                         name = "",
                                         hovertemplate="x3_cal: %{x}<br>x3_exp: %{y}<br>",
                                         mode='markers',
                                         showlegend= False,
                                         marker=dict(size=6,line=dict(width=0.5,color='DarkSlateGrey'))),
                                         row=L_row[i], col=L_col[i])
            
        for i in range(len(names_model)):
            X = np.linspace(min(L_cal[i]),max(L_cal[i]),200)
            fig.add_trace(go.Scatter(x=X,y=X,showlegend= False,marker=dict(size=6,line=dict(width=0.5,color="#2a3f5f")),hoverinfo = "skip"),row=L_row[i], col=L_col[i])

        for i in range(len(names_model)):
            fig.update_xaxes(title = "$x3^{Cal}$")

        for i in range(len(names_model)):
            fig.update_yaxes(title = "$x3^{Exp}$")
            
        fig.update_layout(height=height, width=width,showlegend=False)
        return fig.show()