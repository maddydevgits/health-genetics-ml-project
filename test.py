
dataset=pd.read_csv('dataset.csv')
#print(dataset.head())

symptoms=[]

for i in (dataset.columns[:-1]):
	symptoms.append(i)

#print(symptoms)

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

'''dclassifier=DecisionTreeClassifier()
dclassifier.fit(X_train,Y_train)
y_pred=dclassifier.predict(X_test)
print(accuracy_score(Y_test,y_pred))'''

'''rclassifier=RandomForestClassifier(n_estimators=10)
rclassifier.fit(X_train,Y_train)
y_pred=rclassifier.predict(X_test)
print(accuracy_score(Y_test,y_pred))'''

kclassifier=KNeighborsClassifier(n_neighbors=3)
kclassifier.fit(X_train,Y_train)
y_pred=kclassifier.predict(X_test)
print(accuracy_score(y_pred,Y_test))