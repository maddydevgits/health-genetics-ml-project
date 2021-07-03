from flask import Flask, render_template, request
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from mode_prediction import predict_mode
from doctor_send import send_to_doctor

dataset=pd.read_csv('dataset.csv')
symptoms=[]

disease_labels=['Bronchial Asthma','Diabetes','Heart attack','HyperTension','Paralysis (brain hemorrhage)','Tuberculosis']

for i in (dataset.columns[:-1]):
	symptoms.append(i)

print(symptoms)

X=dataset.iloc[:,:-1].values
#print(X)

Y=dataset.iloc[:,-1].values
#print(Y)

Y=pd.get_dummies(Y)
#print(Y)

X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.25,random_state=0)

#print(X_train)
#print(X_test)
#print(Y_train)
#print(Y_test)

kclassifier=KNeighborsClassifier(n_neighbors=3)
kclassifier.fit(X_train,Y_train)
y_pred=kclassifier.predict(X_test)
print(accuracy_score(y_pred,Y_test))

p=''
id=0

conn = sqlite3.connect('maddy.db')
curs=conn.cursor()
try:
 curs.execute('''CREATE TABLE patients(ID int AUTO_INCREMENT, pname varchar(50) NOT NULL, aadno int(12) NOT NULL, cname varchar(10) NOT NULL, pno int(10) NOT NULL, gen varchar(7)  NOT NULL, age int(2) NOT NULL, weight float NOT NULL, previous_remarks varchar(200) NOT NULL, mode varchar(10) NOT NULL); ''')
 print('Table Created')
except:
 print('Table Already Created')

conn.close()

def updateRemarks(p_id,m,r):
	global id
	conn=sqlite3.connect('maddy.db')
	cursor = conn.execute("UPDATE patients set previous_remarks = ? where aadno = ?",(r,p_id));
	conn.commit()
	cursor = conn.execute("UPDATE patients set mode = ? where aadno = ?",(m,p_id));
	conn.commit()
	print('Updated Remarks')
	conn.close()

def readData(p_id):
	global id
	conn=sqlite3.connect('maddy.db')
	cursor = conn.execute("SELECT * from patients");
	for row in cursor:
		if(row[2]==id):
			return(row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
	return([])

def checkPrevious(aadno):
	global p
	conn=sqlite3.connect('maddy.db')
	cursor = conn.execute("SELECT * from patients");
	for row in cursor:
		if(row[2]==aadno):
			p=row[8]
			conn.close()
			return (p)
	return(p)

def checkRecord(aadno):
	conn = sqlite3.connect('maddy.db')
	cursor = conn.execute("SELECT * from patients");
	for row in cursor:
		if(row[2]==aadno):
			conn.close()
			return(1)
	conn.close()
	return(0)

def insertRecord(pname,aadno,cname,pno,gen,age,weight):
	print('function called')
	#sql="INSERT INTO customers (pname,aadno,cname,pno,gen,age,weight) VALUES (?,?,?,?,?,?,?)",(pname,aadno,cname,pno,gen,age,weight) 
	#print (sql)
	conn = sqlite3.connect('maddy.db')
	cursor = conn.execute("INSERT INTO patients (pname,aadno,cname,pno,gen,age,weight,previous_remarks,mode) VALUES (?,?,?,?,?,?,?,?,?)",(pname,aadno,cname,pno,gen,age,weight,"",""))
	conn.commit()
	print ('Registered into the Table')
	conn.close()

def loginRecord(pname,aadno):
	global id
	conn=sqlite3.connect('maddy.db')
	cursor=conn.execute("SELECT * from patients");
	for row in cursor:
		#print(row)
		if(row[1]==pname and row[2]==aadno):
			id=aadno
			print('Credentials Correct')
			conn.close()
			return(1)
	return(0)

app=Flask(__name__)

@app.route('/',methods=['POST','GET'])
def gets_connected():
	return(render_template('index.html'))

@app.route('/register')
def register_page():
	return(render_template('register.html'))

@app.route('/reports')
def generate_reports():
	conn = sqlite3.connect('maddy.db')
	cursor = conn.execute("SELECT * from patients")
	data=cursor.fetchall()
	conn.close()
	return(render_template('report.html',users=data))

@app.route('/regCustomer',methods=['POST','GET'])
def register_user():
	pname=str(request.form['pname'])
	aadno=int(request.form['aadno'])
	cname=str(request.form['cname'])
	pno=int(request.form['pno'])
	gen=str(request.form['gen'])
	age=int(request.form['age'])
	weight=float(request.form['weight'])
	#print(pname,aadno,cname,pno,gen,age,weight)
	if(checkRecord(aadno)==0):
		insertRecord(pname,aadno,cname,pno,gen,age,weight)
		dummy='Successfully Registered'
	else:
		dummy='Already Registered'
	return(render_template('register.html',rstatus=dummy))

@app.route('/login_user',methods=['POST','GET'])
def login_user():
	pname=str(request.form['pname'])
	aadno=int(request.form['aadno'])
	#print(pname,aadno)
	if(loginRecord(pname,aadno)):
		dummy='Successfully Logging In...'
	else:
		dummy='Check Credentials'
		return(render_template('index.html',lstatus=dummy))
	dummy=checkPrevious(aadno)
	if(dummy==''):
		dummy='No Previous Records'

	return(render_template('symp.html',remarks=dummy))

@app.route('/predict',methods=['POST','GET'])
def predict_data():
	s1=str(request.form['s1'])
	s2=str(request.form['s2'])
	s3=str(request.form['s3'])
	s4=str(request.form['s4'])
	print(s1,s2,s3,s4)
	k=[]
	for i in symptoms:
		k.append(0)

	for i in range(len(symptoms)):
		if symptoms[i]==s1 or symptoms[i]==s2 or symptoms[i]==s3 or symptoms[i]==s4:
			k[i]=1
		else:
			k[i]=0
	print(k)
	label=kclassifier.predict([k])
	disease_name=''
	for i in range(len(label[0])):
		if label[0][i]==1:
			disease_name=disease_labels[i]
	if (disease_name=='Diabetes'):
		medicines='Glimepride tab ,  Metformin tab ,  Gliclazide tab'
	elif(disease_name=='Bronchial Asthma'):
		medicines='Doxiffillin tab ,  Levosolbutomol Bromexyne syrup ,  Asebrofithillin tab ,  Theophylline tab ,  Buducorte inhaler ,  Foracorte Forte inhaler'
	elif(disease_name=='Heart attack'):
		medicines='Sorbitrate tab'
	elif(disease_name=='HyperTension'):
		medicines='Amlodipine tab ,  Ditiazem tab ,  Isravipine tab ,  Nicardipine tab ,  Verapimil tab'
	elif(disease_name=='Paralysis (brain hemorrhage)'):
		medicines='Anafranil tab ,  Clomipranime tab ,  methylphenidate tab'
	elif(disease_name=='Tuberculosis'):
		medicines='Ethambutol tab ,  Pyrazinamide tab ,  Cycloserine tab ,  Ethionamide tab ,  Levofloxacin tab ,  Kanamycan tab'
	updateRemarks(id, predict_mode(),'disease_name: '+disease_name+ ', medicine: '+medicines)
	m=readData(id)
	if(len(m)>1):
		pname=m[0]
		aadno=m[1]
		cname=m[2]
		pno=m[3]
		gen=m[4]
		age=m[5]
		weight=m[6]
		previous_remarks=m[7]
		mode=m[8]
		if(mode=='High'):
			send_to_doctor(cname)
	return(render_template('data.html',disease_prediction=disease_name,pname=pname,aadno=aadno,cname=cname,pno=pno,gen=gen,age=age,weight=weight,previous_remarks=previous_remarks,mode=mode))

@app.route('/login')
def login_page():
	return(render_template('index.html'))

if __name__=="__main__":
	app.run()